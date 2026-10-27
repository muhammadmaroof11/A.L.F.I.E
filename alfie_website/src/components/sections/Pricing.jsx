import React, { useState } from 'react';
import { Check, ShieldCheck, Zap, Radio } from 'lucide-react';
import { motion } from 'motion/react';
import ScrollReveal from '../shared/ScrollReveal';
import SpotlightCard from '../shared/SpotlightCard';
import { BorderBeam } from '../ui/border-beam';
import { Button } from '../ui/button';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '../ui/accordion';

const tiers = [
  {
    name: 'Starter / Local Practice',
    badge: 'FOR SOLO & LOCAL OPERATORS',
    monthlyPrice: 99,
    annualPrice: 79,
    usage: '+ $0.14/min after included time',
    desc: 'Ideal for solo practices, boutique medical clinics, local law offices, and service businesses.',
    popular: false,
    features: [
      '200 Included Active Voice Minutes',
      '24/7 Inbound Answering (<360ms TTFT)',
      'Square & Google Calendar Booking Sync',
      'Instant SMS Confirmation to Client & Owner',
      'Works with Your Existing Phone Number',
      'Full Call Recordings & Transcripts'
    ],
    buttonText: 'Start with Starter',
    buttonVariant: 'outline'
  },
  {
    name: 'Growth / Busy Practice',
    badge: 'MOST POPULAR',
    monthlyPrice: 299,
    annualPrice: 239,
    usage: '+ $0.12/min after included time',
    desc: 'For growing clinics, scaling practices, and law offices.',
    popular: true,
    features: [
      '800 Included Active Voice Minutes',
      'Live Warm Phone Transfer to Your Cell',
      'Custom CRM Sync (Clio, Dentrix, HubSpot)',
      'Automated SMS Deposit & Retainer Links',
      'Multiple Industry Voice Personas',
      'Priority Telephony Audio Queue'
    ],
    buttonText: 'Start Growth Plan',
    buttonVariant: 'default'
  },
  {
    name: 'Enterprise & Scale',
    badge: 'CUSTOM INFRASTRUCTURE',
    monthlyPrice: 'Custom',
    annualPrice: 'Custom',
    usage: 'Volume-tiered minute discounts',
    desc: 'For multi-location franchises, healthcare networks, and enterprise call centers.',
    popular: false,
    features: [
      'Unlimited Concurrent Calls (5,000+ Lines)',
      'Dedicated SIP Trunking & BYOC Support',
      'Signed HIPAA / BAA & SOC-2 Security SLA',
      'Custom Voice Cloning & Tone Engineering',
      'Direct EHR & Database Custom Adapters',
      'Dedicated Solutions Engineer on Slack'
    ],
    buttonText: 'Contact Enterprise Sales',
    buttonVariant: 'outline'
  }
];

