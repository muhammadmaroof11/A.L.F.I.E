import React, { useState, useEffect, useRef } from 'react';
import { 
  Phone, Mic, MicOff, PhoneOff, PhoneCall, Volume2, ShieldCheck, 
  Zap, Globe, Sparkles, Building2, Car, Stethoscope, Scale, UtensilsCrossed,
  CheckCircle2, ArrowRight, Play, Calculator, Star, ExternalLink,
  UserCheck, Clock, Award, ChevronRight, MessageSquare
} from 'lucide-react';

const NICHES = [
  {
    id: 'law',
    slug: 'law-firms',
    title: 'Personal Injury & Law Firms',
    tagline: '24/7 Client Intake & High-Value Case Triage',
    themeColor: 'from-amber-400 via-yellow-500 to-amber-600',
    accentBorder: 'border-amber-500/40',
    accentBg: 'bg-amber-950/30',
    accentText: 'text-amber-400',
    badgeText: 'Legal Intake Specialist',
    icon: Scale,
    description: 'Screens accident dates, liability, and injury severity with composed, authoritative empathy. Instantly triggers warm SIP transfers to managing attorneys for high-value claims.',
    femaleAvatar: '/avatars/law_female.jpg',
    femaleName: 'Elena Vance, Esq. AI',
    femaleVoice: 'Steady, articulate, authoritative legal tone',
    maleAvatar: '/avatars/law_male.jpg',
    maleName: 'Marcus Sterling, AI Triage',
    maleVoice: 'Deep, calm, confident baritone advisor',
    sampleQuestions: [
      '"I was rear-ended at a red light yesterday and have neck pain."',
      '"How does your contingency fee structure work?"',
      '"Can I speak with a managing attorney right away?"'
    ],
    features: [
      'Contingency & liability pre-qualification',
      'Automated retainer e-sign dispatch via SMS',
      'Live warm SIP transfer to attorney mobile phone',
      'Statute of limitations safety checks'
    ]
  },
  {
    id: 'real_estate',
    slug: 'real-estate',
    title: 'Luxury Real Estate',
    tagline: 'Buyer Qualification & Private Viewing Scheduler',
    themeColor: 'from-cyan-400 via-blue-500 to-indigo-600',
    accentBorder: 'border-cyan-500/40',
    accentBg: 'bg-cyan-950/30',
    accentText: 'text-cyan-400',
    badgeText: 'Prime Property Advisor',
    icon: Building2,
    description: 'Captures buyer budgets, preferred locations, and architectural requirements. Answers HOA/amenity questions and books private site tours directly into agent calendars.',
    femaleAvatar: '/avatars/realestate_female.jpg',
    femaleName: 'Sophia Laurent, Real Estate AI',
    femaleVoice: 'Warm, charismatic, polished broker tone',
    maleAvatar: '/avatars/realestate_male.jpg',
    maleName: 'Julian Hayes, Portfolio AI',
    maleVoice: 'Suave, engaging, commercial advisor',
    sampleQuestions: [
      '"I am looking for a 3-bedroom penthouse with coastal views under $2.5M."',
      '"Can I book a private property viewing this Saturday at 2 PM?"',
      '"What are the monthly HOA and building amenity fees?"'
    ],
    features: [
      'Instant property inventory & price lookup',
      'Direct Cal.com & Google Calendar tour bookings',
      'Twenty CRM & HubSpot lead qualification sync',
      'Neighborhood & school district intelligence'
    ]
  },
  {
    id: 'car_rental',
    slug: 'car-rental',
    title: 'Exotic Fleet & Car Rental',
    tagline: 'Instant Vehicle Availability & Fast Reservations',
    themeColor: 'from-emerald-400 via-teal-500 to-cyan-600',
    accentBorder: 'border-emerald-500/40',
    accentBg: 'bg-emerald-950/30',
    accentText: 'text-emerald-400',
    badgeText: 'VIP Fleet Dispatcher',
    icon: Car,
    description: 'Checks real-time vehicle availability (supercars, luxury SUVs), calculates rental duration, deposits, and insurance terms, and locks in reservation dates.',
    femaleAvatar: '/avatars/carrental_female.jpg',
    femaleName: 'Chloe Bennett, VIP Concierge',
    femaleVoice: 'Crisp, upbeat, luxury hospitality tone',
    maleAvatar: '/avatars/carrental_male.jpg',
    maleName: 'Dominic Cruz, Fleet Dispatch',
    maleVoice: 'Fast-paced, sharp, automotive expert',
    sampleQuestions: [
      '"Do you have a Lamborghini Urus or Range Rover available this weekend?"',
      '"What are your minimum age and security deposit requirements?"',
      '"Can you deliver the vehicle directly to Miami Airport?"'
    ],
    features: [
      'Live fleet inventory & deposit calculator',
      'Airport & hotel delivery scheduling',
      'Instant driver license photo capture via SMS link',
      'Automated credit card pre-authorization'
    ]
  },
  {
    id: 'clinic',
    slug: 'clinics',
    title: 'Medical & Dental Clinics',
    tagline: '24/7 Patient Reception & Insurance Triage',
    themeColor: 'from-sky-400 via-blue-500 to-teal-500',
    accentBorder: 'border-sky-500/40',
    accentBg: 'bg-sky-950/30',
    accentText: 'text-sky-400',
    badgeText: 'Clinical Receptionist',
    icon: Stethoscope,
    description: 'Handles high-volume patient triage with gentle empathy, verifies in-network insurance coverage (e.g. Delta Dental, Cigna), and schedules practitioner appointments.',
    femaleAvatar: '/avatars/clinic_female.jpg',
    femaleName: 'Sarah Jenkins, Clinic Coordinator',
    femaleVoice: 'Gentle, reassuring, caring bedside manner',
    maleAvatar: '/avatars/clinic_male.jpg',
    maleName: 'Mark Jensen, RN AI Triage',
    maleVoice: 'Calm, patient, clear medical diction',
    sampleQuestions: [
      '"Do you accept Delta Dental PPO or MetLife insurance?"',
      '"I have severe tooth pain and need an emergency visit today."',
      '"Can I schedule an annual health checkup with Dr. Miller?"'
    ],
    features: [
      'In-network insurance eligibility verification',
      'EMR & practice calendar direct booking',
      'Emergency symptom triage & on-call routing',
      'HIPAA-compliant caller privacy guardrails'
    ]
  },
  {
    id: 'hospitality',
    slug: 'hospitality',
    title: '5-Star Hospitality & Concierge',
    tagline: 'VIP Dining Reservations & Guest Services',
    themeColor: 'from-purple-400 via-fuchsia-500 to-pink-600',
    accentBorder: 'border-purple-500/40',
    accentBg: 'bg-purple-950/30',
    accentText: 'text-purple-400',
    badgeText: 'Head Concierge',
    icon: UtensilsCrossed,
    description: 'Delivers five-star hospitality etiquette. Manages VIP table allocations, records dietary restrictions and anniversaries, and books luxury amenities.',
    femaleAvatar: '/avatars/hospitality_female.jpg',
    femaleName: 'Claire Beaumont, Head Concierge',
    femaleVoice: 'Sophisticated, melodic, five-star poise',
    maleAvatar: '/avatars/hospitality_male.jpg',
    maleName: 'Antoine Moreau, Guest Relations',
    maleVoice: 'Refined, cultured, courteous host',
    sampleQuestions: [
      '"I need a private booth for an anniversary dinner for 4 tonight."',
      '"Does the tasting menu accommodate gluten and dairy allergies?"',
      '"Can you arrange private chauffeur pickup from the hotel lobby?"'
    ],
    features: [
      'Live table inventory & party size balancing',
      'VIP guest profile & dietary preference logging',
      'Private room & bottle service reservations',
      'Multi-course tasting menu explanations'
    ]
  }
];

