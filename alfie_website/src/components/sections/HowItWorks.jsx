import React from 'react';
import { 
  PhoneForwarded, 
  CalendarCheck, 
  MessageSquareCheck, 
  ArrowRight,
  CheckCircle2,
  Radio
} from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import SpotlightCard from '../shared/SpotlightCard';

const steps = [
  {
    step: '01',
    title: 'Forward Your Existing Number',
    desc: 'Keep your current business phone. Simply turn on standard call forwarding from your iPhone, Android, or PBX in under 2 minutes.',
    icon: PhoneForwarded,
    highlights: [
      'Zero new hardware or complex apps required',
      'Works with all carriers (Verizon, AT&T, T-Mobile, Twilio)',
      'Instant conditional or unconditional forwarding'
    ]
  },
  {
    step: '02',
    title: 'A.L.F.I.E Answers & Books Appointments',
    desc: 'Answers on the first ring in under 360ms, speaks with natural human inflection, answers pricing questions, and locks slots.',
    icon: CalendarCheck,
    highlights: [
      'Syncs directly with Square, Fresha, Calendly & Google',
      'Understands your service menus, prices, and FAQs',
      'Handles multiple callers simultaneously with zero hold queues'
    ]
  },
  {
    step: '03',
    title: 'Instant SMS & Warm Handoff',
    desc: 'The caller receives an immediate booking confirmation text with address & parking. High-priority callers can be bridged to your cell.',
    icon: MessageSquareCheck,
    highlights: [
      'Customer receives instant text with booking details',
      'Your personal mobile receives immediate summary alert',
      'Warm live transfer for urgent or high-value inquiries'
    ]
  }
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 bg-slate-50/50 text-slate-900 relative overflow-hidden border-b border-slate-200">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Simple 5-Minute Setup
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            How it works in 3 steps
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Link your existing business line directly to your calendar and mobile notifications.
          </p>
        </div>

        {/* 3 Steps Connected Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto items-stretch relative">
          {steps.map((item, idx) => {
            const IconComp = item.icon;
            return (
              <ScrollReveal key={item.step} y={20} duration={0.5} delay={idx * 0.1}>
                <SpotlightCard className="h-full p-8 flex flex-col justify-between group">
                  
                  <div>
                    {/* Step Number & Icon Header */}
                    <div className="flex items-center justify-between pb-6 border-b border-slate-200 mb-6">
                      <div className="w-12 h-12 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 group-hover:scale-110 group-hover:bg-slate-900 group-hover:text-white transition-all duration-300">
                        <IconComp className="w-6 h-6" />
                      </div>
                      <span className="font-mono font-extrabold text-3xl text-slate-300 group-hover:text-slate-900 transition-colors">
                        {item.step}
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-slate-900 mb-2 font-heading group-hover:text-blue-600 transition-colors">
                      {item.title}
                    </h3>
                    
                    <p className="text-xs text-slate-600 leading-relaxed mb-6">
                      {item.desc}
                    </p>

                    {/* Bullet Highlights */}
                    <div className="space-y-2.5 pt-4 border-t border-slate-200 text-xs">
                      {item.highlights.map((h, i) => (
                        <div key={i} className="flex items-start gap-2 text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                          <span className="leading-snug">{h}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                </SpotlightCard>
              </ScrollReveal>
            );
          })}
        </div>

      </div>
    </section>
  );
}
