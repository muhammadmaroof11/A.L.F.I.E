import React from 'react';
import { Check, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';

const tiers = [
  {
    name: 'Starter Practice',
    badge: 'Single Niche',
    price: '$199',
    period: '/mo',
    usage: '+ $0.15/min live voice stream',
    desc: 'Ideal for solo law practices, private clinics, or boutique hospitality venues needing 24/7 after-hours call capture.',
    popular: false,
    features: [
      '1 Specialized AI Receptionist Persona',
      '24/7 Inbound Call Pick-Up (Sub-second TTFT)',
      'Direct Calendar Slot Booking (Cal.com / EMR)',
      'Basic Lead Capture & SMS Summary Dispatch',
      'Dual-Channel Call Recordings & Transcripts',
      'Standard LiveKit WebRTC Voice Pipeline'
    ],
    buttonText: 'Deploy Starter Node',
    buttonClass: 'btn-secondary'
  },
  {
    name: 'Growth Enterprise',
    badge: 'Most Popular',
    price: '$499',
    period: '/mo',
    usage: '+ $0.12/min live voice stream',
    desc: 'Designed for scaling multi-partner law firms, medical groups, and fleets needing hot call transfers and CRM integrations.',
    popular: true,
    features: [
      'Up to 5 Customized Persona Nodes',
      'Live SIP Hot Lead Transfer directly to Mobile',
      'Automated SMS Retainer & Intake Dispatch',
      'Real-Time Insurance Network Validation',
      'Custom Webhook Builder (Zapier/GHL/HubSpot)',
      'Redis 90-Day Caller Relationship Memory',
      'Priority LiveKit Telephony Queue'
    ],
    buttonText: 'Claim Growth Plan',
    buttonClass: 'btn-primary'
  },
  {
    name: 'Dedicated Infrastructure',
    badge: 'Custom SLA',
    price: 'Custom',
    period: '',
    usage: 'Volume-tiered per-minute discounts',
    desc: 'For multi-location hospital systems, statewide law conglomerates, and national fleet operations with dedicated SIP trunks.',
    popular: false,
    features: [
      'Unlimited Concurrent Call Handling (500+ calls)',
      'Dedicated Private Redis Stack & LiveKit Cluster',
      'Custom Voice Cloning & Tone Engineering',
      'HIPAA / BAA & SOC-2 Signed Security SLA',
      'Direct Database & EMR/EHR Custom Adapters',
      '24/7 Dedicated Solutions Engineer on Slack'
    ],
    buttonText: 'Contact Enterprise Team',
    buttonClass: 'btn-secondary'
  }
];

export default function Pricing() {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="pricing" className="py-20 bg-[#0B0F17] border-b border-white/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white/[0.05] text-[#CBD5E1] border border-white/[0.06]">
            <span>Enterprise SaaS Pricing</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC] tracking-tight">
            Transparent Plans Engineered for Predictable ROI
          </h2>
          <p className="text-sm sm:text-base text-[#94A3B8]">
            No long-term lock-ins. Zero proprietary hardware required. Pay for active telephony minutes with full credit accounting.
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-6xl mx-auto items-stretch">
          {tiers.map((t, idx) => (
            <ScrollReveal key={idx} y={20} duration={0.6} delay={idx * 0.12}>
              <div 
                className={`h-full rounded-2xl p-7 flex flex-col justify-between relative transition-all bg-[#091728] ${
                  t.popular 
                    ? 'border-2 border-slate-900 shadow-md ring-4 ring-slate-900/5' 
                    : 'border border-white/[0.06] shadow-none hover:border-slate-300'
                }`}
              >
                {/* Popular Floating Badge */}
                {t.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-3 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-[0_2px_8px_rgba(0,0,0,0.3)]">
                    ★ {t.badge}
                  </div>
                )}

                <div>
                  {/* Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-white/[0.04]">
                    <div>
                      <h3 className="font-extrabold text-lg text-[#F8FAFC]">{t.name}</h3>
                      {!t.popular && (
                        <span className="text-[10px] font-semibold text-[#64748B] bg-white/[0.05] px-2 py-0.5 rounded mt-1 inline-block">
                          {t.badge}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Price Block */}
                  <div className="py-5">
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl sm:text-4xl font-black text-[#F8FAFC] tracking-tight font-mono">{t.price}</span>
                      <span className="text-xs font-bold text-[#64748B]">{t.period}</span>
                    </div>
                    <p className="text-[11px] text-[#38BDF8] font-semibold mt-1">
                      {t.usage}
                    </p>
                    <p className="text-xs text-[#94A3B8] mt-2.5 leading-relaxed">
                      {t.desc}
                    </p>
                  </div>

                  {/* Feature Checklist */}
                  <div className="space-y-2.5 py-5 border-t border-white/[0.04]">
                    <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Included capabilities:</p>
                    <ul className="space-y-2">
                      {t.features.map((feat, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-[#CBD5E1] font-medium">
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Button Action */}
                <div className="pt-4">
                  <button
                    onClick={() => scrollTo('demo-arena')}
                    className={`${t.buttonClass} w-full text-xs py-3 rounded-xl`}
                  >
                    <span>{t.buttonText}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

              </div>
            </ScrollReveal>
          ))}
        </div>

        {/* Security Guarantee Strip */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 text-xs font-medium text-[#64748B] bg-[#091728] px-4 py-2 rounded-full border border-white/[0.06] shadow-none">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>14-Day Money Back Guarantee • BYOK Carrier Support • Cancel Anytime</span>
          </div>
        </div>

      </div>
    </section>
  );
}
