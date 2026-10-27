import React from 'react';
import ScrollReveal from '../shared/ScrollReveal';
import { NumberTicker } from '../ui/number-ticker';
import { Marquee } from '../ui/marquee';
import SpotlightCard from '../shared/SpotlightCard';

// Authentic SVG Brand & Ecosystem Icons
const GoogleIcon = () => (
  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
  </svg>
);

const SalesforceIcon = () => (
  <svg className="w-4 h-4 shrink-0 fill-[#00A1E0]" viewBox="0 0 24 24">
    <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3z" />
  </svg>
);

const SquareIcon = () => (
  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
    <rect x="2" y="2" width="20" height="20" rx="5" fill="#000000" />
    <rect x="6.5" y="6.5" width="11" height="11" rx="3" fill="#FFFFFF" />
    <rect x="9" y="9" width="6" height="6" rx="1.5" fill="#000000" />
  </svg>
);

const TwilioIcon = () => (
  <svg className="w-4 h-4 shrink-0 fill-[#F22F46]" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" />
    <circle cx="8.5" cy="8.5" r="2.2" fill="white" />
    <circle cx="15.5" cy="8.5" r="2.2" fill="white" />
    <circle cx="8.5" cy="15.5" r="2.2" fill="white" />
    <circle cx="15.5" cy="15.5" r="2.2" fill="white" />
  </svg>
);

const LiveKitIcon = () => (
  <svg className="w-4 h-4 shrink-0 text-cyan-500 fill-current" viewBox="0 0 24 24">
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
  </svg>
);

const HealthcareIcon = () => (
  <svg className="w-4 h-4 shrink-0 fill-[#4F46E5]" viewBox="0 0 24 24">
    <path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.89 2 1.99 2H19c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z" />
  </svg>
);

const SecurityIcon = () => (
  <svg className="w-4 h-4 shrink-0 fill-[#059669]" viewBox="0 0 24 24">
    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z" />
  </svg>
);

const FreshaIcon = () => (
  <svg className="w-4 h-4 shrink-0 fill-[#EC4899]" viewBox="0 0 24 24">
    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
  </svg>
);

const stats = [
  { value: 14.2, prefix: '$', suffix: 'M+', decimalPlaces: 1, label: 'Inbound Revenue Saved', sub: 'Across 500+ active locations' },
  { value: 342, prefix: '', suffix: 'ms', decimalPlaces: 0, label: 'Median Voice Latency', sub: 'Sub-second response time' },
  { value: 99.9, prefix: '', suffix: '%', decimalPlaces: 1, label: 'Call Answer Rate', sub: 'Zero missed bookings' },
  { value: 250, prefix: '', suffix: 'k+', decimalPlaces: 0, label: 'Live Calls Handled', sub: 'Natural human conversation' },
];

const integrations = [
  { name: 'Square Appointments', type: 'Direct Booking', IconComponent: SquareIcon },
  { name: 'Google Calendar', type: '2-Way Sync', IconComponent: GoogleIcon },
  { name: 'Salesforce & Clio', type: 'CRM Integration', IconComponent: SalesforceIcon },
  { name: 'LiveKit Cloud', type: 'WebRTC Telephony', IconComponent: LiveKitIcon },
  { name: 'Twilio & Telnyx', type: 'Carrier Forwarding', IconComponent: TwilioIcon },
  { name: 'Epic & Dentrix EHR', type: 'Healthcare Sync', IconComponent: HealthcareIcon },
  { name: 'HIPAA & SOC-2', type: 'Security Standard', IconComponent: SecurityIcon },
  { name: 'Fresha & Jane App', type: 'Salons & Clinics', IconComponent: FreshaIcon },
];

export default function TrustStrip() {
  return (
    <section className="py-20 sm:py-24 bg-white border-b border-slate-200/70 relative overflow-hidden">

      {/* Metric Blocks Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 mb-12 sm:mb-16">

        {/* Section Label */}
        <div className="text-center mb-10">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Performance & Reliability
          </p>
        </div>

        {/* 4 Clean Metric Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {stats.map((s, idx) => (
            <ScrollReveal key={idx} y={12} duration={0.4} delay={idx * 0.06}>
              <div className="p-5 sm:p-6 text-center sm:text-left h-full rounded-2xl bg-white border border-slate-200/70 shadow-2xs hover:shadow-xs transition-all">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 mb-1 font-heading">
                  <NumberTicker
                    value={s.value}
                    prefix={s.prefix}
                    suffix={s.suffix}
                    decimalPlaces={s.decimalPlaces}
                  />
                </div>
                <p className="text-xs sm:text-sm font-semibold text-slate-900 font-heading">{s.label}</p>
                <p className="text-xs text-slate-500 mt-0.5">{s.sub}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>

      </div>

      {/* Marquee */}
      <div className="w-full relative overflow-hidden pt-6 pb-2 border-t border-slate-100">

        {/* Edge Fade Masks */}
        <div className="absolute left-0 top-0 bottom-0 w-24 sm:w-40 bg-gradient-to-r from-white via-white/80 to-transparent z-10 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-24 sm:w-40 bg-gradient-to-l from-white via-white/80 to-transparent z-10 pointer-events-none" />

        <div className="text-center mb-4">
          <span className="text-xs font-medium text-slate-400">
            Integrates with leading calendars, CRMs, and telephony infrastructure
          </span>
        </div>

        <Marquee pauseOnHover={true} className="[--duration:35s] [--gap:0.75rem]">
          {integrations.map((item, idx) => {
            const Icon = item.IconComponent;
            return (
              <div
                key={idx}
                className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-slate-50/80 border border-slate-200/70 text-xs font-medium text-slate-800 mx-1 cursor-default group hover:bg-white hover:border-slate-300 transition-all"
              >
                <Icon />
                <span className="font-sans group-hover:text-slate-900 transition-colors">{item.name}</span>
                <span className="text-[11px] text-slate-500 bg-white px-2 py-0.5 rounded-full border border-slate-200/60">
                  {item.type}
                </span>
              </div>
            );
          })}
        </Marquee>

      </div>

    </section>
  );
}


