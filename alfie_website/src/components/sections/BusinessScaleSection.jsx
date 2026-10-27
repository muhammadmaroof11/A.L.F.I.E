import React, { useState } from 'react';
import { 
  Store, 
  Building2, 
  CheckCircle2, 
  Calendar, 
  PhoneCall, 
  ShieldCheck, 
  Layers, 
  ArrowRight, 
  MessageSquare, 
  Zap, 
  Users,
  Database,
  Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import SpotlightCard from '../shared/SpotlightCard';
import { Button } from '../ui/button';

export default function BusinessScaleSection() {
  const [activeTab, setActiveTab] = useState('local'); // 'local' | 'enterprise'

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="business-scale" className="py-24 bg-white text-slate-900 relative overflow-hidden border-b border-slate-200">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Built For Every Scale
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Engineered for solo shops to enterprise networks
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Whether you need a dedicated receptionist while working with clients, or custom SIP telephony routing thousands of simultaneous calls across nationwide location networks.
          </p>

          {/* Smooth Spring Segmented Switcher */}
          <div className="inline-flex p-1.5 rounded-2xl bg-slate-100 border border-slate-200 mt-6 shadow-inner relative">
            <button
              type="button"
              onClick={() => setActiveTab('local')}
              className={`relative z-10 flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-colors cursor-pointer ${
                activeTab === 'local' ? 'text-white' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {activeTab === 'local' && (
                <motion.div
                  layoutId="scaleTabPill"
                  className="absolute inset-0 bg-slate-900 rounded-xl -z-10"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <Store className="w-4 h-4" />
              <span>For Local & Solo Shops</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('enterprise')}
              className={`relative z-10 flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-colors cursor-pointer ${
                activeTab === 'enterprise' ? 'text-white' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {activeTab === 'enterprise' && (
                <motion.div
                  layoutId="scaleTabPill"
                  className="absolute inset-0 bg-slate-900 rounded-xl -z-10"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <Building2 className="w-4 h-4" />
              <span>For Multi-Location & Enterprise</span>
            </button>
          </div>
        </div>

        {/* Bento Grid Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'local' ? (
            <motion.div
              key="local"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-12 gap-6 max-w-6xl mx-auto"
            >
              
              {/* Card 1: Answers When Hands Are Full (7 Cols) */}
              <SpotlightCard className="md:col-span-7 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700">
                      <PhoneCall className="w-5 h-5 animate-pulse" />
                    </div>
                    <span className="text-[11px] font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/30">
                      Ring 1 • 340ms Pickup
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    Answers While Hands Are Busy Cutting Hair or On-Site
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-6">
                    Never lose walk-ins or high-ticket appointments to voicemail. A.L.F.I.E speaks with natural warmth, quotes service pricing, and confirms the appointment in under 20 seconds.
                  </p>

                  {/* Interactive Mini Call Stream Graphic */}
                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5 text-xs font-mono">
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span>SIMULATED CALL STREAM</span>
                      <span className="text-slate-700 font-bold">Square Synced</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-700">
                      <span className="font-bold text-slate-900">Customer:</span>
                      <span>"Hey, can I get a skin fade with Marcus around 4:30 PM today?"</span>
                    </div>
                    <div className="flex items-center gap-2 text-emerald-600 pt-1.5 border-t border-slate-200">
                      <span className="font-bold text-emerald-600">A.L.F.I.E:</span>
                      <span>"Done! Marcus is locked in for 4:30 PM. I’ve texted your confirmation!"</span>
                    </div>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center justify-between text-xs font-semibold text-slate-700">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Zero missed revenue during service hours</span>
                  </span>
                  <span className="text-slate-500 font-mono font-normal">100% Automated</span>
                </div>
              </SpotlightCard>

              {/* Card 2: Direct Calendar Slot Reservation (5 Cols) */}
              <SpotlightCard className="md:col-span-5 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mb-4 shadow-sm">
                    <Calendar className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    Live Calendar Booking
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    Direct 2-way integration with Square Appointments, Fresha, Calendly, and Google Calendar. Validates barber/chair availability in real time.
                  </p>

                  {/* Visual Slot Lock Pills */}
                  <div className="grid grid-cols-2 gap-2 mt-2 font-mono">
                    <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-center text-xs font-bold text-emerald-600 shadow-sm">
                      ✓ 4:30 PM (Marcus)
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-slate-500 line-through">
                      3:00 PM (Booked)
                    </div>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" /> Real-time 2-way calendar lock
                </div>
              </SpotlightCard>

              {/* Card 3: Instant SMS Notification Bubble (5 Cols) */}
              <SpotlightCard className="md:col-span-5 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 mb-4 shadow-sm">
                    <MessageSquare className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    Instant SMS Alerts
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    The customer immediately receives a confirmation text with shop address and parking instructions. Your phone gets a summary alert.
                  </p>

                  <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-xs font-mono text-blue-800">
                    💬 "Your appointment with Marcus is confirmed for today at 4:30 PM at Modern Cuts. Reply RESCHEDULE if needed."
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-blue-600" /> Instant client text notification
                </div>
              </SpotlightCard>

              {/* Card 4: 5-Minute Zero-Hardware Setup (7 Cols) */}
              <SpotlightCard className="md:col-span-7 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-500 mb-4 shadow-sm">
                    <Zap className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    5-Minute Zero-Hardware Setup
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    Keep your existing shop phone number. No apps, no new hardware, no complex contracts. Simply turn on standard conditional call forwarding.
                  </p>

                  <div className="flex flex-wrap items-center gap-2.5 text-xs font-mono pt-2">
                    <span className="px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-slate-700">iPhone / Android Forwarding</span>
                    <span className="text-slate-400">➔</span>
                    <span className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 font-bold">A.L.F.I.E Voice Line</span>
                    <span className="text-slate-400">➔</span>
                    <span className="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">Booked Appointment</span>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center justify-between text-xs font-semibold text-amber-600">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" /> Works with Verizon, AT&T, T-Mobile, VOIP
                  </span>
                  <span className="text-slate-500 font-mono font-normal">No equipment needed</span>
                </div>
              </SpotlightCard>

            </motion.div>
          ) : (
            <motion.div
              key="enterprise"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-12 gap-6 max-w-6xl mx-auto"
            >
              
              {/* Enterprise Card 1: 5,000+ Concurrent Lines (7 Cols) */}
              <SpotlightCard className="md:col-span-7 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700">
                      <Radio className="w-5 h-5 animate-pulse" />
                    </div>
                    <span className="text-[11px] font-mono font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                      5,000+ Simultaneous Calls
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    Massive Telephony Concurrency with Zero Hold Times
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    Eliminate busy signals and dropped queues during marketing surges or emergency peaks. Cloud WebRTC and SIP scaling handles multi-regional intake across hundreds of branch locations.
                  </p>

                  {/* Simulated Concurrency Wave Indicator */}
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <div className="text-xs font-mono">
                      <span className="text-slate-500 block text-[10px]">LIVE CONCURRENCY CHANNELS</span>
                      <span className="font-bold text-slate-900 text-sm">5,420 Active Channels</span>
                    </div>
                    <div className="flex items-center gap-1 h-8">
                      {[30, 60, 45, 80, 65, 90, 75, 40, 85, 70, 95, 55].map((h, i) => (
                        <div key={i} className="w-1.5 bg-slate-400 rounded-full animate-pulse" style={{ height: `${h * 0.3}px` }} />
                      ))}
                    </div>
                    <span className="text-[11px] font-mono font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                      99.99% SLA
                    </span>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Unlimited scaling with Bring-Your-Own-Carrier (BYOC)</span>
                </div>
              </SpotlightCard>

              {/* Enterprise Card 2: HIPAA & SOC-2 Compliant (5 Cols) */}
              <SpotlightCard className="md:col-span-5 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mb-4 shadow-sm">
                    <ShieldCheck className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    HIPAA & SOC-2 Certified
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    Signed Business Associate Agreements (BAAs), end-to-end DTLS/SRTP audio encryption, and zero-data-retention options for healthcare and legal security standards.
                  </p>

                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
                      ✓ Signed BAA
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-slate-50 text-slate-600 border border-slate-200 font-bold">
                      AES-256 GCM
                    </span>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" /> Certified healthcare & enterprise grade
                </div>
              </SpotlightCard>

              {/* Enterprise Card 3: Deep EHR & CRM Pipeline (5 Cols) */}
              <SpotlightCard className="md:col-span-5 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 mb-4 shadow-sm">
                    <Database className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    EHR & CRM Deep Sync
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    Native bidirectional synchronization with Epic Systems, AthenaHealth, Dentrix, Salesforce, Clio, and custom REST webhook endpoints.
                  </p>

                  <div className="text-xs font-mono text-slate-600 space-y-1">
                    <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="text-slate-900">Epic EHR Connector</span>
                      <span className="text-emerald-600 font-bold">Sync &lt;65ms</span>
                    </div>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                  <CheckCircle2 className="w-4 h-4" /> Real-time structured data payload
                </div>
              </SpotlightCard>

              {/* Enterprise Card 4: Live Warm Transfer with Brief (7 Cols) */}
              <SpotlightCard className="md:col-span-7 p-7 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600 mb-4 shadow-sm">
                    <Users className="w-5 h-5" />
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 font-heading mb-2">
                    Intelligent Warm Human Transfer with Mobile Brief
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                    When high-priority inquiries or emergency cases are detected, A.L.F.I.E automatically texts a structured case brief to the on-call specialist 1 second before bridging the live call.
                  </p>

                  <div className="p-3.5 rounded-xl bg-purple-50 border border-purple-200 text-xs font-mono text-purple-800">
                    ⚡ Live Transfer: Accident triage completed. Pre-brief sent to Partner cell phone. Call bridging immediately...
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-200 flex items-center justify-between text-xs font-semibold text-purple-700">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-purple-600" /> Zero customer repetition on transfer
                  </span>
                  <span className="text-slate-500 font-mono font-normal">Ghost whisper supported</span>
                </div>
              </SpotlightCard>

            </motion.div>
          )}
        </AnimatePresence>

        {/* Quick Link to Sandbox Bottom */}
        <div className="text-center mt-12">
          <Button
            variant="outline"
            size="lg"
            onClick={() => scrollTo('demo-arena')}
            className="gap-2 text-xs font-bold border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-slate-900"
          >
            <span>Experience the Live Voice Sandbox</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
          </Button>
        </div>

      </div>
    </section>
  );
}
