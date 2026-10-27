import React from 'react';
import { 
  Scale, Shield, PhoneCall, ArrowRight, Lock, 
  FileText, Clock, Smartphone, UserCheck, Check
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import BeforeAfterAudioPlayer from '../components/ui/BeforeAfterAudioPlayer';

export default function LawFirmsPage() {
  const scrollToReality = () => {
    const el = document.getElementById('firm-reality');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  const scrollToDemo = scrollToReality;

  const legalAudioTracks = {
    legacy: {
      title: 'Traditional Answering Service Ticket',
      subtitle: '4 Rings • Generic Message Service • 48-Hour Delay',
      transcript: '"You have reached the answering service for Sterling & Partners. Our office is closed for the weekend. I can take down your phone number and someone will review your inquiry in 24 to 48 business hours..." [Severely injured driver hangs up and calls TV billboard attorney]',
      impact: 'Lost $120,000 catastrophic commercial truck case to competing billboard firm',
      latency: '24-48 hour response callback',
    },
    alfie: {
      title: 'A.L.F.I.E. Autonomous Legal Intake Specialist',
      subtitle: 'First Ring Pickup • Liability Merit Score • 10-Second Warm Transfer',
      transcript: '"Mr. Davis, I understand completely. Because the commercial truck driver ran the red light and police cited him at the scene, liability is clear. I have already sent a case summary to Attorney Sterling\'s personal cell, and I am connecting you to him directly right now."',
      impact: '100% Retainer Locked • Brief Delivered to Attorney Phone • Transfer Connected',
      latency: 'Sub-45ms statute of limitations check',
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-amber-500 selection:text-white relative">
      <Navbar onOpenDemo={scrollToDemo} />

      <main className="pt-14 sm:pt-16">
        {/* ── Hero Section ── */}
        <section className="relative overflow-hidden w-full lg:min-h-[calc(100vh-3.5rem)] lg:max-h-[calc(100vh-3.5rem)] flex items-center bg-white border-b border-slate-200/80 py-8 lg:py-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full py-2">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
              
              {/* Left Column */}
              <div className="lg:col-span-7 space-y-4">
                <h1 className="text-3xl sm:text-4xl lg:text-[2.6rem] xl:text-[2.9rem] font-extrabold tracking-tight text-slate-900 leading-[1.1] font-heading">
                  Never Miss a{' '}
                  <span className="text-amber-600">
                    $50,000+ Retainer
                  </span>{' '}
                  to an Answering Service.
                </h1>

                <p className="text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Elena Vance triages accident liability, verifies statutes of limitations in milliseconds, and warm-bridges high-value claims straight to partner cell phones 24/7.
                </p>

                {/* Proof Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono">
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-amber-600">&lt; 45ms</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Statute Check</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">100%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">After-Hours Capture</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">$45k+</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Avg Retainer Filter</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">0s</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Hold Time</div>
                  </div>
                </div>

                {/* Primary CTAs */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    onClick={scrollToReality}
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-all text-xs"
                  >
                    <PhoneCall className="w-4 h-4 text-white" />
                    <span>See the Intake Reality</span>
                    <ArrowRight className="w-4 h-4 text-white/80" />
                  </button>

                  <a
                    href="#firm-reality"
                    className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all flex items-center gap-2"
                  >
                    <Lock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Why Firms Bleed Retainers</span>
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
                    poster="/assets/posters/law_avatar.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/robot_avatars/law_avatar.webm" type="video/webm" />
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
              <span className="text-xs font-bold text-amber-600 uppercase tracking-widest font-mono">Auditory Comparison</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Listen: Generic Answering Service vs. Warm Attorney Bridge
              </h2>
              <p className="text-sm text-slate-600">
                Catastrophic accident victims want instant empathy and certainty, not a generic answering service ticket.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Interactive Player */}
              <div className="lg:col-span-7">
                <BeforeAfterAudioPlayer 
                  customTracks={legalAudioTracks}
                  title="Personal Injury Intake Triage"
                  subtitle="Live Case Audio Simulation"
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
                    poster="/assets/posters/law.jpg"
                    className="w-full h-full object-cover pointer-events-none"
                  >
                    <source src="/assets/industry_videos/law_firms/law.webm" type="video/webm" />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end p-5">
                    <div>
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/90 text-white text-[10px] font-mono font-bold mb-1">
                        <Check className="w-3 h-3" />
                        <span>High-Value Retainer Filter Active</span>
                      </div>
                      <p className="text-xs font-semibold text-white">
                        Direct Bi-Directional Clio & Filevine Case Creation
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">CASE MERIT</span>
                    <span className="font-bold text-slate-900">Commercial Carrier T-Bone</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">WARM BRIDGE</span>
                    <span className="font-bold text-amber-600">Partner Mobile (10s)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Deterministic Legal Tool Pipeline (Interactive Badges) ── */}
        <section className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
              <span className="text-xs font-bold text-amber-600 uppercase tracking-widest font-mono">Case Intake Logic</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Deterministic Legal Intake Pipeline
              </h2>
              <p className="text-sm text-slate-600">
                Rigorous multi-layer triage ensuring zero conflict of interest and instant escalation for high-liability cases.
              </p>
            </div>

            {/* 4 Interactive Visual Step Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-amber-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  01
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Accident Merit & Liability</h3>
                <p className="text-xs text-slate-500 mb-3">Checks police report presence & opposing driver fault.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-amber-700 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>Clear Liability (Red Light Citation)</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-amber-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  02
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Statute of Limitations</h3>
                <p className="text-xs text-slate-500 mb-3">Calculates jurisdiction time limit against date of loss.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>Incident Date: 14 Days Ago (Active)</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-amber-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  03
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Partner SMS Case Brief</h3>
                <p className="text-xs text-slate-500 mb-3">Transmits 1-line casualty summary to managing attorney.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>SMS Brief Sent 2s Before Ring</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-amber-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  04
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Direct Warm Bridge</h3>
                <p className="text-xs text-slate-500 mb-3">Executes SIP telephony bridge to attorney personal cell.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>Partner Connected (0s Drop)</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pain Point Education: The Silent Revenue Leak in Modern Legal Intake ── */}
        <section id="firm-reality" className="py-20 bg-slate-50/70 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
              <span className="text-xs font-bold text-amber-600 uppercase tracking-widest font-mono">
                The Reality of Modern Legal Intake
              </span>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-900 font-heading tracking-tight">
                Why 80% of High-Value Accident Victims Never Leave a Voicemail
              </h2>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                When a catastrophic injury occurs, victims and their families want immediate human certainty. If your phone rings to voicemail or a generic answering service, they hang up and retain the competitor on the billboard.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
              
              {/* Left Column: Real Law Firm Atmosphere & Financial Reality Card */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="rounded-3xl overflow-hidden border border-slate-200 shadow-md relative h-72 sm:h-80 group">
                  <img
                    src="/assets/industry_photos/law_firms/law.webp"
                    alt="Law firm busy intake operations"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/20 to-transparent flex items-end p-6">
                    <div className="space-y-1">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-amber-300 block">
                        Friday 7:15 PM • Post-Hours Reality
                      </span>
                      <p className="text-sm font-medium text-white/95 leading-snug">
                        Your intake paralegals leave at 5:00 PM. Catastrophic highway collisions happen on weekends.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mathematical Bleed Reality Card */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-mono font-bold text-slate-500 uppercase">Average Retainer Bleed</span>
                    <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                      - $120,000 / Missed Claim
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Personal injury claims are won or lost in the first 15 minutes after an accident. If your phone isn't answered with authoritative empathy on the first ring, that client never calls back.
                  </p>
                  <div className="grid grid-cols-2 gap-3 pt-2 text-center font-mono">
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-rose-600 block">85%</span>
                      <span className="text-[10px] text-slate-500">Hang up on voicemail</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-emerald-600 block">&lt; 10s</span>
                      <span className="text-[10px] text-slate-500">A.L.F.I.E. partner bridge</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: The 3 Core Pain Points & How A.L.F.I.E. Eliminates Them */}
              <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
                
                {/* Pain Point 1 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-amber-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-rose-100">
                      01
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      The "Call-Back Later" Trap Destroys High-Value Retainers
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    An injured caller sitting in an emergency room will not wait for Monday morning. When an automated machine or answering service says <em>"Someone will review your inquiry in 24 to 48 business hours,"</em> they instantly dial the next firm on Google. That single missed call costs your firm six figures in contingency fees.
                  </p>
                </div>

                {/* Pain Point 2 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-amber-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-amber-100">
                      02
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Generic Answering Services Misspell Names & Miss Merits
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    Third-party call centers employ minimum-wage agents handling calls for plumbers, florists, and roofers simultaneously. They don't know tort liability, cannot calculate statutes of limitations, and cannot identify a commercial policy claim worth $500,000.
                  </p>
                </div>

                {/* Pain Point 3 & Resolution */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-amber-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      03
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      How A.L.F.I.E. Solves This Without Adding Staff
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    A.L.F.I.E. acts as your firm's tireless intake gatekeeper. It answers on ring one, conducts an empathetic, rigorous liability triage, verifies the police report presence, logs the case directly into Clio or Filevine, and warm-bridges high-value catastrophic claims straight to your cell phone within 10 seconds.
                  </p>
                </div>

                {/* Reassurance Banner */}
                <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="space-y-0.5 text-center sm:text-left">
                    <h4 className="text-xs font-bold text-amber-900 font-mono uppercase">Zero Software Fatigue for Your Staff</h4>
                    <p className="text-xs text-amber-800/90">A.L.F.I.E. works silently behind your current phone numbers and CRM. Zero new apps to learn.</p>
                  </div>
                  <a
                    href="mailto:contact@alfie.ai?subject=Law%20Firm%20Intake%20Consultation"
                    className="shrink-0 bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-xl text-xs shadow-xs transition-all"
                  >
                    Schedule Firm Walkthrough
                  </a>
                </div>

              </div>

            </div>
          </div>
        </section>

        {/* ── Legal CRM Integrations Strip ── */}
        <section className="py-16 bg-white border-t border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center space-y-6">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 font-mono">
                Native Bi-Directional Legal Practice Management Integrations
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 text-slate-700 text-sm font-semibold">
                <span className="hover:text-amber-600 transition-colors">Clio Manage & Grow</span>
                <span className="hover:text-amber-600 transition-colors">Filevine</span>
                <span className="hover:text-amber-600 transition-colors">Smokeball</span>
                <span className="hover:text-amber-600 transition-colors">MyCase</span>
                <span className="hover:text-amber-600 transition-colors">Lead Docket</span>
                <span className="hover:text-amber-600 transition-colors">DocuSign Retainers</span>
              </div>
              <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed font-mono">
                SOC-2 Type II Certified & Attorney-Client Privilege Protected. Full cryptographic end-to-end audio encryption with zero plain-text retention of privileged conversations.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
