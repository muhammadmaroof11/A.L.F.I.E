import React, { useState } from 'react';
import { Radio, Cpu, PhoneForwarded, Video, Box, ArrowRight, CheckCircle2, Zap, Terminal } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import ModelViewer from '../3d/ModelViewer';

const pipelineStages = [
  {
    step: '01',
    title: 'Zero-Ring Inbound Pick-Up',
    subtitle: 'LiveKit SIP & WebRTC Connection',
    desc: 'The caller dials your existing business number (Twilio / Telnyx BYOK). A.L.F.I.E connects on the very first ring with sub-second latency and zero dead air.',
    type: '3d',
    mediaUrl: '/models/hero_headset.glb',
    badge: 'Stage 1: SIP Ingestion',
    tech: 'Opus 48kHz WebRTC',
    metric: '390ms TTFT',
    details: [
      'Zero proprietary hardware required',
      'Direct Twilio & Telnyx SIP trunking',
      'Dual-channel acoustic echo cancellation'
    ]
  },
  {
    step: '02',
    title: 'Deterministic Tool Calling',
    subtitle: 'Redis Semantic Memory & SQL Queries',
    desc: 'A.L.F.I.E executes deterministic database lookups to verify dental insurance networks, calculate mileage pricing, or triage accident liability with natural voice cadence.',
    type: '3d',
    mediaUrl: '/models/ai_neural_core.glb',
    badge: 'Stage 2: Execution',
    tech: 'Llama 3.3 70B + Redis',
    metric: 'Zero Hallucinations',
    details: [
      'In-network insurance validation in 65ms',
      '90-day caller relationship history recall',
      'Strict legal & HIPAA compliance guardrails'
    ]
  },
  {
    step: '03',
    title: 'Instant SMS Brief & Hot Bridge',
    subtitle: 'LiveKit SIP Phone Transfer',
    desc: 'The qualified lead is scheduled directly into your EMR or CRM, a complete SMS intake summary is texted to your phone, and the caller is warm-transferred to your cell.',
    type: 'video',
    mediaUrl: '/videos/partner_transfer.mp4',
    badge: 'Stage 3: Conversion',
    tech: 'SIP Transfer + Cal.com',
    metric: '100% Retainer Capture',
    details: [
      'SMS intake brief arrives 1s before phone rings',
      'Warm caller transfer to any mobile cell',
      'Automated calendar slot sync in Cal.com/EMR'
    ]
  }
];

export default function HowItWorks() {
  const [activeStep, setActiveStep] = useState(0);
  const currentStage = pipelineStages[activeStep];

  return (
    <section id="how-it-works" className="py-20 bg-[#0B0F17] border-b border-white/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white/[0.05] text-[#CBD5E1] border border-white/[0.06]">
            <span>Telephony Architecture</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC] tracking-tight">
            How A.L.F.I.E Handles Inbound Calls End-to-End
          </h2>
          <p className="text-sm sm:text-base text-[#94A3B8]">
            Click through the 3 pipeline stages below to inspect our sub-second telephony ingestion, tool calling, and mobile warm-transfer architecture.
          </p>
        </div>

        {/* Interactive Stepper Navigation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-4xl mx-auto mb-8">
          {pipelineStages.map((stage, idx) => {
            const isActive = activeStep === idx;
            return (
              <button
                key={idx}
                onClick={() => setActiveStep(idx)}
                className={`p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#091728] border-slate-900 shadow-[0_4px_12px_rgba(0,0,0,0.3)] ring-2 ring-[#38BDF8]/20'
                    : 'bg-[#111726]/60 border-white/[0.06] hover:bg-[#091728] hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-xs font-bold mb-1">
                  <span className={`font-mono text-base ${isActive ? 'text-[#38BDF8]' : 'text-slate-400'}`}>
                    {stage.step}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${isActive ? 'bg-slate-900 text-white' : 'bg-white/[0.05] text-[#94A3B8]'}`}>
                    {stage.badge}
                  </span>
                </div>
                <p className="text-xs font-bold text-[#F8FAFC]">{stage.title}</p>
                <p className="text-[11px] text-[#64748B] font-mono mt-0.5">{stage.tech}</p>
              </button>
            );
          })}
        </div>

        {/* Dynamic Stage Showcase Console */}
        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-5xl mx-auto bg-[#091728] rounded-3xl border border-white/[0.06] p-6 sm:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.3)]">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              
              {/* Left Column: Stage Specs */}
              <div className="lg:col-span-6 space-y-4">
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-black text-[#38BDF8] font-mono">
                    STAGE {currentStage.step}
                  </span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    {currentStage.metric}
                  </span>
                </div>

                <h3 className="text-xl font-extrabold text-[#F8FAFC]">
                  {currentStage.title}
                </h3>
                <p className="text-xs font-semibold text-[#38BDF8] font-mono">
                  {currentStage.subtitle}
                </p>
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  {currentStage.desc}
                </p>

                {/* Key Checklist */}
                <div className="space-y-2 pt-2 border-t border-white/[0.04]">
                  {currentStage.details.map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-[#CBD5E1] font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: High-Impact Dedicated Media Stage */}
              <div className="lg:col-span-6 flex items-center justify-center">
                <div className="w-full aspect-[4/3] rounded-2xl bg-[#0B0F17] border border-white/[0.06] overflow-hidden relative shadow-none flex items-center justify-center">
                  
                  {currentStage.type === 'video' ? (
                    <video
                      key={currentStage.mediaUrl}
                      autoPlay
                      loop
                      muted
                      playsInline
                      className="w-full h-full object-cover rounded-2xl"
                    >
                      <source src={currentStage.mediaUrl} type="video/mp4" />
                    </video>
                  ) : (
                    <div className="w-full h-full min-h-[260px] flex items-center justify-center">
                      <ModelViewer
                        url={currentStage.mediaUrl}
                        scale={2.2}
                        floatSpeed={1.8}
                        autoRotate={true}
                        cameraPosition={[0, 0, 3.8]}
                      />
                    </div>
                  )}

                  {/* Stage Watermark Badge */}
                  <div className="absolute top-3 right-3 bg-[#111726]/90 backdrop-blur-md px-2.5 py-1 rounded-lg border border-white/[0.06] text-[10px] font-mono font-bold text-[#CBD5E1] shadow-none">
                    <span>{currentStage.type === 'video' ? 'Live Hot-Transfer Climax' : 'Active Telephony Node'}</span>
                  </div>

                </div>
              </div>

            </div>
          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
