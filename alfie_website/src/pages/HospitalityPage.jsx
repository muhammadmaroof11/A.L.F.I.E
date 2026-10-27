import React from 'react';
import { 
  Hotel, Shield, PhoneCall, ArrowRight, Lock, 
  Utensils, Calendar, Users, HeartHandshake, Check
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import BeforeAfterAudioPlayer from '../components/ui/BeforeAfterAudioPlayer';

export default function HospitalityPage() {
  const scrollToReality = () => {
    const el = document.getElementById('hospitality-reality');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  const scrollToDemo = scrollToReality;

  const hospitalityAudioTracks = {
    legacy: {
      title: 'Friday 7:00 PM Noisy Host Stand Queue',
      subtitle: '4 Rings • Loud Restaurant Background • Rushed Host',
      transcript: '"[Loud dining room noise, clinking glasses] Thank you for calling L\'Aura, please hold! [3 minutes of silence] Hello? Look, we\'re completely slammed tonight, can you check OpenTable or call tomorrow?" [Caller hangs up]',
      impact: 'Lost $480 4-guest anniversary dinner and tasting menu buyout',
      latency: '3+ minute distracted hold',
    },
    alfie: {
      title: 'A.L.F.I.E. Autonomous Maitre D\'',
      subtitle: 'First Ring Pickup • Studio Acoustics • Direct Table Allocation',
      transcript: '"Good evening Mr. Sterling! I would be delighted to seat your party of four this Friday. I have reserved the Corner Patio Booth at 7:30 PM, and I have flagged your anniversary champagne and nut allergy with Chef Julian."',
      impact: 'Secured $480 Tasting Menu • VIP Notes Logged • OpenTable Synced',
      latency: 'Sub-40ms table allocation',
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-purple-500 selection:text-white relative">
      <Navbar onOpenDemo={scrollToDemo} />

      <main className="pt-14 sm:pt-16">
        {/* ── Hero Section ── */}
        <section className="relative overflow-hidden w-full lg:min-h-[calc(100vh-3.5rem)] lg:max-h-[calc(100vh-3.5rem)] flex items-center bg-white border-b border-slate-200/80 py-8 lg:py-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full py-2">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
              
              {/* Left Column */}
              <div className="lg:col-span-7 space-y-4">
                <h1 className="text-3xl sm:text-4xl lg:text-[2.6rem] xl:text-[2.9rem] font-extrabold tracking-tight text-slate-900 leading-[1.1] font-heading">
                  Zero Unanswered Calls During the{' '}
                  <span className="text-purple-600">
                    Friday 7:00 PM Rush
                  </span>
                  .
                </h1>

                <p className="text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Julian Rossi answers dining room inquiries, logs dietary allergies, and locks table reservations in SevenRooms & OpenTable without taking floor hosts away from guests.
                </p>

                {/* Proof Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono">
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-purple-600">100%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Dinner Rush Capture</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">&lt; 40ms</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Table Inventory Lock</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">-42%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Table No-Shows</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-purple-600">0s</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Hostess Distraction</div>
                  </div>
                </div>

                {/* Primary CTAs */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    onClick={scrollToReality}
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-all text-xs"
                  >
                    <PhoneCall className="w-4 h-4 text-white" />
                    <span>See the Floor Reality</span>
                    <ArrowRight className="w-4 h-4 text-white/80" />
                  </button>

                  <a
                    href="#hospitality-reality"
                    className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all flex items-center gap-2"
                  >
                    <Lock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Why Venues Lose Tables</span>
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
                    poster="/assets/posters/hospitality_avatar.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/robot_avatars/hospitality_avatar.webm" type="video/webm" />
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
              <span className="text-xs font-bold text-purple-600 uppercase tracking-widest font-mono">Auditory Comparison</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Listen: Dinner Rush Chaos vs. Flawless Hospitality
              </h2>
              <p className="text-sm text-slate-600">
                Experience how A.L.F.I.E. protects the dining room atmosphere while capturing high-margin table reservations in seconds.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Interactive Player */}
              <div className="lg:col-span-7">
                <BeforeAfterAudioPlayer 
                  customTracks={hospitalityAudioTracks}
                  title="Fine Dining Reservation Experience"
                  subtitle="Live Floor Audio Simulation"
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
                    poster="/assets/posters/restaurant.jpg"
                    className="w-full h-full object-cover pointer-events-none"
                  >
                    <source src="/assets/industry_videos/hospitality/restaurant.webm" type="video/webm" />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end p-5">
                    <div>
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/90 text-white text-[10px] font-mono font-bold mb-1">
                        <Check className="w-3 h-3" />
                        <span>Live Floor Table Inventory Sync</span>
                      </div>
                      <p className="text-xs font-semibold text-white">
                        Direct Bi-Directional OpenTable & SevenRooms Bridge
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">SEATED TABLE</span>
                    <span className="font-bold text-slate-900">Patio Booth #14 (4p)</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">GUEST PROFILE</span>
                    <span className="font-bold text-purple-600">Anniversary · Champagne</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Deterministic Hospitality Pipeline (Interactive Badges) ── */}
        <section className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
              <span className="text-xs font-bold text-purple-600 uppercase tracking-widest font-mono">Hospitality Logic</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Deterministic Table Reservation Pipeline
              </h2>
              <p className="text-sm text-slate-600">
                Sub-40ms database queries for party size allocation, allergy flags, and instant SMS reservation confirmations.
              </p>
            </div>

            {/* 4 Interactive Visual Step Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-purple-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  01
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Live Table Seating Lock</h3>
                <p className="text-xs text-slate-500 mb-3">Checks open turn windows & party capacity.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-purple-700 flex items-center gap-1.5">
                  <Utensils className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>Table 14: Booth Available</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-purple-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  02
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">VIP Profiling & Allergies</h3>
                <p className="text-xs text-slate-500 mb-3">Logs dietary preferences and celebration notes.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <HeartHandshake className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>Gluten Allergy & Anniversary</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-purple-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  03
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">SevenRooms Booking Write</h3>
                <p className="text-xs text-slate-500 mb-3">Locks reservation directly into the floor management system.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Confirmed in SevenRooms</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-purple-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  04
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Calendar & SMS Dispatch</h3>
                <p className="text-xs text-slate-500 mb-3">Dispatches calendar invitation, dress code & parking directions.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>SMS Sent with Valet PIN</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pain Point Education: The Friday 7:30 PM Crunch ── */}
        <section id="hospitality-reality" className="py-20 bg-slate-50/70 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
              <span className="text-xs font-bold text-purple-600 uppercase tracking-widest font-mono">
                The Reality of Fine Dining & Hospitality
              </span>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-900 font-heading tracking-tight">
                The Friday 7:30 PM Crunch: When a Full Floor Loses You Tomorrow's Tables
              </h2>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                During prime dinner service, your hosts are swamped greeting guests, checking coats, and seating VIPs. When callers hear endless rings or rushed staff, they open Resy and book the competitor across the street.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
              
              {/* Left Column: Real Restaurant Environment & Financial Reality Card */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="rounded-3xl overflow-hidden border border-slate-200 shadow-md relative h-72 sm:h-80 group">
                  <img
                    src="/assets/industry_photos/hospitality/restaurant.webp"
                    alt="Packed restaurant dining room and host stand operations"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/20 to-transparent flex items-end p-6">
                    <div className="space-y-1">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-purple-300 block">
                        Friday 8:00 PM • Host Stand Reality
                      </span>
                      <p className="text-sm font-medium text-white/95 leading-snug">
                        60 seated guests, 4 waiting at the bar, and the reservation line ringing continuously in the background.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mathematical Bleed Reality Card */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-mono font-bold text-slate-500 uppercase">Average Weekend Table Bleed</span>
                    <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                      - $1,800 / Weekend Night
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Celebration diners and high-check corporate parties call ahead to secure special seating. When the phone goes unanswered, they assume you have zero availability and book elsewhere.
                  </p>
                  <div className="grid grid-cols-2 gap-3 pt-2 text-center font-mono">
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-rose-600 block">74%</span>
                      <span className="text-[10px] text-slate-500">Won't call back after busy signal</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-emerald-600 block">0s</span>
                      <span className="text-[10px] text-slate-500">A.L.F.I.E. SevenRooms lock</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: The 3 Core Hospitality Pain Points & How A.L.F.I.E. Eliminates Them */}
              <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
                
                {/* Pain Point 1 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-purple-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-rose-100">
                      01
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      The Noisy, Distracted Host Stand Phone Call
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    When a host tries to take a reservation amidst screaming dining room chatter, clinking glassware, and guests waiting in line, mistakes happen. Dietary allergies get lost, party sizes get mixed up, and callers feel like an unwelcome nuisance.
                  </p>
                </div>

                {/* Pain Point 2 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-purple-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-purple-100">
                      02
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Private Dining & Buyout Inquiries Never Leave Voicemails
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    High-spend corporate event planners looking to book a $4,000 tasting room will not leave a voicemail. If nobody answers with polished menu knowledge and sommelier awareness, they move straight down their vendor list.
                  </p>
                </div>

                {/* Pain Point 3 & Resolution */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-purple-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      03
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      How A.L.F.I.E. Restores 100% Focus to the Floor
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    A.L.F.I.E. speaks with the warmth and precision of a seasoned Maitre D. It interfaces directly with SevenRooms, OpenTable, and Resy, answers wine and corkage questions, notes anniversaries, locks the reservation into your floorplan, and texts valet directions—without your hosts ever picking up a phone.
                  </p>
                </div>

                {/* Reassurance Banner */}
                <div className="p-5 rounded-2xl bg-purple-50/70 border border-purple-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="space-y-0.5 text-center sm:text-left">
                    <h4 className="text-xs font-bold text-purple-950 font-mono uppercase">SevenRooms, OpenTable & Resy Ready</h4>
                    <p className="text-xs text-purple-900/80">Zero disruption to front-of-house staff. Every table captured while your team delights seated guests.</p>
                  </div>
                  <a
                    href="mailto:contact@alfie.ai?subject=Hospitality%20Venue%20Consultation"
                    className="shrink-0 bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-xl text-xs shadow-xs transition-all"
                  >
                    Schedule Venue Walkthrough
                  </a>
                </div>

              </div>

            </div>
          </div>
        </section>

        {/* ── Hospitality Integrations Strip ── */}
        <section className="py-16 bg-white border-t border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center space-y-6">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 font-mono">
                Native Bi-Directional Hospitality & Reservation Integrations
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 text-slate-700 text-sm font-semibold">
                <span className="hover:text-purple-600 transition-colors">SevenRooms</span>
                <span className="hover:text-purple-600 transition-colors">OpenTable</span>
                <span className="hover:text-purple-600 transition-colors">Resy OS</span>
                <span className="hover:text-purple-600 transition-colors">Toast POS</span>
                <span className="hover:text-purple-600 transition-colors">Square for Restaurants</span>
                <span className="hover:text-purple-600 transition-colors">Twilio SMS</span>
              </div>
              <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed font-mono">
                PCI-DSS Level 1 Compliant. Secure deposit holds for large parties without storing payment card numbers on-premise.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
