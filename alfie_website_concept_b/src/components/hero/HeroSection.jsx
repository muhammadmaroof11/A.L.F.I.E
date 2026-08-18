import React from 'react';
import { Phone, ArrowRight, Zap, Play, CheckCircle2, Radio, Activity, Globe } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';

export default function HeroSection({ onStartDemo }) {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  // 24 harmonic spectrum bars for the dispatch card waveform
  const spectrumDelays = [
    0.1, 0.35, 0.6, 0.2, 0.75, 0.4, 0.15, 0.85, 0.3,
    0.5, 0.25, 0.65, 0.18, 0.8, 0.38, 0.55, 0.28, 0.12,
    0.42, 0.7, 0.32, 0.58, 0.22, 0.48
  ];

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-24 pb-16 hero-dark-band overflow-hidden">
      
      {/* Subtle grid pattern on dark background */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.04]"
        style={{
          backgroundSize: '32px 32px',
          backgroundImage: 
            'linear-gradient(to right, rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.3) 1px, transparent 1px)'
        }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        
        {/* Asymmetric 2-Column Hero */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-center">
          
          {/* ─── LEFT COLUMN (7/12): Editorial Authority Typography ─── */}
          <div className="lg:col-span-7 space-y-6 text-left">
            
            {/* Status Telemetry Pill */}
            <ScrollReveal y={15} duration={0.5}>
              <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-white/[0.06] backdrop-blur-md border border-white/10 text-slate-300">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-mono text-slate-400 text-[11px]">TELEPHONY GATEWAY</span>
                <span className="text-slate-500">/</span>
                <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" /> 390ms Sub-Second TTFT
                </span>
              </div>
            </ScrollReveal>

            {/* Oversized Master Headline — WHITE on dark */}
            <ScrollReveal y={20} duration={0.6} delay={0.08}>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-[-0.04em] text-white leading-[1.05]">
                Never Miss a $10,000+ Inbound Call Again.
              </h1>
            </ScrollReveal>

            {/* Sub-copy — light slate on dark */}
            <ScrollReveal y={20} duration={0.6} delay={0.14}>
              <p className="text-base sm:text-lg text-slate-400 font-normal leading-relaxed max-w-xl">
                Autonomous, conversational voice AI infrastructure built for personal injury law practices, dental & medical clinics, and luxury fleet dispatch. Answers on the first ring, verifies case merits and insurance, and warm-transfers qualified leads to your cell.
              </p>
            </ScrollReveal>

            {/* Action CTAs */}
            <ScrollReveal y={15} duration={0.6} delay={0.2}>
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
                <button
                  onClick={() => {
                    if (onStartDemo) onStartDemo();
                    else scrollTo('demo-arena');
                  }}
                  className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5 bg-white text-[#0B0F17] hover:bg-slate-100 transition-all shadow-sm cursor-pointer"
                >
                  <Phone className="w-4 h-4 text-[#0B0F17]" />
                  <span>Test Live 90s Call In Browser</span>
                  <ArrowRight className="w-4 h-4 opacity-70" />
                </button>

                <button
                  onClick={() => scrollTo('niche-showcase')}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 text-slate-300 border border-white/10 hover:bg-white/[0.06] transition-all cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 text-slate-400" />
                  <span>Watch Vertical Reels</span>
                </button>
              </div>
            </ScrollReveal>

            {/* Trust Checklist */}
            <ScrollReveal y={10} duration={0.5} delay={0.25}>
              <div className="pt-2 flex flex-wrap items-center gap-5 text-xs text-slate-500 font-medium">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Zero Hardware Required</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Twilio / Telnyx SIP BYOK</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>SOC-2 & HIPAA Ready</span>
                </div>
              </div>
            </ScrollReveal>

          </div>

          {/* ─── RIGHT COLUMN (5/12): Glassmorphism Live Dispatch Card ─── */}
          <div className="lg:col-span-5 relative flex items-center justify-center">
            
            <ScrollReveal y={30} duration={0.7} delay={0.15}>
              <div className="glass-dispatch p-5 w-full max-w-[420px]">
                
                {/* Card Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-xs font-bold text-white">
                    <Activity className="w-3.5 h-3.5 text-[#38BDF8]" />
                    <span>Live Audio Waveform</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] font-mono text-emerald-400">ACTIVE</span>
                  </div>
                </div>

                {/* Waveform Visualizer */}
                <div className="glass-dispatch-inner p-3 mb-4">
                  <div className="w-full h-16 flex items-end justify-between gap-[2px]">
                    {spectrumDelays.map((delay, idx) => (
                      <span
                        key={idx}
                        className="flex-1 rounded-full dispatch-bar"
                        style={{
                          height: '100%',
                          animationDelay: `${delay}s`,
                          backgroundColor: idx % 4 === 0 ? '#38BDF8' : idx % 3 === 0 ? '#60A5FA' : idx % 2 === 0 ? '#818CF8' : '#94A3B8',
                          opacity: 0.85
                        }}
                      />
                    ))}
                  </div>
                </div>

                {/* Latency + SIP Ticket Side-by-Side */}
                <div className="grid grid-cols-2 gap-3">
                  
                  {/* Latency Panel */}
                  <div className="glass-dispatch-inner p-3">
                    <p className="text-[10px] font-mono text-slate-400 mb-1">Latency</p>
                    <p className="text-2xl font-black text-white font-mono latency-counter">390<span className="text-sm text-slate-400">ms</span></p>
                    <p className="text-[10px] font-mono text-slate-500">TTFT</p>
                  </div>

                  {/* SIP Ticket Panel */}
                  <div className="glass-dispatch-inner p-3">
                    <p className="text-[10px] font-mono text-slate-400 mb-1.5">Real-time SIP Ticket</p>
                    <div className="space-y-0">
                      <div className="sip-ticket-row">
                        <span className="text-slate-500 font-mono">Caller</span>
                        <span className="text-white font-semibold">Jason Smith</span>
                      </div>
                      <div className="sip-ticket-row">
                        <span className="text-slate-500 font-mono">Phone</span>
                        <span className="text-[#38BDF8] font-mono font-semibold">(323) 234-7788</span>
                      </div>
                      <div className="sip-ticket-row">
                        <span className="text-slate-500 font-mono">Vertical</span>
                        <span className="text-amber-400 font-semibold">PI Law</span>
                      </div>
                      <div className="sip-ticket-row">
                        <span className="text-slate-500 font-mono">Statute</span>
                        <span className="text-emerald-400 font-mono font-semibold">710d</span>
                      </div>
                    </div>
                  </div>

                </div>

              </div>
            </ScrollReveal>

          </div>

        </div>

      </div>

    </section>
  );
}
