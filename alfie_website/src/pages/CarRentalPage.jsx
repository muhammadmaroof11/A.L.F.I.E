import React from 'react';
import { 
  Car, Shield, PhoneCall, ArrowRight, Lock, 
  MapPin, DollarSign, CreditCard, Send, Check
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import BeforeAfterAudioPlayer from '../components/ui/BeforeAfterAudioPlayer';

export default function CarRentalPage() {
  const scrollToReality = () => {
    const el = document.getElementById('fleet-reality');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  const scrollToDemo = scrollToReality;

  const carRentalAudioTracks = {
    legacy: {
      title: 'Manual Midnight Dispatch Voicemail',
      subtitle: '4 Rings • Owner Sleeping • Delayed Voicemail',
      transcript: '"You have reached Blackline Executive Limousine. Our office is currently closed. Please leave your pickup date, time, and address after the tone..." [Executive hangs up and opens Uber Black]',
      impact: 'Lost $340 JFK airport transfer to competitor in under 20 seconds',
      latency: 'Closed until 8:00 AM next day',
    },
    alfie: {
      title: 'A.L.F.I.E. Autonomous Dispatcher',
      subtitle: 'Sub-Second Pickup • OSRM Dynamic Pricing • Instant Deposit Link',
      transcript: '"Good evening Mr. Vance! Flight DL 412 is tracking 35 minutes late. For your party of four to The Plaza Hotel in a 2026 Cadillac Escalade ESV, your flat rate is $240. I just texted your Stripe deposit link with Apple Pay."',
      impact: '100% Secured $240 Fare with 20% Deposit Locked Before Hangup',
      latency: '55ms routing & rate calculation',
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-emerald-500 selection:text-white relative">
      <Navbar onOpenDemo={scrollToDemo} />

      <main className="pt-14 sm:pt-16">
        {/* ── Hero Section ── */}
        <section className="relative overflow-hidden w-full lg:min-h-[calc(100vh-3.5rem)] lg:max-h-[calc(100vh-3.5rem)] flex items-center bg-white border-b border-slate-200/80 py-8 lg:py-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full py-2">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">

              {/* Left Column */}
              <div className="lg:col-span-7 space-y-4">
                <h1 className="text-3xl sm:text-4xl lg:text-[2.6rem] xl:text-[2.9rem] font-extrabold tracking-tight text-slate-900 leading-[1.1] font-heading">
                  Never Lose a Midnight{' '}
                  <span className="text-emerald-600">
                    Airport Transfer
                  </span>{' '}
                  to Voicemail.
                </h1>

                <p className="text-sm sm:text-base text-slate-600 max-w-2xl leading-relaxed">
                  Chloe calculates dynamic highway mileage, tracks flight delays, quotes luxury vehicle tiers (Escalade, S-Class), and texts instant Stripe deposit links before callers hang up.
                </p>

                {/* Proof Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono">
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">&lt;15s</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Quote to Text Link</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">100%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">24/7 After-Hours Cover</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-emerald-600">+34%</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Secured Deposits</div>
                  </div>
                  <div className="bg-slate-50 p-2.5 sm:p-3 rounded-xl border border-slate-200/80 shadow-2xs">
                    <div className="text-xl sm:text-2xl font-extrabold text-slate-900">55ms</div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 font-medium mt-0.5">Routing Engine Time</div>
                  </div>
                </div>

                {/* CTAs */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <button
                    onClick={scrollToReality}
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-all text-xs"
                  >
                    <PhoneCall className="w-4 h-4 text-white" />
                    <span>See the Dispatch Reality</span>
                    <ArrowRight className="w-4 h-4 text-white/80" />
                  </button>

                  <a
                    href="#fleet-reality"
                    className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-200/90 shadow-2xs transition-all flex items-center gap-2"
                  >
                    <Lock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Why Fleets Lose Bookings</span>
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
                    poster="/assets/posters/car_rental_avatar.jpg"
                    className="w-full h-full object-contain pointer-events-none"
                  >
                    <source src="/assets/robot_avatars/car_rental_avatar.webm" type="video/webm" />
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
              <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest font-mono">Auditory Comparison</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Listen: Voicemail Hangup vs. 15-Second Deposit Lock
              </h2>
              <p className="text-sm text-slate-600">
                Hear how A.L.F.I.E. rescues late-night airport transfers while owner-operators and dispatchers are asleep.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Interactive Player */}
              <div className="lg:col-span-7">
                <BeforeAfterAudioPlayer 
                  customTracks={carRentalAudioTracks}
                  title="VIP Chauffeur Dispatch Experience"
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
                    poster="/assets/posters/chauffer_service.jpg"
                    className="w-full h-full object-cover pointer-events-none"
                  >
                    <source src="/assets/industry_videos/car_rental/chauffer_service.webm" type="video/webm" />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex items-end p-5">
                    <div>
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/90 text-white text-[10px] font-mono font-bold mb-1">
                        <Check className="w-3 h-3" />
                        <span>Live Distance Quoting Engine Active</span>
                      </div>
                      <p className="text-xs font-semibold text-white">
                        Direct Highway Mileage & Bridge Toll Routing
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">ROUTE TIERS</span>
                    <span className="font-bold text-slate-900">2026 Escalade ESV</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                    <span className="text-slate-400 block text-[10px]">DEPOSIT LINK</span>
                    <span className="font-bold text-emerald-600">Stripe SMS Sent (15s)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Deterministic Dispatch Pipeline (Interactive Badges) ── */}
        <section className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
              <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest font-mono">Dispatch Intelligence</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading">
                Deterministic Chauffeur Routing Pipeline
              </h2>
              <p className="text-sm text-slate-600">
                Under 60ms calculations for highway distance, real-time tolls, vehicle classification, and SMS deposit links.
              </p>
            </div>

            {/* 4 Interactive Visual Step Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-emerald-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  01
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">OSRM Mileage Sync</h3>
                <p className="text-xs text-slate-500 mb-3">Calculates true highway miles & airport access tolls.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>JFK T4 ➔ Plaza (18.4 mi)</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-emerald-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  02
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Rate Card Valuation</h3>
                <p className="text-xs text-slate-500 mb-3">Evaluates vehicle tier flat-rates vs. hourly minimums.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Escalade ESV: $240 Flat</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-emerald-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  03
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Stripe Deposit Link</h3>
                <p className="text-xs text-slate-500 mb-3">Pre-authorizes 20% deposit via PCI-DSS Stripe link.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-emerald-700 flex items-center gap-1.5">
                  <CreditCard className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>$48 Deposit Authorized</span>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-emerald-400 transition-all shadow-2xs group">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-mono font-bold text-xs mb-3 group-hover:scale-105 transition-transform">
                  04
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">Flight Radar & SMS</h3>
                <p className="text-xs text-slate-500 mb-3">Subscribes to flight radar updates & driver assignment.</p>
                <div className="p-2 rounded-lg bg-white border border-slate-200/80 font-mono text-[11px] text-slate-700 flex items-center gap-1.5">
                  <Send className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>SMS Sent with Chauffeur PIN</span>
                </div>
              </div>
            </div>

            {/* Airport Private Jet Hangar Showcase */}
            <div className="mt-8 rounded-2xl overflow-hidden border border-slate-200 bg-slate-50 p-6 flex flex-col md:flex-row items-center gap-6 shadow-xs">
              <div className="w-full md:w-56 h-36 rounded-xl overflow-hidden shrink-0 border border-slate-200">
                <img 
                  src="/assets/industry_photos/car_rental/carrental_male.webp" 
                  alt="Airport FBO and private jet executive dispatch" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="space-y-1.5">
                <span className="text-[10px] font-mono font-bold text-emerald-600 uppercase tracking-widest">FBO & Private Aviation Integration</span>
                <h4 className="text-base font-bold text-slate-900">Tail-Number Tracking for Private Aviation (Signature & Atlantic FBOs)</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  When private charter jets land early or late at Teterboro or Van Nuys, Chloe automatically adjusts chauffeur staging times at the FBO ramp, guaranteeing zero idle waiting charges.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pain Point Education: The Midnight Dispatch Void ── */}
        <section id="fleet-reality" className="py-20 bg-slate-50/70 border-b border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
              <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest font-mono">
                The Reality of Fleet & Livery Dispatch
              </span>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-900 font-heading tracking-tight">
                The Midnight Dispatch Void: The Luxury Bookings You Never Knew You Lost
              </h2>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                Executive travelers and corporate planners don't book on a 9-to-5 schedule. When delayed flights land after midnight and your phone hits voicemail, high-paying clients tap Uber Black in 20 seconds.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
              
              {/* Left Column: Real Fleet Operations & Financial Reality Card */}
              <div className="lg:col-span-5 flex flex-col justify-between space-y-6">
                <div className="rounded-3xl overflow-hidden border border-slate-200 shadow-md relative h-72 sm:h-80 group">
                  <img
                    src="/assets/industry_photos/car_rental/niche_fleet_vip.webp"
                    alt="Night VIP executive fleet dispatch operations"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/20 to-transparent flex items-end p-6">
                    <div className="space-y-1">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-300 block">
                        11:20 PM • Private Aviation Ramp Reality
                      </span>
                      <p className="text-sm font-medium text-white/95 leading-snug">
                        A corporate executive's scheduled driver no-showed. They need an Escalade immediately. Your office is closed.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Mathematical Bleed Reality Card */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-mono font-bold text-slate-500 uppercase">Average Corporate Account Bleed</span>
                    <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                      - $35,000 / Lost Client
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Corporate travel coordinators book their executive accounts with whoever answers first. One missed late-night call costs you not just a $300 airport transfer, but an entire recurring enterprise account.
                  </p>
                  <div className="grid grid-cols-2 gap-3 pt-2 text-center font-mono">
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-rose-600 block">20s</span>
                      <span className="text-[10px] text-slate-500">To lose to rideshare apps</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <span className="text-lg font-black text-emerald-600 block">15s</span>
                      <span className="text-[10px] text-slate-500">A.L.F.I.E. deposit lock</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: The 3 Core Fleet Pain Points & How A.L.F.I.E. Eliminates Them */}
              <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
                
                {/* Pain Point 1 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-emerald-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-rose-100">
                      01
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      The "We'll Email You a Quote" Delay Kills Urgent Bookings
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    Clients wanting a luxury chauffeured vehicle or sprinter van want to know price and availability right now. When human dispatchers say <em>"Give me your email and I'll send an estimate in an hour,"</em> the customer opens their phone and books someone else.
                  </p>
                </div>

                {/* Pain Point 2 */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-emerald-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      02
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      Flight Delays & Time Zone Mismatches Waste Chauffeur Hours
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    When flights are delayed 3 hours and landing at 1:30 AM, dispatchers are asleep and chauffeurs are staging too early, burning idle fuel and incurring parking fees. Manual flight tracking across multiple drivers creates chaos.
                  </p>
                </div>

                {/* Pain Point 3 & Resolution */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200/90 shadow-2xs space-y-2 hover:border-emerald-400/60 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-mono font-bold text-xs shrink-0 border border-emerald-100">
                      03
                    </div>
                    <h3 className="font-bold text-slate-900 text-base font-heading">
                      How A.L.F.I.E. Eliminates The Midnight Void
                    </h3>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-11">
                    A.L.F.I.E. acts as your 24/7/365 master dispatcher. It calculates exact distance and toll quotes instantly via OSRM, collects Stripe card deposits via 1-click SMS link while still on the call, interfaces with FlightAware to monitor tail numbers, and enters the trip directly into Limo Anywhere.
                  </p>
                </div>

                {/* Reassurance Banner */}
                <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200/70 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="space-y-0.5 text-center sm:text-left">
                    <h4 className="text-xs font-bold text-emerald-950 font-mono uppercase">Full Limo Anywhere & Stripe Integration</h4>
                    <p className="text-xs text-emerald-900/80">Never wake up to lost revenue. Chauffeurs dispatched automatically while you sleep.</p>
                  </div>
                  <a
                    href="mailto:contact@alfie.ai?subject=Fleet%20Dispatch%20Consultation"
                    className="shrink-0 bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-xl text-xs shadow-xs transition-all"
                  >
                    Schedule Fleet Walkthrough
                  </a>
                </div>

              </div>

            </div>
          </div>
        </section>

        {/* ── Fleet Integrations Strip ── */}
        <section className="py-16 bg-white border-t border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center space-y-6">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-500 font-mono">
                Native Bi-Directional Fleet Dispatch Integrations
              </h3>
              <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 text-slate-700 text-sm font-semibold">
                <span className="hover:text-emerald-600 transition-colors">Limo Anywhere</span>
                <span className="hover:text-emerald-600 transition-colors">Moovs</span>
                <span className="hover:text-emerald-600 transition-colors">Samsara Telematics</span>
                <span className="hover:text-emerald-600 transition-colors">FlightAware API</span>
                <span className="hover:text-emerald-600 transition-colors">Stripe Terminal & Payment Links</span>
                <span className="hover:text-emerald-600 transition-colors">Twilio High-Throughput SMS</span>
              </div>
              <p className="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed font-mono">
                PCI-DSS Level 1 Compliant. Ephemeral payment tokenization ensures credit card numbers are never stored in audio or text transcripts.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
