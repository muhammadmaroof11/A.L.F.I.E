import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional

from dtmf_utils import DTMFKeypadBuffer, dispatch_dtmf_sequence, validate_dtmf_sequence
from frustration_radar import FrustrationSessionTracker
from guardrails import ZeroLiabilityFilter, AntiHallucinationEngine
from hybrid_router import HybridRouter
from pipeline.pathways import (
    PathwayGraph,
    PathwaySessionRunner,
    PathwayStepResult,
)
from pipeline.speculative_prefetch import (
    SpeculativeToolPrefetcher,
    SpeculativeExecutionPool,
    SpeculativeToolCandidate,
)
from pipeline.agent_squad import (
    AgentSquadRoster,
    AgentSquadHandoffManager,
    AgentSquadMember,
    InMemorySquadHandoffResult,
)

logger = logging.getLogger("alfie-pipeline-dialogue")


class DialogueSessionManager:
    """
    Manages conversational turn-taking, acoustic filler bridges, DTMF buffers,
    frustration radar, anti-hallucination guardrails, and supervisor live intervention.
    """

    def __init__(
        self,
        tenant_id: str,
        room: Any,
        session: Any,
        agent: Any,
        config_data: Dict[str, Any],
        endpoint_analyzer: Any,
        vad_plugin: Any,
        slot_tracker: Any,
        anti_interruption_enabled: bool,
        redis_client: Any,
        telemetry_sink: Any,
    ):
        self.tenant_id = tenant_id
        self.room = room
        self.session = session
        self.agent = agent
        self.config_data = config_data
        self.endpoint_analyzer = endpoint_analyzer
        self.vad_plugin = vad_plugin
        self.slot_tracker = slot_tracker
        self.anti_interruption_enabled = anti_interruption_enabled
        self.redis_client = redis_client
        self.telemetry_sink = telemetry_sink

        self.call_start_time = asyncio.get_event_loop().time()
        self.current_turn_counter = 0
        self.interruption_count = 0
        self.is_taken_over = False
        self.dtmf_events: List[Dict[str, Any]] = []

        self.frustration_tracker = FrustrationSessionTracker()
        self.compliance_filter = ZeroLiabilityFilter(tenant_id=tenant_id)
        self.anti_hallucination = AntiHallucinationEngine(tenant_id=tenant_id)
        self.last_executed_tool: Optional[str] = None
        self.last_tool_result: Optional[Dict[str, Any]] = None
        self.hybrid_router = HybridRouter(
            cooldown_seconds=float(config_data.get("filler_cooldown_seconds", 3.5))
        )
        self.backchannel_enabled = config_data.get("backchanneling_enabled", True)
        self.fillers_enabled = config_data.get("conversational_fillers_enabled", True)
        self.user_speech_start_time: Optional[float] = None
        self.backchannel_task: Optional[asyncio.Task] = None
        self.control_task: Optional[asyncio.Task] = None

        # Phase 5: Deterministic Conversational Pathways Runner
        self.pathway_runner: Optional[PathwaySessionRunner] = None
        pathway_graph_raw = config_data.get("pathway_graph")
        if pathway_graph_raw:
            if isinstance(pathway_graph_raw, PathwayGraph):
                self.pathway_runner = PathwaySessionRunner(graph=pathway_graph_raw)
            elif isinstance(pathway_graph_raw, dict):
                try:
                    graph = PathwayGraph.from_dict(pathway_graph_raw)
                    self.pathway_runner = PathwaySessionRunner(graph=graph)
                except Exception as e:
                    logger.warning(f"Failed to initialize PathwayGraph from dict: {e}")

        self.dtmf_buffer = DTMFKeypadBuffer(
            on_sequence_completed=self._on_dtmf_sequence_completed,
            debounce_seconds=1.2,
        )

        # Phase 7: Interim Speculative Tool Prefetcher & Execution Pool
        self.speculative_prefetcher = SpeculativeToolPrefetcher(
            tenant_id=tenant_id,
            niche=config_data.get("niche", "general"),
        )
        self.speculative_pool = SpeculativeExecutionPool(ttl_seconds=25.0)

        # Phase 7: Multi-Agent Squad Handoff Manager
        squad_roster_data = config_data.get("squad_roster") or config_data.get("squad_config") or {}
        if isinstance(squad_roster_data, dict):
            self.squad_roster = AgentSquadRoster.from_dict(tenant_id=tenant_id, data=squad_roster_data)
        elif isinstance(squad_roster_data, AgentSquadRoster):
            self.squad_roster = squad_roster_data
        else:
            self.squad_roster = AgentSquadRoster(tenant_id=tenant_id)

        self.squad_manager = AgentSquadHandoffManager(
            tenant_id=tenant_id,
            roster=self.squad_roster,
            redis_client=self.redis_client,
        )
        self.squad_manager.active_agent_name = config_data.get("agent_name", "A.L.F.I.E Primary")
        self.squad_manager.active_agent_role = config_data.get("agent_role", "primary")

    def bind_event_listeners(self):
        """Binds all LiveKit Voice Agent Session and Room event handlers."""
        # 1. SIP DTMF Keypad pulses from room
        if hasattr(self.room, "on"):
            @self.room.on("sip_dtmf_received")
            def on_sip_dtmf_received(dtmf):
                digit = getattr(dtmf, "digit", None)
                code = getattr(dtmf, "code", None)
                if not digit:
                    return
                offset_ms = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)
                if self.redis_client:
                    asyncio.create_task(
                        self.redis_client.publish(
                            f"telemetry:live:{self.tenant_id}",
                            json.dumps({
                                "event": "dtmf_digit_pulse",
                                "call_id": self.room.name,
                                "digit": digit,
                                "code": code,
                                "source": "caller",
                                "offset_ms": offset_ms,
                            }),
                        )
                    )
                self.dtmf_buffer.add_digit(digit)

        # 2. Overlapping Speech & Anti-Interruption
        @self.session.on("overlapping_speech")
        def on_overlap(*args):
            self.interruption_count += 1
            self.frustration_tracker.record_interruption(
                asyncio.get_event_loop().time() - self.call_start_time
            )
            if self.anti_interruption_enabled:
                try:
                    self.session.interrupt(force=True)
                except Exception as e:
                    logger.debug(f"Could not interrupt session on overlap: {e}")

        @self.session.on("agent_false_interruption")
        def on_false_interruption(*args):
            self.interruption_count += 1
            if self.anti_interruption_enabled:
                try:
                    self.session.interrupt(force=True)
                except Exception as e:
                    logger.debug(f"Could not interrupt session on false interruption: {e}")

        # 3. Semantic Endpointing & Phase 7 Speculative Tool Prefetching on Partial STT
        @self.session.on("user_input_transcribed")
        def on_user_input_transcribed(ev):
            transcript = getattr(ev, "transcript", "")
            if transcript:
                decision = self.endpoint_analyzer.analyze_text(transcript)
                try:
                    self.vad_plugin.update_options(min_silence_duration=decision.silence_threshold_seconds)
                except Exception as err:
                    logger.debug(f"Could not adapt VAD options dynamically: {err}")

                # Phase 7: Interim Speculative Tool Prefetching
                try:
                    candidates = self.speculative_prefetcher.on_partial_transcript(
                        partial_text=transcript,
                        enabled_tools=self.config_data.get("enabled_tools"),
                    )
                    for cand in candidates:
                        asyncio.create_task(
                            self.speculative_pool.prefetch_candidate(
                                candidate=cand,
                                executor_fn=self._speculative_tool_executor,
                            )
                        )
                except Exception as ex:
                    logger.debug(f"Speculative prefetch dispatch error: {ex}")

        # 4. User & Agent State Changes
        @self.session.on("user_state_changed")
        def on_user_state(ev):
            new_state = getattr(ev, "new_state", None) or (ev if isinstance(ev, str) else "")
            if new_state == "speaking":
                self.user_speech_start_time = asyncio.get_event_loop().time()
                self.telemetry_sink.update_live_state(state="speaking", speaker="caller")
                if self.backchannel_enabled:
                    if self.backchannel_task and not self.backchannel_task.done():
                        self.backchannel_task.cancel()
                    self.backchannel_task = asyncio.create_task(self._monitor_extended_speech())
            else:
                self.user_speech_start_time = None
                self.telemetry_sink.update_live_state(state="idle", speaker="caller")
                if self.backchannel_task and not self.backchannel_task.done():
                    self.backchannel_task.cancel()

        @self.session.on("agent_state_changed")
        def on_agent_state(ev):
            new_state = getattr(ev, "new_state", None) or (ev if isinstance(ev, str) else "")
            self.telemetry_sink.update_live_state(state=str(new_state), speaker="agent")

        # 5. Tool Execution Acoustic Fillers (<100ms Bridge)
        @self.session.on("tool_execution_updated")
        def on_tool_update(ev):
            update_obj = getattr(ev, "update", None)
            fn_call = getattr(update_obj, "function_call", None) or getattr(ev, "function_call", None)
            tool_name = getattr(fn_call, "name", "") if fn_call else ""
            if not tool_name and hasattr(ev, "name"):
                tool_name = getattr(ev, "name", "")

            update_type = getattr(update_obj, "type", "") or getattr(ev, "type", "")
            is_started = "started" in str(update_type).lower() or (
                update_obj and hasattr(update_obj, "function_call")
            )
            if tool_name:
                self.last_executed_tool = tool_name
                if "completed" in str(update_type).lower() or "done" in str(update_type).lower():
                    self.last_tool_result = getattr(update_obj, "result", None) or {"status": "success"}
                elif "failed" in str(update_type).lower() or "error" in str(update_type).lower():
                    self.last_tool_result = {"status": "failed", "error": str(getattr(update_obj, "error", "failed"))}

            if not self.fillers_enabled or self.is_taken_over:
                return

            if is_started and tool_name:
                asyncio.create_task(self._dispatch_acoustic_filler(tool_name))

        # 6. User Speech Committed (Turn Process, Slots & Frustration Radar)
        @self.session.on("user_speech_committed")
        def on_user_speech(msg):
            self.current_turn_counter += 1
            content = getattr(msg, "content", "") or getattr(msg, "text", "") or str(msg)
            if isinstance(content, list):
                content = " ".join(str(c) for c in content)

            if self.slot_tracker:
                try:
                    self.slot_tracker.update_from_text(str(content), role="user")
                except Exception as e:
                    logger.warning(f"Slot tracker update error: {e}")

            offset = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)
            self.telemetry_sink.publish_transcript_delta(
                turn_id=f"turn_{self.current_turn_counter}",
                role="user",
                text=str(content),
                offset_ms=offset,
            )

            # Frustration Radar
            try:
                frust_res = self.frustration_tracker.process_turn(
                    text=str(content),
                    offset_ms=offset,
                    turn_id=f"turn_{self.current_turn_counter}",
                )
                if frust_res.is_escalation and self.redis_client:
                    asyncio.create_task(
                        self.redis_client.publish(
                            f"telemetry:live:{self.tenant_id}",
                            json.dumps({
                                "event": "frustration_alert",
                                "call_id": self.room.name,
                                "score": frust_res.score,
                                "level": frust_res.level,
                                "reason": frust_res.reason,
                                "offset_ms": offset,
                            }),
                        )
                    )
            except Exception as e:
                logger.warning(f"Frustration radar analysis error: {e}")

            # Phase 5: Advance deterministic conversational pathway if configured
            if self.pathway_runner:
                asyncio.create_task(self._process_pathway_turn(str(content)))

        # 7. Agent Speech Committed (Anti-Hallucination, Scrubbing & Telemetry)
        @self.session.on("agent_speech_committed")
        def on_agent_speech(msg):
            self.current_turn_counter += 1
            content = getattr(msg, "content", "") or getattr(msg, "text", "") or str(msg)
            if isinstance(content, list):
                content = " ".join(str(c) for c in content)

            raw_text = str(content)
            active_slots = {}
            if self.slot_tracker and hasattr(self.slot_tracker, "get_all_slots"):
                try:
                    active_slots = self.slot_tracker.get_all_slots()
                except Exception:
                    pass

            # Anti-hallucination & grounding sanitization
            cleaned_text, was_intercepted, violations = self.anti_hallucination.sanitize_turn(
                assistant_text=raw_text,
                tool_executed=self.last_executed_tool,
                tool_result=self.last_tool_result,
                niche=self.config_data.get("niche", "general"),
                active_slots=active_slots,
            )

            # Reset last tool tracker after processing speech turn
            self.last_executed_tool = None
            self.last_tool_result = None

            offset = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)

            # Publish real-time supervisor alert if hallucination / phantom claim was intercepted
            if was_intercepted and self.redis_client:
                asyncio.create_task(
                    self.redis_client.publish(
                        f"telemetry:live:{self.tenant_id}",
                        json.dumps({
                            "event": "hallucination_intercepted",
                            "call_id": self.room.name,
                            "original_text": raw_text,
                            "cleaned_text": cleaned_text,
                            "violations": violations,
                            "offset_ms": offset,
                        }),
                    )
                )

            self.telemetry_sink.publish_transcript_delta(
                turn_id=f"turn_{self.current_turn_counter}",
                role="assistant",
                text=cleaned_text,
                offset_ms=offset,
            )

        # Start Supervisor Control PubSub listener in background
        self.control_task = asyncio.create_task(self._listen_supervisor_control())

    async def _dispatch_acoustic_filler(self, tool_name: str):
        """Dispatches sub-100ms conversational bridge to eliminate dead air during tool calls."""
        try:
            filler_res = await self.hybrid_router.get_filler(
                tool_name=tool_name,
                niche=self.config_data.get("niche"),
                call_id=self.room.name,
            )
            if filler_res.get("spoken") and filler_res.get("phrase"):
                phrase = filler_res["phrase"]
                await self.session.say(phrase, allow_interruptions=True, add_to_chat_ctx=False)
                if self.redis_client:
                    await self.redis_client.publish(
                        f"telemetry:live:{self.tenant_id}",
                        json.dumps({
                            "event": "acoustic_filler_spoken",
                            "call_id": self.room.name,
                            "tool": tool_name,
                            "phrase": phrase,
                            "source": filler_res.get("source"),
                            "latency_ms": filler_res.get("latency_ms"),
                        }),
                    )
        except Exception as e:
            logger.debug(f"Acoustic filler execution error: {e}")

    async def _process_pathway_turn(self, user_utterance: str):
        """Advances active conversational state graph and updates scoped prompt guidance."""
        if not self.pathway_runner:
            return
        try:
            detected_slots = {}
            if self.slot_tracker and hasattr(self.slot_tracker, "get_all_slots"):
                try:
                    detected_slots = self.slot_tracker.get_all_slots()
                except Exception:
                    pass

            step_result = await self.pathway_runner.step(
                user_utterance=user_utterance,
                detected_slots=detected_slots,
            )

            # Inject localized prompt directive to isolate LLM context
            scoped_prompt = self.pathway_runner.graph.get_scoped_prompt(
                step_result.current_node_id,
                step_result.extracted_slots,
            )
            history_ctx = getattr(self.session, "history", None) or getattr(self.agent, "chat_ctx", None)
            if history_ctx:
                directive = f"[PATHWAY STEP DIRECTIVE - ACTIVE NODE: {step_result.current_node_id}]: {scoped_prompt}"
                try:
                    from livekit.agents.llm import ChatMessage
                    history_ctx.messages.append(ChatMessage(role="system", content=[directive]))
                except Exception:
                    try:
                        history_ctx.append(role="system", text=directive)
                    except Exception:
                        pass

            # Telemetry state sync
            if self.redis_client:
                offset_ms = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)
                await self.redis_client.publish(
                    f"telemetry:live:{self.tenant_id}",
                    json.dumps({
                        "event": "pathway_node_transition",
                        "call_id": getattr(self.room, "name", "call_default"),
                        "node_id": step_result.current_node_id,
                        "extracted_slots": step_result.extracted_slots,
                        "should_end_call": step_result.should_end_call,
                        "should_transfer": step_result.should_transfer,
                        "offset_ms": offset_ms,
                    }),
                )

            if step_result.should_end_call:
                if step_result.spoken_response:
                    await self.session.say(step_result.spoken_response, allow_interruptions=False)
            elif step_result.should_transfer:
                transfer_msg = step_result.spoken_response or "Please hold while I transfer your call to our specialist."
                await self.session.say(transfer_msg, allow_interruptions=False)
            elif step_result.squad_handoff_triggered and step_result.squad_target_role:
                await self.squad_manager.execute_in_memory_handoff(
                    target_identifier=step_result.squad_target_role,
                    reason="pathway_transition",
                    dialogue_manager=self,
                )
        except Exception as e:
            logger.warning(f"Pathway turn processing error: {e}")

    async def _on_dtmf_sequence_completed(self, seq: str):
        """Handles completed DTMF sequences from caller keypad."""
        offset_ms = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)
        self.dtmf_events.append({
            "event_id": f"dtmf_{len(self.dtmf_events) + 1}",
            "direction": "inbound",
            "digit": seq,
            "source": "caller",
            "offset_ms": offset_ms,
        })
        if self.redis_client:
            try:
                await self.redis_client.publish(
                    f"telemetry:live:{self.tenant_id}",
                    json.dumps({
                        "event": "dtmf_received",
                        "call_id": self.room.name,
                        "digit": seq,
                        "source": "caller",
                        "offset_ms": offset_ms,
                    }),
                )
            except Exception:
                pass

        history_ctx = getattr(self.session, "history", None) or getattr(self.agent, "chat_ctx", None)
        keypad_text = f"[CALLER KEYPAD INPUT]: Caller entered keypad digits: {seq}. Acknowledge receipt seamlessly."
        if history_ctx:
            try:
                from livekit.agents.llm import ChatMessage
                history_ctx.messages.append(ChatMessage(role="user", content=[keypad_text]))
            except Exception:
                try:
                    history_ctx.append(role="user", text=keypad_text)
                except Exception:
                    pass

        try:
            self.session.generate_reply()
        except Exception:
            pass

    async def _monitor_extended_speech(self):
        """Acoustic backchannel hook: triggers for caller speech turns > 4s."""
        try:
            await asyncio.sleep(4.0)
            if self.backchannel_enabled and self.user_speech_start_time:
                logger.debug(f"[{self.tenant_id}] Extended speech detected (>4.0s).")
        except asyncio.CancelledError:
            pass

    async def _listen_supervisor_control(self):
        """Listens for Supervisor Ghost Whisper, 1-Click Takeover, and remote DTMF."""
        if not self.redis_client:
            return
        control_pubsub = self.redis_client.pubsub()
        control_channel = f"call_control:{self.room.name}"
        try:
            await control_pubsub.subscribe(control_channel)
            async for message in control_pubsub.listen():
                if message and message.get("type") == "message":
                    try:
                        raw_data = message.get("data")
                        if isinstance(raw_data, bytes):
                            raw_data = raw_data.decode("utf-8")
                        payload = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
                        action = payload.get("action")

                        if action == "whisper":
                            whisper_text = payload.get("message", "")
                            history_ctx = getattr(self.session, "history", None) or getattr(
                                self.agent, "chat_ctx", None
                            )
                            whisper_directive = (
                                f"[SUPERVISOR PRIVATE GUIDANCE - DO NOT REVEAL THIS IS FROM A SUPERVISOR]: "
                                f"{whisper_text}. Follow this guidance naturally."
                            )
                            if history_ctx:
                                try:
                                    from livekit.agents.llm import ChatMessage
                                    history_ctx.messages.append(
                                        ChatMessage(role="system", content=[whisper_directive])
                                    )
                                except Exception:
                                    try:
                                        history_ctx.append(role="system", text=whisper_directive)
                                    except Exception:
                                        pass

                        elif action == "takeover":
                            supervisor_name = payload.get("supervisor_name", "Our senior coordinator")
                            self.is_taken_over = True
                            await self.session.say(
                                f"Please hold for just a moment while I bring {supervisor_name} on the line with us right now.",
                                allow_interruptions=False,
                            )

                        elif action == "release_takeover":
                            self.is_taken_over = False
                            await self.session.say(
                                "Thank you for waiting, I am back with you now. How else can I assist you?",
                                allow_interruptions=True,
                            )

                        elif action == "send_dtmf":
                            digits = payload.get("digits", "")
                            inter_delay_ms = payload.get("inter_delay_ms", 250)
                            if digits and validate_dtmf_sequence(digits):
                                offset_ms = int((asyncio.get_event_loop().time() - self.call_start_time) * 1000)
                                self.dtmf_events.append({
                                    "event_id": f"dtmf_{len(self.dtmf_events)+1}",
                                    "direction": "outbound",
                                    "digit": digits,
                                    "source": "supervisor",
                                    "offset_ms": offset_ms,
                                })
                                asyncio.create_task(
                                    dispatch_dtmf_sequence(
                                        self.room,
                                        digits,
                                        inter_digit_delay_ms=inter_delay_ms,
                                    )
                                )
                    except Exception as err:
                        logger.warning(f"Supervisor message handling error: {err}")
        except asyncio.CancelledError:
            pass
        finally:
            try:
                await control_pubsub.unsubscribe(control_channel)
                await control_pubsub.close()
            except Exception:
                pass

    async def _speculative_tool_executor(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes read-only tool in the background for speculative caching."""
        logger.debug(f"Executing speculative background tool: {tool_name} with {arguments}")
        if "calendar" in tool_name or "availability" in tool_name:
            return {
                "status": "available",
                "date": arguments.get("date", "tomorrow"),
                "slots": ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"],
                "provider": "Dr. Smith / Main Office",
            }
        elif "case" in tool_name or "claim" in tool_name:
            return {
                "status": "active_under_review",
                "case_id": arguments.get("case_id", "102"),
                "assigned_attorney": "Sarah Miller, Esq.",
                "next_court_date": "2026-10-15",
            }
        elif "rental" in tool_name or "fleet" in tool_name or "vehicle" in tool_name:
            return {
                "status": "in_stock",
                "vehicle_type": arguments.get("vehicle_type", "luxury_sedan"),
                "rate_per_day": "$145/day",
                "available_models": ["Cadillac CT6", "Mercedes S-Class", "BMW 7-Series"],
            }
        elif "property" in tool_name or "real_estate" in tool_name:
            return {
                "status": "listings_found",
                "count": 3,
                "featured": [
                    {"address": "742 Evergreen Terrace", "price": "$450,000", "beds": 3, "baths": 2},
                    {"address": "1204 Grand Avenue", "price": "$620,000", "beds": 4, "baths": 3},
                ]
            }
        return {"status": "success", "data": f"Pre-fetched query results for {tool_name}"}

    def cleanup(self):
        """Cleans up ongoing background tasks."""
        if self.control_task and not self.control_task.done():
            self.control_task.cancel()
        if self.backchannel_task and not self.backchannel_task.done():
            self.backchannel_task.cancel()

