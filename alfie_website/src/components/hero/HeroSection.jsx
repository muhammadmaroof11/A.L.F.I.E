import React from 'react';
import { Phone, ArrowRight, Zap, Play, CheckCircle2, Radio } from 'lucide-react';
import ModelViewer from '../3d/ModelViewer';
import ScrollReveal from '../shared/ScrollReveal';

export default function HeroSection({ onStartDemo }) {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  // 18 harmonic spectrum bars for the audio visualizer inside the headphones
  const spectrumDelays = [
    0.1, 0.35, 0.6, 0.2, 0.75, 0.4, 0.15, 0.85, 0.3,
    0.5, 0.25, 0.65, 0.18, 0.8, 0.38, 0.55, 0.28, 0.12
  ];

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-28 pb-16 bg-[#091728] overflow-hidden">
      
      {/* ── LAYER 1: Ambient Video Background ── */}
      <div className="absolute inset-0 z-0">
        <video 
          autoPlay 
          loop 
          muted 
          playsInline
          className="w-full h-full object-cover opacity-[0.12]"
        >
          <source src="/videos/hero_bg.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-[#091728]/60 via-[#091728]/40 to-[#091728]" />
      </div>

      {/* ── LAYER 2: Dark Grid Pattern ── */}
      <div className="absolute inset-0 bg-grid-dark pointer-events-none z-[1]" />

      {/* ── LAYER 3: Flowing SVG Soundwave ── */}
      <div className="absolute inset-0 pointer-events-none z-[2] overflow-hidden flex items-center">
        <div className="w-[200%] h-full flex shrink-0 animate-wave-travel-1 opacity-50">
          <svg 
            viewBox="0 0 2880 500" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg" 
            className="w-full h-full object-cover"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="cyanWaveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.5" />
                <stop offset="25%" stopColor="#60A5FA" stopOpacity="0.7" />
                <stop offset="50%" stopColor="#818CF8" stopOpacity="0.55" />
                <stop offset="75%" stopColor="#38BDF8" stopOpacity="0.65" />
                <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.5" />
              </linearGradient>

              <linearGradient id="dimWaveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.15" />
                <stop offset="50%" stopColor="#818CF8" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#38BDF8" stopOpacity="0.15" />
              </linearGradient>

              <filter id="waveGlow" x="-10%" y="-10%" width="120%" height="120%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Primary wave */}
            <path
              d="M 0,260 C 360,160 720,380 1080,330 C 1440,280 1800,160 2160,380 C 2520,330 2880,260 2880,260"
              stroke="url(#cyanWaveGrad)"
              strokeWidth="2.5"
              fill="none"
              strokeLinecap="round"
              filter="url(#waveGlow)"
            />

            {/* Secondary wave (dimmer, dashed) */}
            <path
              d="M 0,290 C 400,380 800,240 1200,350 C 1600,420 2000,240 2400,350 C 2800,420 2880,290 2880,290"
              stroke="url(#dimWaveGrad)"
              strokeWidth="1.75"
              strokeDasharray="5 7"
              fill="none"
            />
          </svg>
        </div>
      </div>

      {/* ── LAYER 4: Content ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-4 items-center">
          
          {/* Left Column: Editorial Typography */}
          <div className="lg:col-span-7 space-y-6 text-left">
            
            {/* Telemetry Pill */}
            <ScrollReveal y={15} duration={0.5}>
              <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-white/[0.05] backdrop-blur-md border border-white/[0.08] text-slate-300">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-mono text-slate-500 text-[11px]">TELEPHONY GATEWAY</span>
                <span className="text-slate-600">/</span>
                <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" /> 390ms Sub-Second TTFT
                </span>
              </div>
            </ScrollReveal>

            {/* Headline */}
            <ScrollReveal y={20} duration={0.6} delay={0.08}>
              <h1 className="text-4xl sm:text-5xl lg:text-[72px] font-black tracking-[-0.04em] text-white leading-[1.02]">
                Never Miss a $10,000+ Inbound Call Again.
              </h1>
            </ScrollReveal>

            {/* Sub-copy */}
            <ScrollReveal y={20} duration={0.6} delay={0.14}>
              <p className="text-base sm:text-lg text-slate-400 font-normal leading-relaxed max-w-xl">
                Autonomous, conversational voice AI infrastructure built for personal injury law practices, dental & medical clinics, and luxury fleet dispatch. Answers on the first ring, verifies case merits and insurance, and warm-transfers qualified leads to your cell.
              </p>
            </ScrollReveal>

            {/* CTAs */}
            <ScrollReveal y={15} duration={0.6} delay={0.2}>
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
                <button
                  onClick={() => {
                    if (onStartDemo) onStartDemo();
                    else scrollTo('demo-arena');
                  }}
                  className="cd-btn-primary w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5"
                >
                  <Phone className="w-4 h-4 text-blue-200" />
                  <span>Launch Live Call Demo</span>
                  <ArrowRight className="w-4 h-4 opacity-70" />
                </button>

                <button
                  onClick={() => scrollTo('niche-showcase')}
                  className="cd-btn-secondary w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2"
                >
                  <Play className="w-3.5 h-3.5 text-slate-400" />
                  <span>View Architecture Spec</span>
                </button>
              </div>
            </ScrollReveal>

            {/* Trust checklist */}
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

          {/* Right Column: 3D Headset + Waveform Inside */}
          <div className="lg:col-span-5 relative flex items-center justify-center">
            <div className="w-full aspect-[4/3] max-w-[460px] min-h-[340px] sm:min-h-[380px] relative flex items-center justify-center">
              
              <ModelViewer
                url="/models/hero_headset.glb"
                scale={1.32}
                rotation={[0.08, 0.42, -0.06]}
                autoRotate={false}
                enableFloat={false}
                cameraPosition={[0, 0, 4.5]}
                className="w-full h-full min-h-[340px] sm:min-h-[380px]"
              />

              {/* Waveform Badge Inside Headphone Arch */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 pt-6">
                <div className="w-fit max-w-[210px] bg-[#111726]/85 backdrop-blur-md px-3 py-2 rounded-xl border border-white/[0.08] shadow-sm flex flex-col items-center gap-1 pointer-events-auto transition-transform hover:scale-105">
                  
                  <div className="flex items-center gap-1.5 text-[9px] font-mono font-bold text-slate-300">
                    <Radio className="w-2.5 h-2.5 text-[#38BDF8] animate-pulse" />
                    <span>Live Channel • Opus 48k</span>
                  </div>

                  <div className="w-[170px] h-4 flex items-end justify-between gap-[2px] px-1 bg-white/[0.04] rounded p-0.5 border border-white/[0.06]">
                    {spectrumDelays.map((delay, idx) => (
                      <span
                        key={idx}
                        className="flex-1 rounded-full spectrum-bar"
                        style={{
                          height: '100%',
                          animationDelay: `${delay}s`,
                          backgroundColor: idx % 3 === 0 ? '#38BDF8' : idx % 2 === 0 ? '#60A5FA' : '#818CF8'
                        }}
                      />
                    ))}
                  </div>

                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

    </section>
  );
}