export default function App() {
  const [selectedNiche, setSelectedNiche] = useState(NICHES[0]);
  const [selectedGender, setSelectedGender] = useState('female'); // 'female' | 'male'
  const [callState, setCallState] = useState('idle'); // 'idle' | 'connecting' | 'active' | 'ended'
  const [isMuted, setIsMuted] = useState(false);
  const [secondsRemaining, setSecondsRemaining] = useState(90); // 90-second demo limit
  const [statusMessage, setStatusMessage] = useState('');
  
  // Callback Form
  const [callbackName, setCallbackName] = useState('');
  const [callbackPhone, setCallbackPhone] = useState('');
  const [callbackSuccess, setCallbackSuccess] = useState(false);
  const [callbackLoading, setCallbackLoading] = useState(false);

  // ROI Calculator State
  const [dailyCalls, setDailyCalls] = useState(50);
  const [avgTicketValue, setAvgTicketValue] = useState(400);

  const timerRef = useRef(null);

  // ROI calculation
  const missedCallsPerMonth = Math.round(dailyCalls * 30 * 0.22);
  const recoveredRevenue = Math.round(missedCallsPerMonth * 0.35 * avgTicketValue);
  const hoursSavedPerMonth = Math.round((dailyCalls * 30 * 4.5) / 60);

  // Current Avatar details based on gender
  const currentAvatar = selectedGender === 'female' ? selectedNiche.femaleAvatar : selectedNiche.maleAvatar;
  const currentName = selectedGender === 'female' ? selectedNiche.femaleName : selectedNiche.maleName;
  const currentVoice = selectedGender === 'female' ? selectedNiche.femaleVoice : selectedNiche.maleVoice;

  useEffect(() => {
    if (callState === 'active') {
      timerRef.current = setInterval(() => {
        setSecondsRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            endVoiceCall();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setSecondsRemaining(90);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [callState]);

  const startVoiceCall = () => {
    setCallState('connecting');
    setStatusMessage(`Connecting to ${currentName} (${selectedGender.toUpperCase()} AI)...`);

    // Simulated / live WebRTC connection
    setTimeout(() => {
      setCallState('active');
      setStatusMessage(`Live 90s Preview Session Active — Speak into your mic!`);
    }, 1200);
  };

  const endVoiceCall = () => {
    setCallState('ended');
    setStatusMessage('Demo Call Concluded. Schedule your custom deployment!');
    setTimeout(() => {
      setCallState('idle');
    }, 3500);
  };

  const handleRequestCallback = (e) => {
    e.preventDefault();
    if (!callbackPhone) return;
    setCallbackLoading(true);
    setTimeout(() => {
      setCallbackLoading(false);
      setCallbackSuccess(true);
    }, 1000);
  };

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="min-h-screen bg-[#05070c] text-slate-100 selection:bg-cyan-500 selection:text-black">
      {/* Dynamic Ambient Glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[550px] bg-cyan-500/10 blur-[150px] rounded-full" />
        <div className="absolute top-[800px] -left-40 w-[600px] h-[600px] bg-indigo-600/10 blur-[160px] rounded-full" />
        <div className="absolute top-[1600px] -right-40 w-[700px] h-[600px] bg-amber-500/10 blur-[160px] rounded-full" />
      </div>

      {/* Top Brand Navigation */}
      <header className="relative z-20 border-b border-slate-800/80 bg-[#05070c]/85 backdrop-blur-xl sticky top-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          {/* Logo & Custom Wordmark */}
          <div className="flex items-center gap-3.5">
            <img src="/logo.png" alt="A.L.F.I.E Logo" className="w-10 h-10 object-contain drop-shadow-[0_0_12px_rgba(0,210,224,0.3)]" />
            <div className="flex flex-col">
              <div className="flex items-center gap-1 text-2xl font-black tracking-widest text-white">
                <span>A</span>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mb-1" />
                <span>L</span>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mb-1" />
                <span>F</span>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mb-1" />
                <span>I</span>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mb-1" />
                <span>E</span>
              </div>
              <span className="text-[9px] font-bold text-cyan-400 uppercase tracking-widest -mt-1">Automated Voice AI</span>
            </div>
          </div>

          <nav className="hidden lg:flex items-center gap-7 text-sm font-medium text-slate-300">
            <a href="#arena" className="hover:text-cyan-400 transition-colors">Niche Demo Arena</a>
            <a href="#verticals" className="hover:text-cyan-400 transition-colors">Verticals</a>
            <a href="#features" className="hover:text-cyan-400 transition-colors">Technology</a>
            <a href="#roi" className="hover:text-cyan-400 transition-colors">ROI Calculator</a>
            <a href="#pricing" className="hover:text-cyan-400 transition-colors">Pricing</a>
          </nav>

          <div className="flex items-center gap-3">
            <a 
              href="http://localhost:5174" 
              target="_blank" 
              rel="noreferrer"
              className="text-xs font-semibold px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
            >
              Client Portal <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
            <a 
              href="http://localhost:5173" 
              target="_blank" 
              rel="noreferrer"
              className="text-xs font-bold px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 shadow-md shadow-cyan-500/20 hover:brightness-110 transition-all flex items-center gap-1.5"
            >
              Super Admin <ExternalLink className="w-3.5 h-3.5 text-slate-950" />
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-16 pb-12 px-6 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-950/40 text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-6">
          <Zap className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          Autonomous Listening & Fluency Intelligence Engine
        </div>

        <h1 className="text-4xl md:text-7xl font-extrabold tracking-tight max-w-5xl mx-auto leading-[1.1] mb-6">
          Hyper-Realistic Voice AI Receptionists{' '}
          <span className="text-gradient-cyan">Custom-Trained for Your Industry.</span>
        </h1>

        <p className="text-base md:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed mb-10">
          A.L.F.I.E answers on the first ring, qualifies high-value clients, and executes appointments directly in your CRM. Test individual niche avatars below with real-time 90-second voice benchmarks.
        </p>

        {/* Quick Vertical Badges */}
        <div className="flex flex-wrap items-center justify-center gap-2 max-w-4xl mx-auto mb-12">
          {NICHES.map((n) => {
            const Icon = n.icon;
            const isSelected = selectedNiche.id === n.id;
            return (
              <button
                key={n.id}
                onClick={() => {
                  if (callState !== 'active') setSelectedNiche(n);
                }}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 border ${
                  isSelected 
                    ? `${n.accentBg} ${n.accentBorder} ${n.accentText} shadow-md` 
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {n.title}
              </button>
            );
          })}
        </div>

        {/* ========================================================================= */}
        {/* INTERACTIVE NICHE DEMO CALL ARENA (ELEVENLABS-STYLE TESTBENCH) */}
        {/* ========================================================================= */}
        <div id="arena" className="scroll-mt-28 max-w-5xl mx-auto">
          <div className="glass-panel-glow p-6 md:p-10 rounded-3xl text-left relative overflow-hidden border border-slate-800">
            {/* Header / Active Niche Meta */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-1">
                  <span className={`px-2.5 py-0.5 rounded-full ${selectedNiche.accentBg} ${selectedNiche.accentBorder} ${selectedNiche.accentText} border`}>
                    {selectedNiche.badgeText}
                  </span>
                  <span className="text-slate-400">90-Second Timed Live Preview</span>
                </div>
                <h2 className="text-2xl md:text-3xl font-extrabold text-white">{selectedNiche.title}</h2>
              </div>

              {/* Gender & Voice Avatar Switcher */}
              <div className="flex items-center gap-2 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
                <button
                  onClick={() => setSelectedGender('female')}
                  disabled={callState === 'active'}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                    selectedGender === 'female' 
                      ? 'bg-cyan-500 text-slate-950 shadow-md' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" /> Female Voice
                </button>
                <button
                  onClick={() => setSelectedGender('male')}
                  disabled={callState === 'active'}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                    selectedGender === 'male' 
                      ? 'bg-cyan-500 text-slate-950 shadow-md' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" /> Male Voice
                </button>
              </div>
            </div>

            {/* Avatar & Call Controls Split Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 py-6 items-center">
              {/* Left Column: Photorealistic Avatar Portrait */}
              <div className="lg:col-span-5 relative group">
                <div className="relative rounded-2xl overflow-hidden border border-slate-700/80 shadow-2xl bg-slate-950 aspect-[3/4] max-w-[340px] mx-auto">
                  <img 
                    src={currentAvatar} 
                    alt={currentName} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
                  
                  {/* Avatar Overlay Badge */}
                  <div className="absolute bottom-4 left-4 right-4 p-3 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-700/80">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-bold text-white">{currentName}</div>
                        <div className="text-[11px] text-cyan-400 font-medium">{currentVoice}</div>
                      </div>
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Interactive Call Console & Prompts */}
              <div className="lg:col-span-7 space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white mb-2">{selectedNiche.tagline}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{selectedNiche.description}</p>
                </div>

                {/* Sample Conversational Questions */}
                <div className="space-y-2 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                    What to test during your demo call:
                  </span>
                  {selectedNiche.sampleQuestions.map((q, idx) => (
                    <div key={idx} className="text-xs text-slate-200 italic flex items-center gap-2">
                      <ChevronRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" /> {q}
                    </div>
                  ))}
                </div>

                {/* Live Call Control Bench */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                  {callState === 'idle' && (
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div>
                        <div className="text-sm font-bold text-white">Ready for 90-Second Test Call</div>
                        <div className="text-xs text-slate-400">Uses browser microphone (Zero login required)</div>
                      </div>
                      <button
                        onClick={startVoiceCall}
                        className="py-3 px-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-black text-xs shadow-lg shadow-cyan-500/25 hover:brightness-110 transition-all flex items-center justify-center gap-2"
                      >
                        <Play className="w-4 h-4 fill-current" /> Call {selectedGender === 'female' ? 'Elena' : 'Marcus'}
                      </button>
                    </div>
                  )}

                  {callState === 'connecting' && (
                    <div className="flex items-center justify-center gap-3 py-2 text-amber-400 text-sm font-bold">
                      <span className="w-3 h-3 rounded-full bg-amber-400 animate-ping" />
                      {statusMessage}
                    </div>
                  )}

                  {callState === 'active' && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                          <span className="text-xs font-bold text-emerald-400 uppercase">Live Session</span>
                        </div>
                        {/* Countdown Dial */}
                        <div className="flex items-center gap-1.5 text-sm font-mono font-black text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-lg border border-cyan-800">
                          <Clock className="w-3.5 h-3.5 text-cyan-400" />
                          {formatTimer(secondsRemaining)} remaining
                        </div>
                      </div>

                      {/* Waveform Bars */}
                      <div className="flex items-center justify-center gap-1.5 h-8">
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                        <span className="wave-bar w-1 bg-cyan-400 rounded-full" />
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => setIsMuted(!isMuted)}
                          className="flex-1 py-2 px-3 rounded-xl bg-slate-800 text-xs font-bold text-slate-200 border border-slate-700 flex items-center justify-center gap-1.5"
                        >
                          {isMuted ? <MicOff className="w-3.5 h-3.5 text-amber-400" /> : <Mic className="w-3.5 h-3.5 text-cyan-400" />}
                          {isMuted ? 'Unmute' : 'Mute'}
                        </button>
                        <button
                          onClick={endVoiceCall}
                          className="flex-1 py-2 px-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-red-600/30"
                        >
                          <PhoneOff className="w-3.5 h-3.5" /> End Demo
                        </button>
                      </div>
                    </div>
                  )}

                  {callState === 'ended' && (
                    <div className="text-center py-2 text-xs font-bold text-cyan-400">
                      {statusMessage}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Bottom Key Features Strip */}
            <div className="pt-6 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              {selectedNiche.features.map((f, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 5 DEEP-DIVE VERTICAL SHOWCASES */}
      {/* ========================================================================= */}
      <section id="verticals" className="py-20 px-6 max-w-7xl mx-auto border-t border-slate-900">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">Tailored Vertical Suites</div>
          <h2 className="text-3xl md:text-5xl font-extrabold text-white">Built Specifically for Your Business Operations</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {NICHES.map((n) => {
            const Icon = n.icon;
            return (
              <div key={n.id} className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col justify-between hover:border-cyan-500/30 transition-all">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-900 border border-slate-700 text-slate-300">
                      {n.badgeText}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{n.title}</h3>
                  <p className="text-slate-400 text-xs leading-relaxed mb-4">{n.description}</p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  {n.features.slice(0, 3).map((feat, i) => (
                    <div key={i} className="text-xs text-slate-300 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3 h-3 text-cyan-400 shrink-0" /> {feat}
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      setSelectedNiche(n);
                      window.scrollTo({ top: document.getElementById('arena').offsetTop - 100, behavior: 'smooth' });
                    }}
                    className="mt-4 w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-bold text-cyan-400 flex items-center justify-center gap-1 transition-all"
                  >
                    Test {n.title} Live <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* ROI & REVENUE CALCULATOR */}
      {/* ========================================================================= */}
      <section id="roi" className="py-20 px-6 max-w-5xl mx-auto border-t border-slate-900">
        <div className="glass-panel-glow p-8 md:p-12 rounded-3xl border border-cyan-500/20">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <div className="inline-flex items-center gap-1.5 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Calculator className="w-4 h-4" /> Live ROI Calculator
            </div>
            <h2 className="text-3xl font-extrabold text-white">How Much Revenue Are You Missing?</h2>
            <p className="text-slate-400 text-sm mt-2">
              22% of inbound calls go unanswered during rush hours and weekends. See your potential monthly savings.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm font-semibold mb-2">
                  <span className="text-slate-300">Daily Inbound Calls:</span>
                  <span className="text-cyan-400 font-bold">{dailyCalls} calls / day</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="300"
                  step="5"
                  value={dailyCalls}
                  onChange={(e) => setDailyCalls(Number(e.target.value))}
                  className="w-full accent-cyan-400 bg-slate-800 rounded-lg h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm font-semibold mb-2">
                  <span className="text-slate-300">Average Customer Value:</span>
                  <span className="text-emerald-400 font-bold">${avgTicketValue}</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="2000"
                  step="25"
                  value={avgTicketValue}
                  onChange={(e) => setAvgTicketValue(Number(e.target.value))}
                  className="w-full accent-emerald-400 bg-slate-800 rounded-lg h-2"
                />
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl text-center space-y-4 shadow-xl">
              <div>
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Estimated Monthly Recovered Revenue</div>
                <div className="text-4xl font-black text-emerald-400 mt-1">${recoveredRevenue.toLocaleString()} / mo</div>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800 text-left">
                <div>
                  <div className="text-xs text-slate-400">Missed Calls Saved</div>
                  <div className="text-xl font-bold text-white">{missedCallsPerMonth} calls</div>
                </div>
                <div>
                  <div className="text-xs text-slate-400">Staff Time Saved</div>
                  <div className="text-xl font-bold text-white">{hoursSavedPerMonth} hours</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* PRICING */}
      {/* ========================================================================= */}
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto border-t border-slate-900">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">Transparent Pricing</div>
          <h2 className="text-3xl md:text-5xl font-extrabold text-white">Simple Plans That Scale With Your Call Volume</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel p-8 rounded-3xl border border-slate-800 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Starter</h3>
              <p className="text-slate-400 text-xs mb-6">For single-location boutique clinics, realtors, and restaurants.</p>
              <div className="text-4xl font-black text-white mb-6">
                $99 <span className="text-xs text-slate-400 font-normal">/ month</span>
              </div>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> 300 Included Voice Minutes</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> 1 Dedicated US Phone Number</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Calendar & Appointment Booking</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> WebChat Embeddable Widget</li>
              </ul>
            </div>
            <a href="#arena" className="mt-8 w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs text-center transition-all">
              Test Agent
            </a>
          </div>

          <div className="glass-panel-glow p-8 rounded-3xl border border-cyan-500/40 flex flex-col justify-between relative">
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-[10px] font-black uppercase tracking-wider text-slate-950 shadow-md">
              Most Popular
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Professional</h3>
              <p className="text-slate-400 text-xs mb-6">For high-traffic agencies, car rental fleets, and busy law offices.</p>
              <div className="text-4xl font-black text-cyan-400 mb-6">
                $299 <span className="text-xs text-slate-400 font-normal">/ month</span>
              </div>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> 1,200 Included Voice Minutes</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Multi-Persona Vertical Switching</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Full CRM Sync (Twenty, HubSpot, GHL)</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Live Warm Call Transfer via SIP</li>
              </ul>
            </div>
            <a href="#arena" className="mt-8 w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-black text-xs text-center shadow-lg shadow-cyan-500/30 hover:brightness-110 transition-all">
              Start Free Demo Call
            </a>
          </div>

          <div className="glass-panel p-8 rounded-3xl border border-slate-800 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Enterprise</h3>
              <p className="text-slate-400 text-xs mb-6">For hospital networks, call centers, and multi-tenant franchises.</p>
              <div className="text-4xl font-black text-white mb-6">
                $799 <span className="text-xs text-slate-400 font-normal">/ month</span>
              </div>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> 4,000 Included Voice Minutes</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Custom Voice Cloning & Brand Tone</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> Dedicated SIP Trunk & BYOK Twilio</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" /> 24/7 Priority SLA & Onboarding</li>
              </ul>
            </div>
            <a href="#arena" className="mt-8 w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs text-center transition-all">
              Contact Sales
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-12 px-6 bg-[#030508] text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3.5">
            <img src="/logo.png" alt="A.L.F.I.E Logo" className="w-7 h-7 object-contain" />
            <span className="text-slate-300 font-bold text-sm">A.L.F.I.E Voice AI</span>
            <span>© 2026 All Rights Reserved.</span>
          </div>

          <div className="flex items-center gap-6">
            <a href="http://localhost:5173" target="_blank" rel="noreferrer" className="hover:text-cyan-400 transition-colors">Super Admin</a>
            <a href="http://localhost:5174" target="_blank" rel="noreferrer" className="hover:text-cyan-400 transition-colors">Client Portal</a>
            <a href="#arena" className="hover:text-cyan-400 transition-colors">Test Voice Agent</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