const faqs = [
  {
    q: 'Can I use A.L.F.I.E for my local business or practice?',
    a: 'Yes! A.L.F.I.E was purpose-built for busy operators. When your team is busy attending to clients or patients, A.L.F.I.E answers your line on ring 1, quotes details, checks your calendar, and books the appointment in seconds.'
  },
  {
    q: 'Can I keep my existing business phone number?',
    a: 'Yes. You do not need to change phone numbers or buy any new hardware. You simply turn on standard call forwarding from your iPhone, Android, or carrier to your dedicated A.L.F.I.E voice line.'
  },
  {
    q: 'Can A.L.F.I.E transfer urgent callers directly to my personal cell phone?',
    a: 'Yes. For high-priority inquiries or emergency callers, A.L.F.I.E sends you a structured summary text 1 second before executing a live warm phone transfer directly to your mobile phone.'
  },
  {
    q: 'Is enterprise patient and client data HIPAA & SOC-2 compliant?',
    a: 'Yes. A.L.F.I.E offers zero-data-retention options and executes formal Business Associate Agreements (BAAs) for healthcare systems, law practices, and enterprise organizations.'
  }
];

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="pricing" className="py-24 bg-white text-slate-900 relative overflow-hidden border-b border-slate-200">
      
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-6xl h-[600px] bg-slate-100/50 rounded-full blur-3xl pointer-events-none opacity-30" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Predictable Pricing
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Simple plans for every stage
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            From solo practice owners to national enterprise networks. Zero hidden fees, cancel anytime.
          </p>

          {/* Billing Interval Switcher */}
          <div className="flex items-center justify-center gap-3.5 pt-6 font-mono">
            <span className={`text-xs font-bold transition-colors ${!isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>
              Monthly Billing
            </span>

            <button
              type="button"
              onClick={() => setIsAnnual(!isAnnual)}
              className="w-13 h-7 rounded-full bg-slate-200 border border-white/10 p-1 transition-colors relative cursor-pointer"
            >
              <motion.div 
                className="w-5 h-5 rounded-full bg-slate-900"
                animate={{ x: isAnnual ? 24 : 0 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>

            <span className={`text-xs font-bold flex items-center gap-2 transition-colors ${isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>
              <span>Annual Billing</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                Save 20%
              </span>
            </span>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto items-stretch">
          {tiers.map((tier, idx) => {
            const price = typeof tier.monthlyPrice === 'number' 
              ? (isAnnual ? tier.annualPrice : tier.monthlyPrice) 
              : tier.monthlyPrice;

            return (
              <ScrollReveal key={tier.name} y={20} duration={0.5} delay={idx * 0.1}>
                <SpotlightCard 
                  className={`h-full p-8 flex flex-col justify-between relative ${
                    tier.popular 
                      ? 'border-slate-900 ring-1 ring-slate-900/20 shadow-sm shadow-slate-900/10' 
                      : 'border-white/10'
                  }`}
                  spotlightColor={tier.popular ? "rgba(0, 240, 255, 0.15)" : "rgba(0, 240, 255, 0.08)"}
                >
                  {/* Glowing BorderBeam on popular tier */}
                  {tier.popular && (
                    <BorderBeam size={180} duration={10} colorFrom="#94a3b8" colorTo="#cbd5e1" />
                  )}

                  <div>
                    {/* Badge */}
                    <div className="flex items-center justify-between gap-2 mb-4">
                      <span className={`text-[10px] font-mono font-extrabold uppercase tracking-wider px-2.5 py-1 rounded-full ${
                        tier.popular 
                          ? 'bg-slate-900 text-white' 
                          : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}>
                        {tier.badge}
                      </span>
                    </div>

                    <h3 className="text-xl font-bold text-slate-900 font-heading">
                      {tier.name}
                    </h3>
                    
                    <p className="text-xs text-slate-500 mt-2 min-h-8 leading-relaxed">
                      {tier.desc}
                    </p>

                    {/* Price Block */}
                    <div className="my-6 pb-6 border-b border-slate-200">
                      <div className="flex items-baseline gap-1.5">
                        {typeof price === 'number' ? (
                          <>
                            <span className="text-4xl sm:text-5xl font-extrabold text-slate-900 font-heading font-mono">
                              ${price}
                            </span>
                            <span className="text-xs text-slate-500 font-mono font-medium">/ month</span>
                          </>
                        ) : (
                          <span className="text-3xl font-extrabold text-slate-900 font-heading font-mono">
                            {price}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500 mt-1.5 font-mono">
                        {tier.usage}
                      </p>
                    </div>

                    {/* Features */}
                    <div className="space-y-3 text-xs mb-8">
                      {tier.features.map((feat, i) => (
                        <div key={i} className="flex items-start gap-2.5 text-slate-600">
                          <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Button */}
                  <div>
                    <Button
                      variant={tier.buttonVariant}
                      className="w-full text-xs font-bold py-5 shadow-sm cursor-pointer"
                      onClick={() => scrollTo('demo-arena')}
                    >
                      {tier.buttonText}
                    </Button>
                  </div>

                </SpotlightCard>
              </ScrollReveal>
            );
          })}
        </div>

        {/* Enterprise Security Banner */}
        <div className="max-w-4xl mx-auto mt-14 p-6 rounded-3xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-slate-600 flex items-center justify-center shrink-0 shadow-cyan-glow">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span className="text-slate-600 font-medium leading-relaxed">
              Need custom telephony compliance, dedicated SIP trunking, or signed Business Associate Agreements?
            </span>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => scrollTo('demo-arena')}
            className="shrink-0 text-xs font-bold border-slate-300 text-slate-600 hover:text-slate-900"
          >
            Talk to Telephony Lead
          </Button>
        </div>

        {/* FAQ Accordion Section */}
        <div className="max-w-3xl mx-auto mt-20">
          <div className="text-center mb-10 space-y-2">
            <h3 className="text-2xl font-extrabold text-slate-900 font-heading">
              Frequently Answered Questions
            </h3>
            <p className="text-xs text-slate-500">
              Everything you need to know about deploying A.L.F.I.E for your business.
            </p>
          </div>

          <Accordion type="single" collapsible className="space-y-3">
            {faqs.map((faq, index) => (
              <AccordionItem 
                key={index} 
                value={`item-${index}`}
                className="bg-white border border-slate-200 rounded-2xl px-5 overflow-hidden transition-all shadow-sm hover:border-slate-300"
              >
                <AccordionTrigger className="text-left text-xs sm:text-sm font-bold text-slate-900 py-4.5 hover:no-underline cursor-pointer font-heading">
                  {faq.q}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-slate-600 pb-4 leading-relaxed">
                  {faq.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

      </div>
    </section>
  );
}
