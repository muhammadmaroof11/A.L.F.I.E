import React, { useState } from 'react';
import {
  PhoneMissed,
  PhoneCall,
  Clock,
  UserX,
  CalendarCheck,
  MessageSquareCheck,
  TrendingDown,
  TrendingUp,
  Play,
  AlertTriangle,
  Radio,
  Cpu,
  Sparkles,
  PhoneOff,
  Zap,
  Lock,
  CheckCircle2,
  XCircle,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import { Button } from '../ui/button';
import BeforeAfterAudioPlayer from '../ui/BeforeAfterAudioPlayer';
import TelephonySignalFlow from '../ui/TelephonySignalFlow';
import WaveformEqualizer from '../ui/WaveformEqualizer';

const legacyNodes = [
  {
    step: '01',
    label: 'Inbound Ringing (Hands Occupied)',
    sub: 'Cutting hair, examining patient, or in court. Phone rings 4 times.',
    icon: PhoneMissed
  },
  {
    step: '02',
    label: 'Voicemail Recording Greeting',
    sub: 'Drops to generic prompt: "Please leave a message after the tone..."',
    icon: Clock
  },
  {
    step: '03',
    label: 'Immediate Call Disconnect',
    sub: '84% of callers refuse voicemail and hang up immediately.',
    icon: UserX
  },
  {
    step: '04',
    label: 'Revenue Lost to Competitor',
    sub: 'Customer searches Google Maps and books with the next available shop.',
    icon: TrendingDown
  }
];

const alfieNodes = [
  {
    step: '01',
    label: 'First Ring Pickup',
    sub: 'Answers instantly in under 350ms with warm human cadence.',
    icon: PhoneCall
  },
  {
    step: '02',
    label: 'Natural Q&A & Intake',
    sub: 'Answers service menu pricing, staff availability, and business FAQs.',
    icon: Cpu
  },
  {
    step: '03',
    label: 'Direct Calendar Lock',
    sub: 'Locks open chair in Square, Fresha, Calendly, or EHR system.',
    icon: CalendarCheck
  },
  {
    step: '04',
    label: 'Instant SMS Confirmation',
    sub: 'Caller receives immediate text receipt with location & appointment details.',
    icon: MessageSquareCheck
  }
];

export default function ProblemSolution() {
  const [activeSignalStep, setActiveSignalStep] = useState(3);
  const [isSimulatingPulse, setIsSimulatingPulse] = useState(false);

  const runSimulation = () => {
    setIsSimulatingPulse(true);
    setActiveSignalStep(0);
    const t1 = setTimeout(() => setActiveSignalStep(1), 700);
    const t2 = setTimeout(() => setActiveSignalStep(2), 1400);
    const t3 = setTimeout(() => {
      setActiveSignalStep(3);
      setIsSimulatingPulse(false);
    }, 2200);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  };

  return (
    <section id="signal-pipeline" className="pb-24 pt-12 bg-slate-50/50 text-slate-900 relative overflow-hidden border-b border-slate-200/70">
      <div id="signal-flow" className="absolute -top-20" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Call Intake Benchmark
          </p>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Never lose a caller to voicemail again
          </h2>

          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-2xl mx-auto">
            84% of customers who reach a voicemail recording hang up without leaving a message. A.L.F.I.E. answers on the first ring, handles questions, and books appointments directly.
          </p>

          {/* Interactive Simulation Trigger Button */}
          <div className="pt-2">
            <Button
              variant="primary"
              size="sm"
              onClick={runSimulation}
              disabled={isSimulatingPulse}
              className="gap-2 text-xs font-semibold bg-[#008BC5] hover:bg-[#007cae] text-white border-0 shadow-2xs rounded-full px-5 py-2 cursor-pointer transition-all"
            >
              <Play className={`w-3.5 h-3.5 ${isSimulatingPulse ? 'animate-spin text-white' : 'fill-current'}`} />
              <span>{isSimulatingPulse ? 'Simulating Call Ingress...' : 'Simulate Inbound Call'}</span>
            </Button>
          </div>
        </div>

        {/* Dual Pipelines Grid (Legacy vs A.L.F.I.E) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto items-stretch mb-16">

          {/* Card 1: Legacy Voicemail Drop */}
          <ScrollReveal y={20} duration={0.5} delay={0.1}>
            <div className="h-full p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/70 shadow-2xs flex flex-col justify-between">
              <div>
                {/* Header */}
                <div className="flex items-center justify-between pb-5 border-b border-slate-100 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs">
                      01
                    </div>
                    <div>
                      <h3 className="font-semibold text-base text-slate-900">
                        Standard Voicemail Drop
                      </h3>
                      <p className="text-xs text-slate-500">Traditional 4-Ring Recording</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200/60">
                    High Drop-Off
                  </span>
                </div>

                {/* 3D Robot Chaos Video Animation (2.webm) */}
                <div className="relative w-full h-44 rounded-2xl bg-slate-50/50 overflow-hidden mb-4 border border-slate-100 flex items-center justify-center">
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    poster="/assets/posters/2.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/brand_mascot/2.webm" type="video/webm" />
                  </video>
                </div>

                {/* Steps */}
                <div className="space-y-3 my-4">
                  {legacyNodes.map((node, idx) => {
                    const IconComp = node.icon;
                    const isActive = isSimulatingPulse && activeSignalStep === idx;
                    return (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border transition-all duration-200 ${
                          isActive
                            ? 'bg-[#1D293D] text-white border-[#1D293D] shadow-2xs'
                            : 'bg-slate-50/70 border-slate-200/60'
                        }`}
                      >
                        <div className="flex items-center gap-2.5 mb-1">
                          <div className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 ${
                            isActive ? 'bg-[#008BC5] text-white' : 'bg-white text-slate-700 border border-slate-200'
                          }`}>
                            <IconComp className="w-3 h-3" />
                          </div>
                          <span className={`font-semibold text-xs ${isActive ? 'text-white' : 'text-slate-900'}`}>{node.label}</span>
                        </div>
                        <p className={`text-xs pl-7 leading-relaxed ${isActive ? 'text-slate-300' : 'text-slate-500'}`}>{node.sub}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-medium mt-4">
                <span className="text-slate-500">Impact:</span>
                <span className="text-slate-700 font-semibold">Lost customer & revenue</span>
              </div>
            </div>
          </ScrollReveal>

          {/* Card 2: With A.L.F.I.E */}
          <ScrollReveal y={20} duration={0.5} delay={0.2}>
            <div className="h-full p-6 sm:p-8 rounded-3xl bg-white border border-[#008BC5]/20 shadow-xs flex flex-col justify-between ring-1 ring-[#008BC5]/10">
              <div>
                {/* Header */}
                <div className="flex items-center justify-between pb-5 border-b border-slate-100 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-[#008BC5] text-white flex items-center justify-center font-bold text-xs">
                      02
                    </div>
                    <div>
                      <h3 className="font-semibold text-base text-slate-900">
                        With A.L.F.I.E.
                      </h3>
                      <p className="text-xs text-slate-500">Sub-Second AI Receptionist</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-medium border border-emerald-200/60 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Instant Answer</span>
                  </span>
                </div>

                {/* 3D Robot Flow Video Animation (3.webm) */}
                <div className="relative w-full h-44 rounded-2xl bg-slate-50/50 overflow-hidden mb-4 border border-slate-100 flex items-center justify-center">
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    poster="/assets/posters/3.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/brand_mascot/3.webm" type="video/webm" />
                  </video>
                </div>

                {/* Steps */}
                <div className="space-y-3 my-4">
                  {alfieNodes.map((node, idx) => {
                    const IconComp = node.icon;
                    const isActive = isSimulatingPulse && activeSignalStep === idx;
                    return (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border transition-all duration-200 ${
                          isActive
                            ? 'bg-[#1D293D] text-white border-[#1D293D] shadow-2xs'
                            : 'bg-slate-50/70 border-slate-200/60'
                        }`}
                      >
                        <div className="flex items-center gap-2.5 mb-1">
                          <div className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 ${
                            isActive ? 'bg-white text-slate-900' : 'bg-[#008BC5] text-white'
                          }`}>
                            <IconComp className="w-3 h-3" />
                          </div>
                          <span className={`font-semibold text-xs ${isActive ? 'text-white' : 'text-slate-900'}`}>
                            {node.label}
                          </span>
                        </div>
                        <p className={`text-xs pl-7 leading-relaxed ${isActive ? 'text-slate-300' : 'text-slate-600'}`}>
                          {node.sub}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-medium mt-4">
                <span className="text-slate-500">Impact:</span>
                <span className="text-slate-900 font-semibold">100% Captured appointment & SMS receipt</span>
              </div>
            </div>
          </ScrollReveal>

        </div>

        {/* Audio Player */}
        <ScrollReveal y={20} duration={0.5} className="max-w-4xl mx-auto mb-16">
          <BeforeAfterAudioPlayer />
        </ScrollReveal>

        {/* Telephony Signal Flow */}
        <ScrollReveal y={20} duration={0.5} className="max-w-6xl mx-auto">
          <TelephonySignalFlow />
        </ScrollReveal>

      </div>
    </section>
  );
}
