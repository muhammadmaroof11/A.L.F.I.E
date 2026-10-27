import React from 'react';
import { 
  Stethoscope, Shield, PhoneCall, CheckCircle, ArrowRight, Lock, 
  Sparkles, Zap, Activity, Clock, FileCheck, Check
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import BeforeAfterAudioPlayer from '../components/ui/BeforeAfterAudioPlayer';

export default function ClinicsPage() {
  const scrollToReality = () => {
    const el = document.getElementById('clinic-reality');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  const scrollToDemo = scrollToReality;

  const clinicAudioTracks = {
    legacy: {
      title: 'Traditional Front Desk Hold Queue',
      subtitle: '4 Rings • 8-Minute Hold Queue • Patient Drop-Off',
      transcript: '"Thank you for calling Miller Family Dental. All our staff are currently helping other patients or on the phone. Your call is number 7 in line. Please hold..." [Patient hangs up after 4 minutes]',
      impact: 'Lost $1,800 crown procedure to competing clinic down the road',
      latency: '8+ min hold time',
    },
    alfie: {
      title: 'A.L.F.I.E. Practice Voice Node',
      subtitle: '1st Ring Pickup • 65ms Payer Check • Instant EMR Slot Lock',
      transcript: '"Good morning Michael! Yes, Dr. Miller is in-network with your Delta Dental Premier PPO. I see a cancellation today at 2:30 PM in Operatory 3. I have confirmed your appointment and texted your pre-op prep."',
      impact: 'Zero Hold Time • $1,800 Production Saved • Calendar Locked',
      latency: '65ms eligibility lookup',
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-cyan-500 selection:text-white relative">
      <Navbar onOpenDemo={scrollToDemo} />

      <main className="pt-14 sm:pt-16">
        {/* ── Hero Section ── */}
        <section className="relative overflow-hidden w-full lg:min-h-[calc(100vh-3.5rem)] lg:max-h-[calc(100vh-3.5rem)] flex items-center bg-white border-b border-slate-200/80 py-8 lg:py-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full py-2">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">

              {/* Left Column */}
              <div className="lg:col-span-7 space-y-4">
                <h1 className="text-3xl sm:text-4xl lg:text-[2.6rem] xl:text-[2.9rem] font-extrabold tracking-tight text-slate-900 leading-[1.1] font-heading">
                  Zero Missed Patients.{' '}
                  <span className="text-[#008BC5]">
                    Instant Insurance Validation
                  </span>{' '}
                  & Direct EMR Booking.
                </h1>

                <p className="text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Sarah validates PPO eligibility in 65ms, schedules doctor operatory chairs directly in Dentrix or Epic EMR, and dispatches pre-op SMS instructions 24/7.
                </p>

                {/* Proof Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono">
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-cyan-600">65ms</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Insurance Lookup</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">99.4%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Call Capture Rate</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">-42%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">No-Show Rate</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-cyan-600">0s</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Patient Hold Time</div>
                  </div>
                </div>

                {/* CTAs */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    onClick={scrollToReality}
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-all text-xs"
                  >
                    <PhoneCall className="w-4 h-4 text-white" />
                    <span>See the Practice Reality</span>
                    <ArrowRight className="w-4 h-4 text-white/80" />
                  </button>

                  <a
                    href="#clinic-reality"
                    className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all flex items-center gap-2"
                  >
                    <Lock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Why Clinics Lose Patients</span>
                  </a>
                </div>
              </div>

              {/* Right Column: Prominent 3D Robot Avatar Video (Single Focused Asset) */}
              <div className="lg:col-span-5 flex justify-center lg:justify-end">
                <div className="rounded-3xl overflow-hidden bg-slate-900/5 border border-slate-200 shadow-xl relative w-full max-w-[460px] aspect-[4/3] flex items-center justify-center p-2 group hover:shadow-2xl transition-all duration-300">
                  <video 
                    autoPlay 
                    loop 
                    muted 
                    playsInline 
                    poster="/assets/posters/clinic_avatar_2.jpg" 
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/robot_avatars/clinic_avatar_2.webm" type="video/webm" />
                  </video>
                </div>
              </div>

            </div>
          </div>
        </section>

        {/* ── Interactive Audio Experience: Hear the Difference ── */}
        <section className="py-16 sm:py-20 bg-slate-50/60 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-10 space-y-2">
              <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest font-mono">Auditory Comparison</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Listen: Hold Music vs. Instant Chair Booking
              </h2>
              <p className="text-sm text-slate-600">
                Switch between traditional front desk triage and A.L.F.I.E. to experience the patient journey firsthand.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Interactive Player */}
              <div className="lg:col-span-7">
                <BeforeAfterAudioPlayer 
                  customTracks={clinicAudioTracks}
                  title="Clinical Call Experience Triage"
                  subtitle="Live Audio Simulation"
                />
              </div>

              {/* Side Video Preview Card */}
              <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-xs">
                <div className="relative aspect-video overflow-hidden">
                  <video 
                    autoPlay 
                    loop 
                    muted 
                    playsInline 
                    poster="/assets/posters/doctor.jpg"
                    className="w-full h-full object-cover pointer-events-none"
                  >
                    <source src="/assets/industry_videos/clinics/doctor.webm" type="video/webm" />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end p-5">
                    <div>
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/90 text-white text-[10px] font-mono font-bold mb-1">
                        <Check className="w-3 h-3" />
                        <span>Direct EMR Write-Back Active</span>
                      </div>
                      <p className="text-xs font-semibold text-white">
                        Synchronized with Dentrix Ascend & Epic MyChart
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">VERIFIED PAYER</span>
                    <span className="font-bold text-slate-900">Delta Dental PPO</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">SLOT LOCK</span>
                    <span className="font-bold text-emerald-600">Chair 3 (Today 2:30 PM)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Deterministic Healthcare Tool Pipeline (Interactive Badges) ── */}
        <section className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
              <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest font-mono">Deterministic Telephony</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Real-Time Clinical Tool Execution Pipeline
              </h2>
              <p className="text-sm text-slate-600">
                Every call triggers deterministic API calls with zero hallucination risk and sub-100ms response windows.
              </p>
            </div>

            {/* 4 Interactive Visual Step Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  01
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Payer Network Check</h3>
                <p className="text-xs text-slate-500 mb-3">Queries live provider eligibility clearinghouse.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-cyan-700 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>Delta Dental: Tier 1 Active</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  02
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Operatory Calendar</h3>
                <p className="text-xs text-slate-500 mb-3">Checks doctor chair status & procedure buffers.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                  <span>Dr. Miller: Chair 3 Open</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  03
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">EMR Appointment Lock</h3>
                <p className="text-xs text-slate-500 mb-3">Writes patient ID & slot directly to Dentrix/Epic.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <FileCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Slot #892 Confirmed</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  04
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Pre-Op SMS Dispatch</h3>
                <p className="text-xs text-slate-500 mb-3">Sends calendar invite, directions, and fasting rules.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                  <span>SMS Sent with Gate PIN</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pain Point Education: The Front-Desk Tug of War ── */}
        <section id="clinic-reality" className="py-20 bg-slate-50/70 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
              <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest font-mono">
                The Reality of Modern Practice Operations
              </span>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-900 font-heading tracking-tight">
                The Front-Desk Tug of War: When Ringing Phones Cost You New Patients
              </h2>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                Your receptionist cannot give warm, 5-star attention to the patient checking in at the desk while simultaneously answering a ringing line. When patients wait on hold music, they hang up and book the clinic down the road.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
              
              {/* Left Column: Real Clinic Environment & Financial Reality Card */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="rounded-3xl overflow-hidden border border-slate-200 shadow-md relative h-72 sm:h-80 group">
                  <img
                    src="/assets/industry_photos/clinics/niche_clinic_consult.webp"
                    alt="Clinical practice front desk and consultation room"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/20 to-transparent flex items-end p-6">
                    <div className="space-y-1">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-300 block">
                        Tuesday 10:15 AM • Front-Desk Reality
                      </span>
                      <p className="text-sm font-medium text-white/95 leading-snug">
                        2 patients waiting to check in, 1 paying a co-pay, and an insurance rep on hold. The phone rings 4 times.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mathematical Bleed Reality Card */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-mono font-bold text-slate-500 uppercase">Average Patient Lifetime Bleed</span>
                    <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                      - $4,200 / Missed Call
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    High-value restorative, implant, and aesthetic procedures begin with a single phone inquiry. If that call hits hold music or voicemail, 60% of new patients immediately dial the next clinic.
                  </p>
                  <div className="grid grid-cols-2 gap-3 pt-2 text-center font-mono">
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-rose-600 block">62%</span>
                      <span className="text-[10px] text-slate-500">Hang up after 45s hold</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-emerald-600 block">0s</span>
                      <span className="text-[10px] text-slate-500">A.L.F.I.E. chair lock</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: The 3 Core Practice Pain Points & How A.L.F.I.E. Eliminates Them */}
              <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
                
                {/* Pain Point 1 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-rose-100">
                      01
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Hold Music Drives High-Value Patients Straight to Competitors
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    When a patient with an urgent toothache or cosmetic interest calls, they expect immediate guidance. Putting them on hold behind three in-office check-ins leads to instant drop-off. In under two minutes, they have booked an exam with a competing clinic.
                  </p>
                </div>

                {/* Pain Point 2 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-cyan-100">
                      02
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Staff Burnout from Divided Attention at Reception
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    Front desk coordinators are frequently overwhelmed handling treatment plans, collecting deductibles, and answering routine questions. Forcing them to triage incoming calls leads to billing errors, unreturned messages, and staff burnout.
                  </p>
                </div>

                {/* Pain Point 3 & Resolution */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      03
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      How A.L.F.I.E. Protects the Practice Silently
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    A.L.F.I.E. acts as an autonomous clinical coordinator. It answers on ring one, checks insurance in-network eligibility, looks up operatory chairs directly in Dentrix or Epic, reserves the slot, and sends pre-op preparation texts—freeing your staff to focus 100% on patients in the room.
                  </p>
                </div>

                {/* Reassurance Banner */}
                <div className="p-5 rounded-2xl bg-cyan-50/70 border border-cyan-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="space-y-0.5 text-center sm:text-left">
                    <h4 className="text-xs font-bold text-cyan-950 font-mono uppercase">100% HIPAA & BAA Compliant</h4>
                    <p className="text-xs text-cyan-900/80">No plain-text PHI storage. Seamless integration with your existing telephony and EMR.</p>
                  </div>
                  <a
                    href="mailto:contact@alfie.ai?subject=Clinical%20Practice%20Consultation"
                    className="shrink-0 bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-xl text-xs shadow-xs transition-all"
                  >
                    Schedule Practice Walkthrough
                  </a>
                </div>

              </div>

            </div>
          </div>
        </section>

        {/* ── Integrations & HIPAA Strip ── */}
        <section className="py-16 bg-white border-t border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center space-y-6">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 font-mono">
                Native Bi-Directional EMR & Practice Management Integrations
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 text-slate-700 text-sm font-semibold">
                <span className="hover:text-cyan-600 transition-colors">Dentrix Ascend</span>
                <span className="hover:text-cyan-600 transition-colors">Epic Systems</span>
                <span className="hover:text-cyan-600 transition-colors">AthenaHealth</span>
                <span className="hover:text-cyan-600 transition-colors">NexHealth</span>
                <span className="hover:text-cyan-600 transition-colors">Cerner / Oracle Health</span>
                <span className="hover:text-cyan-600 transition-colors">Kareo Clinical</span>
              </div>
              <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed font-mono">
                HIPAA Compliant & BAA Ready. Ephemeral voice processing with zero raw PHI stored in plain text. Automated redacting of SSNs and payment cards before storage.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
