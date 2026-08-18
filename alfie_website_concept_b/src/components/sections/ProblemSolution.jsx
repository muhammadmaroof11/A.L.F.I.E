import React, { useState } from 'react';
import { XCircle, CheckCircle2, TrendingDown, TrendingUp, PhoneMissed, PhoneCall, Clock, UserX, UserCheck, AlertTriangle, ShieldCheck, Video, Image as ImageIcon } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';

export default function ProblemSolution() {
  const [activeMedia, setActiveMedia] = useState('video'); // 'video' | 'photo'

  return (
    <section className="py-20 bg-[#091728] border-b border-white/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-300 border border-amber-200">
            <span>The $10,000+ Missed Call Reality</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC] tracking-tight">
            Why High-Value Businesses Bleed Clients After Hours
          </h2>
          <p className="text-sm sm:text-base text-[#94A3B8]">
            In competitive verticals like Personal Injury Law or Private Clinics, 84% of callers hang up and dial the next competitor if they hit voicemail or an offshore answering service.
          </p>
        </div>

        {/* Cinematic Side-by-Side Split Story */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto items-stretch">
          
          {/* Card 1: The Pain (Before) */}
          <ScrollReveal y={20} duration={0.6} delay={0.1}>
            <div className="h-full bg-[#0B0F17] rounded-3xl p-6 sm:p-8 border border-red-500/20 shadow-none flex flex-col justify-between">
              
              <div>
                {/* Header */}
                <div className="flex items-center justify-between pb-4 border-b border-red-500/10">
                  <div className="flex items-center gap-2 text-red-400 font-extrabold text-base">
                    <XCircle className="w-5 h-5 text-red-400" />
                    <span>Traditional Phone Bottlenecks</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-md bg-red-100 text-red-300 text-[11px] font-bold">
                    34% Call Failure Rate
                  </span>
                </div>

                {/* Hero Media: Overwhelmed Lawyer */}
                <div className="my-5 rounded-2xl overflow-hidden border border-red-500/15 shadow-[0_4px_12px_rgba(0,0,0,0.3)] relative h-[220px] bg-slate-900 group">
                  <img 
                    src="/images/before_overwhelmed.jpeg" 
                    alt="Overwhelmed Business Owner at Cluttered Desk" 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent flex items-end p-4">
                    <div>
                      <p className="text-white text-xs font-bold flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        <span>The Cost: $140,000+ Lost In Unanswered Retainers</span>
                      </p>
                      <p className="text-[11px] text-slate-300 font-mono mt-0.5">
                        Callers dial your rival firm within 90 seconds of hitting voicemail.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Pain Points List */}
                <div className="space-y-3 text-xs">
                  <div className="flex items-start gap-2.5">
                    <PhoneMissed className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">4-Minute Hold Times & Voicemails</p>
                      <p className="text-[#64748B]">Peak hours and lunch breaks cause high-intent clients to hang up.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5">
                    <UserX className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">Offshore Call Centers Read Scripts</p>
                      <p className="text-[#64748B]">Generic operators cannot verify dental insurance or intake accident merits.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5">
                    <Clock className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">Emergency Leads Sit Overnight</p>
                      <p className="text-[#64748B]">No instant partner hot-transfer means emergency retained cases are lost.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Metric */}
              <div className="pt-4 mt-6 border-t border-red-500/10 flex items-center justify-between text-xs font-semibold text-red-400 bg-red-500/100/10 p-3 rounded-xl">
                <span className="flex items-center gap-1.5 font-bold">
                  <TrendingDown className="w-4 h-4" /> Average Missed Revenue:
                </span>
                <span className="font-mono font-bold">$12,000 - $45,000 / mo</span>
              </div>

            </div>
          </ScrollReveal>

          {/* Card 2: The Victory (After - A.L.F.I.E) */}
          <ScrollReveal y={20} duration={0.6} delay={0.2}>
            <div className="h-full bg-[#0B0F17] rounded-3xl p-6 sm:p-8 border border-blue-500/20 shadow-none flex flex-col justify-between">
              
              <div>
                {/* Header & Media Toggle */}
                <div className="flex items-center justify-between pb-4 border-b border-blue-500/10">
                  <div className="flex items-center gap-2 text-[#F8FAFC] font-extrabold text-base">
                    <CheckCircle2 className="w-5 h-5 text-[#38BDF8]" />
                    <span>The A.L.F.I.E Standard</span>
                  </div>

                  <div className="flex items-center gap-1 bg-[#091728] p-0.5 rounded-lg border border-white/[0.06]">
                    <button
                      onClick={() => setActiveMedia('video')}
                      className={`px-2.5 py-0.5 rounded text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                        activeMedia === 'video' ? 'bg-blue-600 text-white shadow-none' : 'text-[#94A3B8] hover:text-[#F8FAFC]'
                      }`}
                    >
                      <Video className="w-3 h-3" />
                      Reel
                    </button>
                    <button
                      onClick={() => setActiveMedia('photo')}
                      className={`px-2.5 py-0.5 rounded text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                        activeMedia === 'photo' ? 'bg-slate-900 text-white shadow-none' : 'text-[#94A3B8] hover:text-[#F8FAFC]'
                      }`}
                    >
                      <ImageIcon className="w-3 h-3" />
                      Outcome
                    </button>
                  </div>
                </div>

                {/* Hero Media: Partner Victory Reel / Confident Photo */}
                <div className="my-5 rounded-2xl overflow-hidden border border-blue-500/15 shadow-[0_4px_12px_rgba(0,0,0,0.3)] relative h-[220px] bg-slate-900 group">
                  {activeMedia === 'video' ? (
                    <video 
                      autoPlay 
                      loop 
                      muted 
                      playsInline 
                      className="w-full h-full object-cover"
                    >
                      <source src="/videos/niche_montage.mp4" type="video/mp4" />
                    </video>
                  ) : (
                    <img 
                      src="/images/after_confident.jpeg" 
                      alt="Confident Partner with Seamless Lead Inflow" 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent flex items-end p-4">
                    <div>
                      <p className="text-white text-xs font-bold flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>The Outcome: 100% Inbound Lead Capture</span>
                      </p>
                      <p className="text-[11px] text-slate-300 font-mono mt-0.5">
                        Every caller is triaged, qualified, and delivered straight to your calendar.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Solution Points List */}
                <div className="space-y-3 text-xs">
                  <div className="flex items-start gap-2.5">
                    <PhoneCall className="w-4 h-4 text-[#38BDF8] shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">Zero-Ring Pick Up (390ms Latency)</p>
                      <p className="text-[#64748B]">Sub-second human conversational voice AI with zero dead air.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5">
                    <UserCheck className="w-4 h-4 text-[#38BDF8] shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">Deterministic Domain Qualification</p>
                      <p className="text-[#64748B]">Validates insurance, checks accident statute, or quotes luxury fleet rates.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5">
                    <Clock className="w-4 h-4 text-[#38BDF8] shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-[#E2E8F0]">Warm SIP Transfer + SMS Brief</p>
                      <p className="text-[#64748B]">Sends the managing attorney a full lead summary before their phone rings.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Metric */}
              <div className="pt-4 mt-6 border-t border-blue-500/10 flex items-center justify-between text-xs font-semibold text-emerald-400 bg-emerald-500/100/10 p-3 rounded-xl">
                <span className="flex items-center gap-1.5 font-bold">
                  <TrendingUp className="w-4 h-4 text-emerald-400" /> Inbound Lead Capture Rate:
                </span>
                <span className="font-mono font-bold">99.4% (Zero Dropped Calls)</span>
              </div>

            </div>
          </ScrollReveal>

        </div>

      </div>
    </section>
  );
}
