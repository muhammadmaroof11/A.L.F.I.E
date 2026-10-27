import React from 'react';
import { 
  Building2, Shield, PhoneCall, ArrowRight, Lock, 
  Search, CheckSquare, Calendar, KeyRound, Check
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import BeforeAfterAudioPlayer from '../components/ui/BeforeAfterAudioPlayer';

export default function RealEstatePage() {
  const scrollToReality = () => {
    const el = document.getElementById('realty-reality');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  const scrollToDemo = scrollToReality;

  const realEstateAudioTracks = {
    legacy: {
      title: 'Busy Agent Voicemail on Yard Sign Lead',
      subtitle: '4 Rings • Agent in Closing • Unanswered Sign Call',
      transcript: '"Hi, you have reached Marcus with Prestige Properties. I am currently touring with clients or at a closing. Please leave your name, phone number, and property address after the tone..." [Curbside buyer drives away to next open house]',
      impact: 'Lost $1,450,000 listing transaction to competing neighborhood broker',
      latency: '3 to 5-hour delayed callback',
    },
    alfie: {
      title: 'A.L.F.I.E. Autonomous Realty Concierge',
      subtitle: 'First Ring Pickup • MLS Database Query • Showing Locked in Calendar',
      transcript: '"Hello! Thank you for calling about 742 Evergreen Terrace. This is a 4-bedroom, 3.5-bath modern colonial listed at $1,450,000. It features an open chef\'s kitchen and heated pool. Are you looking to purchase with pre-approved financing or cash? Great! I have booked your private tour for Thursday at 4:00 PM and texted the gate code."',
      impact: 'Secured Pre-Qualified VIP Tour • Gate Code Delivered • Synced to Follow Up Boss',
      latency: 'Sub-80ms MLS inventory check',
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
                  Turn Yard Signs & Portals into{' '}
                  <span className="text-[#008BC5]">
                    Booked VIP Showings
                  </span>{' '}
                  in 15 Seconds.
                </h1>

                <p className="text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Marcus Sterling answers sign calls instantly, validates buyer pre-approval financing, filters unvetted inquiries, and books private showings into your calendar 24/7.
                </p>

                {/* Proof Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono">
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-cyan-600">3.8x</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Showing Conversion</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">&lt; 80ms</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Live MLS IDX Query</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">100%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Sign & Zillow Pickup</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">$0</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Wasted Ad Spend</div>
                  </div>
                </div>

                {/* Primary CTAs */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    onClick={scrollToReality}
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-all text-xs"
                  >
                    <PhoneCall className="w-4 h-4 text-white" />
                    <span>See the Realty Reality</span>
                    <ArrowRight className="w-4 h-4 text-white/80" />
                  </button>

                  <a
                    href="#realty-reality"
                    className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all flex items-center gap-2"
                  >
                    <Lock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Why Brokers Lose Buyers</span>
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
                    poster="/assets/posters/real_estate_avatar.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/robot_avatars/real_estate_avatar.webm" type="video/webm" />
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
                Listen: Voicemail Loss vs. Instant Pre-Qualified Showing
              </h2>
              <p className="text-sm text-slate-600">
                Buyers parked curbside looking at your yard sign won't wait 3 hours for a callback. Hear the A.L.F.I.E. conversion difference.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Interactive Player */}
              <div className="lg:col-span-7">
                <BeforeAfterAudioPlayer 
                  customTracks={realEstateAudioTracks}
                  title="Real Estate Inbound Lead Triage"
                  subtitle="Live Telephony Simulation"
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
                    poster="/assets/posters/real_estate.jpg"
                    className="w-full h-full object-cover pointer-events-none"
                  >
                    <source src="/assets/industry_videos/real_estate/real_estate.webm" type="video/webm" />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end p-5">
                    <div>
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/90 text-white text-[10px] font-mono font-bold mb-1">
                        <Check className="w-3 h-3" />
                        <span>Live MLS Integration Active</span>
                      </div>
                      <p className="text-xs font-semibold text-white">
                        Direct Bi-Directional Follow Up Boss & kvCORE Sync
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">LISTING STATUS</span>
                    <span className="font-bold text-slate-900">Active MLS ($1.45M)</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">QUALIFIED TOUR</span>
                    <span className="font-bold text-cyan-600">Locked: Thursday 4 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Deterministic Realty Pipeline (Interactive Badges) ── */}
        <section className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
              <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest font-mono">Realty Automation</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Deterministic Buyer Qualification Pipeline
              </h2>
              <p className="text-sm text-slate-600">
                Sub-80ms MLS database lookups for active status, square footage, HOA fees, and calendar locking.
              </p>
            </div>

            {/* 4 Interactive Visual Step Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  01
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">MLS Inventory Lookup</h3>
                <p className="text-xs text-slate-500 mb-3">Instant query against active MLS IDX feeds by address.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-cyan-700 flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                  <span>MLS #8820: Active ($1.45M)</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  02
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Financing Qualification</h3>
                <p className="text-xs text-slate-500 mb-3">Screens for jumbo pre-approval & cash buyer readiness.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <CheckSquare className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                  <span>Jumbo Pre-Approval Verified</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  03
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Calendar Tour Booking</h3>
                <p className="text-xs text-slate-500 mb-3">Syncs with listing agent's Google or Outlook calendar.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Thursday 4:00 PM Locked</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-cyan-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  04
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Brochure & Gate PIN SMS</h3>
                <p className="text-xs text-slate-500 mb-3">Sends PDF brochure, floor plans, and gated entry code.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                  <span>SMS Sent with Gate Code</span>
                </div>
              </div>
            </div>

            {/* Sold Sign Video Feature Card */}
            <div className="mt-8 rounded-2xl overflow-hidden border border-slate-200 bg-slate-50 p-6 flex flex-col md:flex-row items-center gap-6 shadow-xs">
              <div className="w-full md:w-56 h-36 rounded-xl overflow-hidden shrink-0 border border-slate-200 relative">
                <video 
                  autoPlay 
                  loop 
                  muted 
                  playsInline 
                  poster="/assets/posters/real_estate_2.jpg"
                  className="w-full h-full object-cover pointer-events-none"
                >
                  <source src="/assets/industry_videos/real_estate/real_estate_2.webm" type="video/webm" />
                </video>
              </div>
              <div className="space-y-1.5">
                <span className="text-[10px] font-mono font-bold text-cyan-600 uppercase tracking-widest">Accelerated Deal Velocity</span>
                <h4 className="text-base font-bold text-slate-900">Close More Listings with 24/7 Rapid Response</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Real estate leads contacted within 5 minutes of inquiry are 21x more likely to enter the sales cycle. Marcus Sterling ensures 100% of sign calls, website queries, and Zillow leads receive an immediate, professional, conversational response within 15 seconds.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pain Point Education: The Curbside Sign Bleed ── */}
        <section id="realty-reality" className="py-20 bg-slate-50/70 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
              <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest font-mono">
                The Reality of Real Estate Lead Conversion
              </span>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-900 font-heading tracking-tight">
                The Curbside Sign Bleed: Why Motivated Buyers Call the Next Agent
              </h2>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                When an approved buyer is parked in front of your listing calling the yard sign, their intent is at an all-time peak. If your phone goes to voicemail, they drive away to the next open house or tap Zillow to connect with a competing broker.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
              
              {/* Left Column: Real Luxury Property & Financial Reality Card */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="rounded-3xl overflow-hidden border border-slate-200 shadow-md relative h-72 sm:h-80 group">
                  <img
                    src="/assets/industry_photos/real_estate/niche_realestate_luxury.webp"
                    alt="Luxury residential property listing"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/20 to-transparent flex items-end p-6">
                    <div className="space-y-1">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-300 block">
                        Sunday 2:15 PM • Curbside Reality
                      </span>
                      <p className="text-sm font-medium text-white/95 leading-snug">
                        An approved $1.8M buyer is parked outside your new listing. You're hosting an open house across town and cannot answer.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mathematical Bleed Reality Card */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-mono font-bold text-slate-500 uppercase">Average Commission Bleed</span>
                    <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                      - $45,000 / Missed Buyer
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Direct buyer inquiries on your listings represent double-ended transactions. Missing one curbside sign call gives away a 5-figure commission check to another agent within minutes.
                  </p>
                  <div className="grid grid-cols-2 gap-3 pt-2 text-center font-mono">
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-rose-600 block">82%</span>
                      <span className="text-[10px] text-slate-500">Won't leave sign voicemail</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-emerald-600 block">&lt; 15s</span>
                      <span className="text-[10px] text-slate-500">A.L.F.I.E. tour booking</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: The 3 Core Realty Pain Points & How A.L.F.I.E. Eliminates Them */}
              <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
                
                {/* Pain Point 1 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-rose-100">
                      01
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      The "Currently in a Showing" Voicemail Trap
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    Top-producing agents are constantly in showings, closings, or driving between appointments. But when a hot buyer calls your sign and hears <em>"I'm currently touring with clients, please leave a message,"</em> they don't wait. They call the next sign down the street.
                  </p>
                </div>

                {/* Pain Point 2 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-cyan-100">
                      02
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Wasting Hours on Unvetted Curiosity Callers
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    Agents spend hours answering random tire-kickers and neighbors asking for property prices without pre-approvals. Meanwhile, real accredited jumbo buyers get lost in an overflowing voicemail inbox.
                  </p>
                </div>

                {/* Pain Point 3 & Resolution */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-cyan-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      03
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      How A.L.F.I.E. Converts Sign Calls into Private Tours
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    A.L.F.I.E. answers on ring one with deep knowledge of every property in your MLS IDX inventory. It confirms price, bedrooms, and HOA fees, verifies buyer pre-approval credentials, books a private showing directly in ShowingTime, and texts the agent a full dossier on the buyer within 30 seconds.
                  </p>
                </div>

                {/* Reassurance Banner */}
                <div className="p-5 rounded-2xl bg-cyan-50/70 border border-cyan-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="space-y-0.5 text-center sm:text-left">
                    <h4 className="text-xs font-bold text-cyan-950 font-mono uppercase">ShowingTime & MLS IDX Synchronized</h4>
                    <p className="text-xs text-cyan-900/80">Every yard sign and portal lead converted into calendar bookings while you tour with clients.</p>
                  </div>
                  <a
                    href="mailto:contact@alfie.ai?subject=Brokerage%20Lead%20Consultation"
                    className="shrink-0 bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-xl text-xs shadow-xs transition-all"
                  >
                    Schedule Brokerage Walkthrough
                  </a>
                </div>

              </div>

            </div>
          </div>
        </section>

        {/* ── Realty CRM Integrations Strip ── */}
        <section className="py-16 bg-white border-t border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center space-y-6">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 font-mono">
                Native Bi-Directional Real Estate CRM & MLS Integrations
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 text-slate-700 text-sm font-semibold">
                <span className="hover:text-cyan-600 transition-colors">Follow Up Boss</span>
                <span className="hover:text-cyan-600 transition-colors">kvCORE</span>
                <span className="hover:text-cyan-600 transition-colors">BoomTown</span>
                <span className="hover:text-cyan-600 transition-colors">Chime / Lofty</span>
                <span className="hover:text-cyan-600 transition-colors">LionDesk</span>
                <span className="hover:text-cyan-600 transition-colors">MLS IDX Feeds</span>
              </div>
              <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed font-mono">
                MLS IDX & Fair Housing Compliant. Rigorous deterministic guardrails prevent steering, price misquotations, or disclosure violations.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
