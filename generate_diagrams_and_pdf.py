"""
A.L.F.I.E - Enterprise Architecture, ERD & Call Flow Visual Generator
Generates high-resolution PNG images and an Executive PDF Presentation Deck.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle, ConnectionPatch
import numpy as np

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation_assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common Palette & Theme
BG_COLOR = "#0B0F19"
CARD_BG = "#111827"
CARD_BORDER = "#1F2937"
ACCENT_BLUE = "#38BDF8"
ACCENT_CYAN = "#06B6D4"
ACCENT_PURPLE = "#818CF8"
ACCENT_GREEN = "#10B981"
ACCENT_AMBER = "#F59E0B"
ACCENT_ROSE = "#F43F5E"
TEXT_WHITE = "#F9FAFB"
TEXT_MUTED = "#9CA3AF"
TEXT_DIM = "#6B7280"

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def draw_card(ax, x, y, w, h, title, items, badge="", badge_color=ACCENT_BLUE, border_color="#374151", bg_color=CARD_BG, title_color=TEXT_WHITE):
    """Draw a styled tech stack / entity card."""
    box = FancyBboxPatch((x, y - h), w, h,
                         boxstyle="round,pad=0.015,rounding_size=0.02",
                         ec=border_color, fc=bg_color, lw=1.5, zorder=2)
    ax.add_patch(box)
    
    # Title bar background
    title_h = 0.045
    t_box = FancyBboxPatch((x, y - title_h), w, title_h,
                           boxstyle="round,pad=0.01,rounding_size=0.02",
                           ec=border_color, fc="#1E293B", lw=1.2, zorder=3)
    ax.add_patch(t_box)
    
    # Title text
    ax.text(x + 0.02, y - 0.025, title, color=title_color, fontsize=9.5, fontweight='bold', va='center', zorder=4)
    
    # Badge if any
    if badge:
        ax.text(x + w - 0.02, y - 0.025, badge, color=badge_color, fontsize=7.5, fontweight='bold', ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.2", fc="#0F172A", ec=badge_color, lw=1), zorder=4)
        
    # Content items
    line_y = y - title_h - 0.025
    for item in items:
        if isinstance(item, tuple):
            k, v = item
            ax.text(x + 0.02, line_y, k, color=TEXT_WHITE, fontsize=8, fontweight='semibold', va='center', zorder=4)
            ax.text(x + w - 0.02, line_y, v, color=TEXT_MUTED, fontsize=7.5, ha='right', va='center', zorder=4)
        else:
            ax.text(x + 0.02, line_y, f"• {item}", color=TEXT_MUTED, fontsize=7.5, va='center', zorder=4)
        line_y -= 0.026


def generate_erd_diagram():
    """Generates the comprehensive Database & In-Memory Entity Relationship Diagram."""
    fig, ax = plt.subplots(figsize=(20, 11.5), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Header
    ax.text(0.04, 0.96, "A.L.F.I.E — DATABASE & DATA PLATFORM E.R.D", color=TEXT_WHITE, fontsize=16, fontweight='bold', va='top')
    ax.text(0.04, 0.925, "Relational Schema (PostgreSQL) + In-Memory State & Vector Caches (Redis Stack)", color=ACCENT_CYAN, fontsize=10, va='top')

    # Status / SLA Badge
    ax.text(0.96, 0.95, "PRODUCTION SCHEMA v2.4 • MULTI-TENANT ISOLATION", color=ACCENT_GREEN, fontsize=9, fontweight='bold', ha='right',
            bbox=dict(boxstyle="round,pad=0.4", fc="#064E3B", ec=ACCENT_GREEN, lw=1.2))

    # COLUMN 1: Core Tenancy & Routing (x: 0.04, w: 0.28)
    draw_card(ax, 0.04, 0.88, 0.28, 0.26, "alfie_tenants", [
        ("tenant_id (PK)", "UUID"),
        ("name", "VARCHAR(255)"),
        ("niche", "VARCHAR(50)"),
        ("status", "VARCHAR(50)"),
        ("credit_limit_usd", "DECIMAL(10,2)"),
        ("subscription_tier", "VARCHAR(50)"),
        ("tenant_config", "JSONB"),
        ("created_at", "TIMESTAMP")
    ], badge="TENANCY ROOT", badge_color=ACCENT_CYAN, border_color=ACCENT_CYAN)

    draw_card(ax, 0.04, 0.58, 0.28, 0.19, "alfie_phone_numbers", [
        ("id (PK)", "SERIAL"),
        ("phone_number (UK)", "VARCHAR(50)"),
        ("tenant_id (FK)", "VARCHAR(255)"),
        ("niche", "VARCHAR(50)"),
        ("provider", "LiveKit SIP / Tel"),
        ("created_at", "TIMESTAMP")
    ], badge="TELEPHONY ROUTING", badge_color=ACCENT_BLUE)

    draw_card(ax, 0.04, 0.35, 0.28, 0.22, "alfie_niches & personas", [
        ("niche_key (UK)", "VARCHAR(100)"),
        ("display_name", "VARCHAR(255)"),
        ("system_prompt_template", "TEXT"),
        ("default_voice_id", "VARCHAR(255)"),
        ("default_tools_json", "JSONB"),
        ("example_conversation", "TEXT")
    ], badge="AGENT PERSONAS", badge_color=ACCENT_PURPLE)

    # COLUMN 2: Telemetry, Logs & Live Sessions (x: 0.36, w: 0.30)
    draw_card(ax, 0.36, 0.88, 0.30, 0.32, "alfie_call_recordings", [
        ("call_id (PK)", "VARCHAR(255)"),
        ("tenant_id (FK)", "VARCHAR(255)"),
        ("caller_number", "VARCHAR(50)"),
        ("duration_seconds", "INTEGER"),
        ("transcript", "JSONB"),
        ("sentiment", "VARCHAR(50)"),
        ("stt_ms / llm_ttft_ms", "INTEGER"),
        ("tts_ms / total_ms", "INTEGER"),
        ("total_tokens / cost_usd", "INT / DECIMAL"),
        ("recording_url", "TEXT")
    ], badge="CALL TELEMETRY", badge_color=ACCENT_GREEN, border_color=ACCENT_GREEN)

    draw_card(ax, 0.36, 0.52, 0.30, 0.20, "alfie_telemetry & usage", [
        ("id (PK)", "SERIAL"),
        ("tenant_id (FK)", "VARCHAR(255)"),
        ("call_id", "VARCHAR(255)"),
        ("event_type", "VARCHAR(255)"),
        ("data", "JSONB (Latency/VAD)"),
        ("credits_consumed", "DECIMAL(10,4)")
    ], badge="GRANULAR STREAM", badge_color=ACCENT_AMBER)

    draw_card(ax, 0.36, 0.28, 0.30, 0.21, "alfie_custom_tools", [
        ("id (PK)", "SERIAL"),
        ("tool_name (UK)", "VARCHAR(100)"),
        ("webhook_url", "TEXT"),
        ("http_method", "VARCHAR(10)"),
        ("parameters_json", "JSONB"),
        ("description", "TEXT")
    ], badge="DYNAMIC DISPATCH", badge_color=ACCENT_PURPLE)

    # COLUMN 3: Business CRM, Callbacks & In-Memory Redis Stack (x: 0.70, w: 0.26)
    draw_card(ax, 0.70, 0.88, 0.26, 0.23, "alfie_leads", [
        ("id (PK)", "SERIAL"),
        ("tenant_id (FK)", "VARCHAR(255)"),
        ("name", "VARCHAR(255)"),
        ("phone", "VARCHAR(50)"),
        ("email", "VARCHAR(255)"),
        ("status", "new | qual | conv"),
        ("notes", "TEXT")
    ], badge="LEAD CAPTURE", badge_color=ACCENT_GREEN)

    draw_card(ax, 0.70, 0.61, 0.26, 0.25, "alfie_callbacks", [
        ("id (PK)", "SERIAL"),
        ("tenant_id (FK)", "VARCHAR(255)"),
        ("call_id (FK)", "VARCHAR(255)"),
        ("caller_name / phone", "VARCHAR"),
        ("target_agent_id", "VARCHAR(255)"),
        ("target_department", "VARCHAR(100)"),
        ("priority / status", "high | sched"),
        ("notification_sent", "BOOLEAN")
    ], badge="HOT TRANSFER FALLBACK", badge_color=ACCENT_ROSE, border_color=ACCENT_ROSE)

    draw_card(ax, 0.70, 0.32, 0.26, 0.25, "REDIS STACK MEMORY", [
        ("caller_memory:{phone}", "90-Day Context"),
        ("semantic_cache:query", "Vector Search"),
        ("call_dedup:filter", "Bloom 30s Guard"),
        ("transfer_buffer:{id}", "Live Hot Handoff"),
        ("telemetry_stream", "Durable Ingest"),
        ("metrics:latency", "TimeSeries (100ms)")
    ], badge="ULTRA-FAST CACHE", badge_color=ACCENT_CYAN, border_color=ACCENT_CYAN, bg_color="#0F172A")

    # Connectors / Relationships with arrows
    arrow_props = dict(arrowstyle="-|>", color="#4B5563", lw=1.5, mutation_scale=12)
    accent_arrow = dict(arrowstyle="-|>", color=ACCENT_CYAN, lw=1.5, mutation_scale=12)
    rose_arrow = dict(arrowstyle="-|>", color=ACCENT_ROSE, lw=1.5, mutation_scale=12)
    green_arrow = dict(arrowstyle="-|>", color=ACCENT_GREEN, lw=1.5, mutation_scale=12)

    # Tenant -> Phone Numbers
    ax.annotate("", xy=(0.18, 0.58), xytext=(0.18, 0.62), arrowprops=arrow_props)
    # Tenant -> Call Recordings
    ax.annotate("", xy=(0.36, 0.75), xytext=(0.32, 0.75), arrowprops=accent_arrow)
    # Call Recordings -> Telemetry
    ax.annotate("", xy=(0.51, 0.52), xytext=(0.51, 0.56), arrowprops=arrow_props)
    # Call Recordings -> Callbacks
    ax.annotate("", xy=(0.70, 0.73), xytext=(0.66, 0.73), arrowprops=rose_arrow)
    # Tenant -> Leads
    ax.annotate("", xy=(0.70, 0.82), xytext=(0.66, 0.82), arrowprops=green_arrow)

    # Footer note
    ax.text(0.5, 0.03, "A.L.F.I.E Voice Architecture • Multi-Tenant PostgreSQL RDBMS + Redis Stack State Engine",
            color=TEXT_MUTED, fontsize=9, ha='center')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "alfie_erd_diagram.png")
    plt.savefig(output_path, dpi=300, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}")


def generate_call_flow_diagram():
    """Generates the End-to-End Call & Agent Flow lifecycle visual diagram."""
    fig, ax = plt.subplots(figsize=(20, 11.5), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Header
    ax.text(0.04, 0.96, "A.L.F.I.E — END-TO-END CALL & AGENT ARCHITECTURE FLOW", color=TEXT_WHITE, fontsize=16, fontweight='bold', va='top')
    ax.text(0.04, 0.925, "Telephony Ingress -> Low-Latency AI Reasoning Core -> Redis Caching -> Real-Time Persistence", color=ACCENT_CYAN, fontsize=10, va='top')

    ax.text(0.96, 0.95, "SUB-SECOND SPEECH-TO-SPEECH SLA (<800ms TOTAL)", color=ACCENT_GREEN, fontsize=9, fontweight='bold', ha='right',
            bbox=dict(boxstyle="round,pad=0.4", fc="#064E3B", ec=ACCENT_GREEN, lw=1.2))

    # STAGE 1: Ingress (x: 0.04, w: 0.17)
    draw_card(ax, 0.04, 0.87, 0.17, 0.65, "1. INGRESS & SIP GATEWAY", [
        ("PSTN / Mobile Call", "Carrier Trunk"),
        ("LiveKit SIP Trunk", "Inbound Rule"),
        ("Twilio Gateway", "DID Forwarding"),
        ("WebRTC Demo Arena", "Browser Client"),
        ("Room Allocator", "room_name: call_id"),
        ("RedisBloom Dedup", "Spam / Loop Guard"),
        ("Tenant DID Lookup", "alfie_phone_numbers"),
        ("Latency SLA", "10 - 25 ms")
    ], badge="STEP 01", badge_color=ACCENT_BLUE)

    # STAGE 2: Speech-to-Text & VAD (x: 0.23, w: 0.17)
    draw_card(ax, 0.23, 0.87, 0.17, 0.65, "2. STREAMING STT & VAD", [
        ("Silero VAD", "Speech Activity"),
        ("Deepgram Nova-3", "Multi-lingual STT"),
        ("AssemblyAI / Whisper", "Fallback STT"),
        ("Stream Frame Chunker", "20ms Audio Packets"),
        ("Interruption Handler", "Instant Mute (<30ms)"),
        ("Language Detection", "EN / UR / AR"),
        ("Target Latency", "160 - 190 ms")
    ], badge="STEP 02", badge_color=ACCENT_CYAN)

    # STAGE 3: Agent Core & Caching (x: 0.42, w: 0.20)
    draw_card(ax, 0.42, 0.87, 0.20, 0.65, "3. AGENT REASONING CORE", [
        ("CachedOpenAILLM", "Streaming Pipeline"),
        ("Redis Semantic Cache", "Vector LLM Match"),
        ("Redis Caller Memory", "90-Day History / Name"),
        ("Vertical FAQ Store", "Pre-warmed Niches"),
        ("Gemini 2.5 / GPT-4o", "Primary Reasoning"),
        ("Groq Llama-3.3 70B", "Ultra-Fast Alternative"),
        ("LLMLingua Cache", "Prompt Optimization"),
        ("Target TTFT", "280 - 420 ms")
    ], badge="STEP 03", badge_color=ACCENT_PURPLE, border_color=ACCENT_PURPLE)

    # STAGE 4: Tool Execution & Synthesis (x: 0.64, w: 0.17)
    draw_card(ax, 0.64, 0.87, 0.17, 0.65, "4. TOOLS & AUDIO SYNTHESIS", [
        ("save_lead_info()", "CRM Lead Capture"),
        ("check_availability()", "Live Booking"),
        ("transfer_to_dept()", "Live SIP Refer"),
        ("schedule_callback()", "Line-Busy Fallback"),
        ("Cartesia Sonic TTS", "Low-Latency Voice"),
        ("ElevenLabs Turbo v2", "Expressive Multilingual"),
        ("Target TTFA", "180 - 210 ms")
    ], badge="STEP 04", badge_color=ACCENT_AMBER)

    # STAGE 5: Telemetry & Monitoring (x: 0.83, w: 0.14)
    draw_card(ax, 0.83, 0.87, 0.14, 0.65, "5. TELEMETRY & PERSISTENCE", [
        ("Redis Stream", "telemetry_stream"),
        ("Async Ingest Worker", "worker.py"),
        ("PostgreSQL RDBMS", "Long-Term Logs"),
        ("WebSockets", "Live Broadcast"),
        ("Super Admin UI", "Global Telemetry"),
        ("Client Admin UI", "Tenant Portal"),
        ("Webhook Alerts", "Slack / CRM Sync")
    ], badge="STEP 05", badge_color=ACCENT_GREEN)

    # Bottom Pipeline Latency Summary Bar
    bar_box = FancyBboxPatch((0.04, 0.08), 0.92, 0.10,
                             boxstyle="round,pad=0.015,rounding_size=0.02",
                             ec=ACCENT_CYAN, fc="#0F172A", lw=1.5, zorder=2)
    ax.add_patch(bar_box)

    ax.text(0.06, 0.155, "TOTAL VOICE TURN LATENCY BREAKDOWN (BENCHMARK: 680ms - 810ms)", color=TEXT_WHITE, fontsize=10, fontweight='bold')
    
    # Latency breakdown segments
    segs = [
        ("VAD Detection", "35ms", ACCENT_BLUE, 0.06, 0.15),
        ("STT Stream (Deepgram)", "180ms", ACCENT_CYAN, 0.23, 0.22),
        ("LLM TTFT (Cached / Streaming)", "320ms", ACCENT_PURPLE, 0.47, 0.24),
        ("TTS First Audio (Cartesia)", "190ms", ACCENT_AMBER, 0.73, 0.21)
    ]
    
    for title, val, col, sx, sw in segs:
        s_box = FancyBboxPatch((sx, 0.095), sw, 0.045,
                               boxstyle="round,pad=0.01,rounding_size=0.01",
                               ec=col, fc="#1E293B", lw=1.2, zorder=3)
        ax.add_patch(s_box)
        ax.text(sx + 0.015, 0.117, title, color=TEXT_WHITE, fontsize=7.5, fontweight='bold', va='center', zorder=4)
        ax.text(sx + sw - 0.015, 0.117, val, color=col, fontsize=8, fontweight='bold', ha='right', va='center', zorder=4)

    # Horizontal Transition Arrows between stages
    arrow_props = dict(arrowstyle="-|>", color=ACCENT_CYAN, lw=2.0, mutation_scale=16)
    ax.annotate("", xy=(0.22, 0.55), xytext=(0.21, 0.55), arrowprops=arrow_props)
    ax.annotate("", xy=(0.41, 0.55), xytext=(0.40, 0.55), arrowprops=arrow_props)
    ax.annotate("", xy=(0.63, 0.55), xytext=(0.62, 0.55), arrowprops=arrow_props)
    ax.annotate("", xy=(0.82, 0.55), xytext=(0.81, 0.55), arrowprops=arrow_props)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "alfie_call_flow_diagram.png")
    plt.savefig(output_path, dpi=300, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}")


def generate_high_level_flow_diagram():
    """Generates an executive, simplified high-level flow diagram with abstracted technical details."""
    fig, ax = plt.subplots(figsize=(19, 10), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Header
    ax.text(0.05, 0.94, "A.L.F.I.E — HIGH-LEVEL CALL & AGENT FLOW", color=TEXT_WHITE, fontsize=18, fontweight='bold', va='top')
    ax.text(0.05, 0.895, "Executive Overview: How A.L.F.I.E Handles Customer Inquiries from Start to Finish", color=ACCENT_CYAN, fontsize=11, va='top')

    ax.text(0.95, 0.93, "SUB-SECOND NATURAL CONVERSATION", color=ACCENT_GREEN, fontsize=10, fontweight='bold', ha='right',
            bbox=dict(boxstyle="round,pad=0.5", fc="#064E3B", ec=ACCENT_GREEN, lw=1.5))

    # Helper for big high-level cards
    def draw_hl_card(x, y, w, h, step_num, title, icon, bullets, accent_col):
        # Card body
        box = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.015,rounding_size=0.03",
                             ec=accent_col, fc=CARD_BG, lw=1.8, zorder=2)
        ax.add_patch(box)
        
        # Header strip
        hb = FancyBboxPatch((x, y - 0.08), w, 0.08, boxstyle="round,pad=0.01,rounding_size=0.02",
                            ec=accent_col, fc="#1E293B", lw=1.2, zorder=3)
        ax.add_patch(hb)
        
        # Step badge
        ax.text(x + 0.02, y - 0.04, f"{step_num}", color="#0B0F19", fontsize=10, fontweight='bold', va='center',
                bbox=dict(boxstyle="circle,pad=0.3", fc=accent_col, ec=accent_col, lw=1), zorder=4)
        
        # Title with icon
        ax.text(x + 0.055, y - 0.04, f"{icon}  {title}", color=TEXT_WHITE, fontsize=12, fontweight='bold', va='center', zorder=4)
        
        # Bullets
        by = y - 0.12
        for b in bullets:
            ax.text(x + 0.02, by, f"• {b}", color=TEXT_MUTED, fontsize=9, va='center', zorder=4)
            by -= 0.038

    # 4 Main Conversational Stages in top row (y = 0.82, h = 0.32)
    card_w = 0.20
    card_h = 0.32
    
    draw_hl_card(0.05, 0.82, card_w, card_h, "1", "CALLER INGRESS", "[CALL]", [
        "Customer dials business line",
        "Or starts live website demo",
        "Instant connection (<50ms)",
        "Zero hold time or IVR maze"
    ], ACCENT_BLUE)

    draw_hl_card(0.28, 0.82, card_w, card_h, "2", "LISTEN & TRANSCRIBE", "[VOICE]", [
        "Real-time voice recognition",
        "Multilingual (EN / Urdu / Arabic)",
        "Instant barge-in detection",
        "Understands accents & noise"
    ], ACCENT_CYAN)

    draw_hl_card(0.51, 0.82, card_w, card_h, "3", "THINK & DECIDE", "[BRAIN]", [
        "Identifies customer intent",
        "Recalls 90-day caller history",
        "Consults business knowledge base",
        "Decides best action or answer"
    ], ACCENT_PURPLE)

    draw_hl_card(0.74, 0.82, card_w, card_h, "4", "SPEAK NATURALLY", "[AUDIO]", [
        "Human-like voice & cadence",
        "Sub-second response time",
        "Natural tone & pacing",
        "Smooth conversational flow"
    ], ACCENT_AMBER)

    # Conversational Loop Back Indicator
    loop_box = FancyBboxPatch((0.28, 0.44), 0.66, 0.05, boxstyle="round,pad=0.01,rounding_size=0.015",
                              ec=ACCENT_CYAN, fc="#0F172A", lw=1.2, zorder=2)
    ax.add_patch(loop_box)
    ax.text(0.61, 0.465, "LIVE CONVERSATION CYCLE (Repeats naturally until inquiry is resolved)", 
            color=ACCENT_CYAN, fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=3)

    # Horizontal Flow Arrows (Row 1)
    flow_arr = dict(arrowstyle="-|>", color=ACCENT_CYAN, lw=2.5, mutation_scale=18)
    ax.annotate("", xy=(0.27, 0.66), xytext=(0.26, 0.66), arrowprops=flow_arr)
    ax.annotate("", xy=(0.50, 0.66), xytext=(0.49, 0.66), arrowprops=flow_arr)
    ax.annotate("", xy=(0.73, 0.66), xytext=(0.72, 0.66), arrowprops=flow_arr)

    # Downward Flow from Step 3 to Actions
    down_arr = dict(arrowstyle="-|>", color=ACCENT_GREEN, lw=2.5, mutation_scale=18)
    ax.annotate("", xy=(0.61, 0.35), xytext=(0.61, 0.43), arrowprops=down_arr)

    # 2 Bottom Outcome & Systems Stages (y = 0.35, h = 0.26)
    draw_hl_card(0.05, 0.35, 0.43, 0.26, "5", "INTELLIGENT OUTCOMES & ACTIONS", "[ACTION]", [
        "Schedules appointments directly in calendar",
        "Qualifies leads & collects essential details",
        "Hot-transfers to human staff when requested",
        "Schedules priority callback if line is busy"
    ], ACCENT_GREEN)

    draw_hl_card(0.52, 0.35, 0.42, 0.26, "6", "BUSINESS & CRM INTEGRATION", "[SYNC]", [
        "Syncs lead & transcript to CRM instantly",
        "Sends live alerts to team via Slack / SMS",
        "Updates Super Admin & Client Dashboards",
        "Generates call summaries & sentiment score"
    ], ACCENT_ROSE)

    # Arrow between 5 and 6
    ax.annotate("", xy=(0.51, 0.22), xytext=(0.49, 0.22), arrowprops=dict(arrowstyle="-|>", color=ACCENT_ROSE, lw=2.5, mutation_scale=18))

    # Bottom Footer Tag
    ax.text(0.5, 0.03, "A.L.F.I.E Voice AI Platform • High-Level Architecture Flow",
            color=TEXT_MUTED, fontsize=9.5, ha='center')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "alfie_high_level_flow.png")
    plt.savefig(output_path, dpi=300, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}")


def generate_pdf_deck():
    """Compiles the diagrams and executive architectural summaries into a presentation PDF."""
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    pdf_path = os.path.join(OUTPUT_DIR, "ALFIE_Architecture_and_Call_Flow_Presentation.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter),
                            leftMargin=30, rightMargin=30, topMargin=25, bottomMargin=25)

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'Heading2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor("#334155"),
        leading=14
    )

    story = []

    # PAGE 1: Title & Executive Summary
    story.append(Paragraph("A.L.F.I.E — Voice AI Enterprise Platform", title_style))
    story.append(Paragraph("Architecture, Database E.R.D & End-to-End Call Lifecycle Flow Deck", subtitle_style))
    story.append(Spacer(1, 10))

    summary_text = """
    <b>A.L.F.I.E</b> is an autonomous, sub-second latency Voice AI operating system engineered for enterprise inbound/outbound call operations, intelligent CRM appointment scheduling, lead qualification, and resilient hot-transfer routing across 5 distinct commercial verticals (Law Firms, Medical Clinics, Real Estate, Luxury Car Rentals, and Hospitality).
    """
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 15))

    # Tech Stack Summary Table
    table_data = [
        [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Technologies & Protocols</b>", body_style), Paragraph("<b>Key Responsibilities & SLAs</b>", body_style)],
        [Paragraph("<b>Telephony & Media</b>", body_style), Paragraph("LiveKit WebRTC Cloud / Self-Hosted, SIP Trunks (Twilio / Telnyx), Opus/PCM Codecs", body_style), Paragraph("Inbound PSTN dispatch, audio frame streaming, sub-25ms jitter buffer", body_style)],
        [Paragraph("<b>Speech-to-Text (STT)</b>", body_style), Paragraph("Deepgram Nova-3, AssemblyAI Streaming, Silero VAD", body_style), Paragraph("Real-time audio transcription, turn detection, 180ms latency SLA", body_style)],
        [Paragraph("<b>Reasoning Core (LLM)</b>", body_style), Paragraph("Gemini 2.5, OpenAI GPT-4o-mini, Groq Llama-3.3, CachedOpenAILLM", body_style), Paragraph("Vertical persona instruction, intent routing, function calling, 320ms TTFT", body_style)],
        [Paragraph("<b>Speech Synthesis (TTS)</b>", body_style), Paragraph("Cartesia Sonic (Sonic-1 / Multilingual), ElevenLabs Turbo v2", body_style), Paragraph("Human-like cadence, streaming PCM chunking, 190ms TTFA", body_style)],
        [Paragraph("<b>In-Memory Caches & State</b>", body_style), Paragraph("Redis Stack 7.4+ (Bloom, TimeSeries, Vector Search, Streams, Hashes)", body_style), Paragraph("90-day caller context memory, semantic prompt cache, spam dedup, stream ingest", body_style)],
        [Paragraph("<b>Persistence & Telemetry</b>", body_style), Paragraph("PostgreSQL 16 (AsyncPG connection pool 2-20), Redis Streams, WebSockets", body_style), Paragraph("Multi-tenant call recordings, billing ledgers, QA metrics, real-time admin sync", body_style)]
    ]

    t = Table(table_data, colWidths=[120, 260, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(PageBreak())

    # PAGE 2: High-Level Simplified Flow
    story.append(Paragraph("1. High-Level Call & Agent Flow (Executive)", h2_style))
    story.append(Paragraph("Abstracted overview: Ingress -> Listen -> Think & Decide -> Speak -> Business Actions -> CRM Sync.", subtitle_style))
    story.append(Image(os.path.join(OUTPUT_DIR, "alfie_high_level_flow.png"), width=730, height=395))
    story.append(PageBreak())

    # PAGE 3: Deep Technical Call Flow Diagram Visual
    story.append(Paragraph("2. Deep Technical Call & Agent Lifecycle Flow", h2_style))
    story.append(Paragraph("Sub-second speech-to-speech loop across LiveKit, Deepgram, LLM reasoning, Cartesia TTS, and Redis caching.", subtitle_style))
    story.append(Image(os.path.join(OUTPUT_DIR, "alfie_call_flow_diagram.png"), width=730, height=395))
    story.append(PageBreak())

    # PAGE 4: Database E.R.D & In-Memory Topology Visual
    story.append(Paragraph("3. Relational Database Schema (E.R.D) & Memory Topology", h2_style))
    story.append(Paragraph("PostgreSQL multi-tenant architecture, call recording ledgers, line-busy callbacks, and Redis Stack state.", subtitle_style))
    story.append(Image(os.path.join(OUTPUT_DIR, "alfie_erd_diagram.png"), width=730, height=395))

    doc.build(story)
    print(f"Generated Presentation PDF: {pdf_path}")


if __name__ == "__main__":
    generate_high_level_flow_diagram()
    generate_erd_diagram()
    generate_call_flow_diagram()
    try:
        generate_pdf_deck()
    except Exception as e:
        print(f"PDF deck compilation note: {e}")

