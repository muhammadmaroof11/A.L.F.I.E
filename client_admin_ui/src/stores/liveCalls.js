import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '../services/api';

export const useLiveCallsStore = defineStore('liveCalls', () => {
  const activeCalls = ref([]);
  const selectedCallId = ref(null);
  const wsConnected = ref(false);
  const isSimulating = ref(false);
  let ws = null;
  let reconnectTimer = null;
  let heartbeatInterval = null;

  const selectedCall = computed(() => {
    return activeCalls.value.find((c) => c.call_id === selectedCallId.value) || activeCalls.value[0] || null;
  });

  const activeCallCount = computed(() => activeCalls.value.length);

  function connectWebSocket(token) {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/client/live-calls/ws?token=${token || ''}`;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        wsConnected.value = true;
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
        heartbeatInterval = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingEvent(data);
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        wsConnected.value = false;
        clearInterval(heartbeatInterval);
        scheduleReconnect(token);
      };

      ws.onerror = () => {
        wsConnected.value = false;
      };
    } catch (err) {
      console.warn('WebSocket connection error:', err);
      scheduleReconnect(token);
    }
  }

  function scheduleReconnect(token) {
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        connectWebSocket(token);
      }, 4000);
    }
  }

  function disconnectWebSocket() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    if (ws) {
      ws.close();
      ws = null;
    }
    wsConnected.value = false;
  }

  function handleIncomingEvent(data) {
    const eventType = data.event || data.type;
    const callId = data.call_id || data.room_name;

    if (!callId) {
      if (data.active_calls && Array.isArray(data.active_calls)) {
        activeCalls.value = data.active_calls;
        if (!selectedCallId.value && activeCalls.value.length > 0) {
          selectedCallId.value = activeCalls.value[0].call_id;
        }
      }
      return;
    }

    let call = activeCalls.value.find((c) => c.call_id === callId);

    if (eventType === 'call_started' || eventType === 'call_connected') {
      if (!call) {
        call = {
          call_id: callId,
          caller_phone: data.caller_phone || data.phone || 'Incoming Caller',
          started_at: data.timestamp || Date.now(),
          state: 'active',
          speaker_state: 'idle',
          agent_name: data.agent_name || 'A.L.F.I.E Voice Agent',
          niche: data.niche || 'general',
          transcripts: [],
          dtmf_events: [],
          frustration_score: 0.0,
          current_node: data.initial_node || 'Greeting',
        };
        activeCalls.value.unshift(call);
      }
      if (!selectedCallId.value) {
        selectedCallId.value = callId;
      }
    } else if (call) {
      if (eventType === 'transcript_delta') {
        if (!call.transcripts) call.transcripts = [];
        call.transcripts.push({
          turn_id: data.turn_id || `turn_${call.transcripts.length + 1}`,
          role: data.role || 'user',
          text: data.text || '',
          offset_ms: data.offset_ms || 0,
          timestamp: Date.now(),
        });
      } else if (eventType === 'user_state_changed') {
        call.speaker_state = data.state === 'speaking' ? 'caller_speaking' : 'idle';
      } else if (eventType === 'agent_state_changed') {
        call.speaker_state = data.state === 'speaking' ? 'agent_speaking' : 'idle';
      } else if (eventType === 'dtmf_digit_pulse') {
        if (!call.dtmf_events) call.dtmf_events = [];
        call.dtmf_events.push({
          digit: data.digit,
          offset_ms: data.offset_ms,
          source: data.source || 'caller',
          timestamp: Date.now(),
        });
      } else if (eventType === 'frustration_alert') {
        call.frustration_score = data.score || 0.8;
        call.frustration_level = data.level || 'elevated';
      } else if (eventType === 'pathway_node_transition') {
        call.current_node = data.node_id || call.current_node;
        if (data.extracted_slots) {
          call.slots = { ...(call.slots || {}), ...data.extracted_slots };
        }
      } else if (eventType === 'agent_squad_handoff') {
        call.agent_name = data.target_agent;
        call.agent_role = data.target_role;
        call.last_handoff = {
          from: data.previous_agent,
          to: data.target_agent,
          reason: data.reason,
          duration_ms: data.handoff_duration_ms,
        };
      } else if (eventType === 'supervisor_takeover') {
        call.state = 'supervisor_takeover';
      } else if (eventType === 'release_takeover') {
        call.state = 'active';
      } else if (eventType === 'call_ended' || eventType === 'call_disconnected') {
        activeCalls.value = activeCalls.value.filter((c) => c.call_id !== callId);
        if (selectedCallId.value === callId) {
          selectedCallId.value = activeCalls.value.length > 0 ? activeCalls.value[0].call_id : null;
        }
      }
    }
  }

  async function simulateDemoCall() {
    isSimulating.value = true;
    try {
      const resp = await api.post('/api/client/live-calls/simulate-inbound');
      if (resp.data && resp.data.call_id) {
        handleIncomingEvent({
          event: 'call_started',
          call_id: resp.data.call_id,
          caller_phone: resp.data.caller_phone || '+1 (555) 382-9910',
          agent_name: 'Sarah (Triage)',
          niche: 'general',
          timestamp: Date.now(),
        });
      }
    } catch (e) {
      // Local fallback simulation if endpoint in sandbox
      const mockCallId = `demo_call_${Date.now()}`;
      handleIncomingEvent({
        event: 'call_started',
        call_id: mockCallId,
        caller_phone: '+1 (415) 882-1049',
        agent_name: 'Receptionist AI',
        niche: 'general',
        timestamp: Date.now(),
      });
    } finally {
      isSimulating.value = false;
    }
  }

  return {
    activeCalls,
    selectedCallId,
    selectedCall,
    activeCallCount,
    wsConnected,
    isSimulating,
    connectWebSocket,
    disconnectWebSocket,
    simulateDemoCall,
    handleIncomingEvent,
  };
});
