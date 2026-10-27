import React, { useState, useEffect } from 'react';
import { ArrowRight, PhoneCall, CheckCircle2 } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import InteractiveSoundwaveGrid from '../ui/InteractiveSoundwaveGrid';
import DynamicVoiceWave from '../ui/DynamicVoiceWave';
import VoiceBorderFrame from '../ui/VoiceBorderFrame';
import { Button } from '../ui/button';

export default function HeroSection({ onStartDemo }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative w-full mt-14 h-[calc(100vh-3.5rem)] min-h-[520px] flex items-center justify-center bg-white text-slate-900 border-b border-slate-200/80">

      {/* Calm Ambient Wave Canvas */}
      <InteractiveSoundwaveGrid />

      {/* Mirrored Dual Voice Wave Spectrum Straddling Section Border */}
      <div
        className={`absolute bottom-0 left-0 right-0 w-full pointer-events-none z-20 translate-y-1/2 transition-opacity duration-1000 ease-out ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
      >
        <DynamicVoiceWave className="w-full h-16 sm:h-20 md:h-24 lg:h-28" />
      </div>

      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 py-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">

          {/* ── Left Column: Value Headline & Copy (Extended Width) ── */}
          <div className="lg:col-span-7 flex flex-col justify-center space-y-5 lg:space-y-6">

            {/* Main Pain-Hitting Prominent Headline (3 Lines) */}
            <ScrollReveal y={15} duration={0.5}>
              <h1 className="text-3xl sm:text-4xl lg:text-[3.2rem] xl:text-[3.7rem] font-extrabold tracking-tight text-slate-900 leading-[1.08]">
                Never Lose Clients to Voicemail.{' '}
                <span className="text-[#008BC5] font-extrabold">A.L.F.I.E Books Them on Ring 1.</span>
              </h1>
            </ScrollReveal>

            {/* High-Converting Visceral Body Copy (Extended Max Width) */}
            <ScrollReveal y={15} duration={0.5} delay={0.1}>
              <p className="text-base sm:text-lg lg:text-[1.125rem] text-slate-600 font-normal leading-relaxed max-w-2xl">
                85% of callers who hit voicemail hang up to call your competitor. A.L.F.I.E answers on Ring 1 (&lt;342ms), speaks with natural human warmth, and locks appointments into your calendar 24/7.
              </p>
            </ScrollReveal>

            {/* Call To Action Buttons */}
            <ScrollReveal y={15} duration={0.5} delay={0.2}>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-1">
                <Button
                  size="lg"
                  variant="primary"
                  onClick={() => {
                    if (onStartDemo) onStartDemo('clinic');
                    else scrollTo('demo-arena');
                  }}
                  className="gap-2 text-xs sm:text-sm font-semibold cursor-pointer px-5 py-3.5 bg-[#008BC5] text-white hover:bg-[#007cae] rounded-xl shadow-xs border-0"
                >
                  <PhoneCall className="w-4 h-4 text-white" />
                  <span>Test Live Call in Browser</span>
                  <ArrowRight className="w-4 h-4 text-white/80" />
                </Button>

                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => scrollTo('how-it-works')}
                  className="gap-2 text-xs sm:text-sm font-medium border-slate-200 text-slate-700 hover:bg-slate-50 px-5 py-3.5 rounded-xl cursor-pointer"
                >
                  <span>See How It Works</span>
                </Button>
              </div>

              {/* Verified Telephony Specs Bar */}
              <div className="flex flex-wrap items-center gap-4 sm:gap-6 pt-5 text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Works with Existing Number</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Square &amp; EHR Lock</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Sub-400ms Turnaround</span>
                </span>
              </div>
            </ScrollReveal>

          </div>

          {/* ── Right Column: Enterprise Voice Terminal Mascot Pod ── */}
          <div className="lg:col-span-5 flex items-center justify-center lg:justify-end">
            <ScrollReveal y={20} duration={0.6} delay={0.2} className="w-full flex justify-center lg:justify-end">
              <VoiceBorderFrame className="w-[250px] sm:w-[290px] lg:w-[325px] aspect-square">
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="/assets/posters/1.jpg"
                  className="w-full h-full object-contain scale-[0.95] pointer-events-none p-0 border-0 outline-none bg-transparent"
                >
                  <source src="/assets/brand_mascot/1.mp4" type="video/mp4" />
                </video>
              </VoiceBorderFrame>
            </ScrollReveal>
          </div>

        </div>
      </div>

    </section>
  );
}
