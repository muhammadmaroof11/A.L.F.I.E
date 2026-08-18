import React, { useState } from 'react';
import { Scale, Stethoscope, Car, Building2, Hotel, ArrowRight, PhoneCall, Terminal, Video, Box, Volume2, ShieldCheck } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import ModelViewer from '../3d/ModelViewer';

const niches = [
  {
    id: 'legal',
    name: 'Personal Injury Law',
    subtitle: 'Autonomous $10k+ Retainer Triage & Partner Phone Bridge',
    badge: 'Legal Intake Engine',
    icon: Scale,
    tagColor: 'bg-amber-50 text-amber-800 border-amber-200',
    modelUrl: '/models/niche_legal.glb',
    videoUrl: '/videos/legal_intake.mp4',
    photoUrl: '/images/niche_legal_detail.jpeg',
    avatarF: '/avatars/law_female.jpg',
    avatarM: '/avatars/law_male.jpg',
    personaName: 'Elena Vance (Intake Paralegal)',
    lossReality: '84% of injured callers hang up and call the next firm if put on hold.',
    toolExecutions: [
      { fn: 'verify_statute_of_limitations', arg: 'state="CA", accident_date="2026-07-14"', result: 'VALID (710 days remaining)', time: '42ms' },
      { fn: 'triage_liability_merits', arg: 'police_report=True, liability="Opposing Driver Ran Red Light"', result: 'HIGH VALUE LEAD ($45k+ EST)', time: '110ms' },
      { fn: 'dispatch_pre_transfer_sms', arg: 'to="+1 (415) 890-1234", brief="Rear-End Injury | Merits Clear"', result: 'DELIVERED', time: '180ms' },
      { fn: 'bridge_sip_live_call', arg: 'target="Partner_iPhone", timeout=25', result: 'CONNECTED (Warm Bridge)', time: '210ms' }
    ],
    scriptSnippet: '"I understand completely, Mr. Davis. Since the opposing driver ran the red light, liability is clear. Let me send a brief to Attorney Sterling and connect you directly right now."'
  },
  {
    id: 'clinic',
    name: 'Medical & Dental Clinics',
    subtitle: 'Real-Time Insurance Network Validation & EMR Scheduling',
    badge: 'Clinical Reception Desk',
    icon: Stethoscope,
    tagColor: 'bg-sky-50 text-sky-800 border-sky-200',
    modelUrl: '/models/niche_clinic.glb',
    videoUrl: '/videos/clinic_demo.mp4',
    photoUrl: '/images/niche_clinic_consult.jpeg',
    avatarF: '/avatars/clinic_female.jpg',
    avatarM: '/avatars/clinic_male.jpg',
    personaName: 'Sarah Jenkins (Clinic Coordinator)',
    lossReality: 'Front desk busy signals lose high-margin dental implant & aesthetic patients.',
    toolExecutions: [
      { fn: 'lookup_insurance_carrier', arg: 'payer="Delta Dental PPO", subscriber_id="D9812498"', result: 'IN-NETWORK (Tier 1)', time: '65ms' },
      { fn: 'query_doctor_calendar', arg: 'provider="Dr. Miller", date="2026-08-18"', result: 'OPENINGS: [14:30, 16:15]', time: '82ms' },
      { fn: 'book_emr_appointment', arg: 'patient="Sarah Lynn", time="14:30", type="Root Canal"', result: 'RESERVED (Slot #892)', time: '140ms' },
      { fn: 'dispatch_pre_op_sms', arg: 'to="+1 (212) 555-0199", template="Fast_Reminder"', result: 'DELIVERED', time: '190ms' }
    ],
    scriptSnippet: '"Good morning! Yes, your Delta Dental PPO is 100% in-network with Dr. Miller. I have 2:30 PM open today—I have locked that into your calendar and texted your parking instructions."'
  },
  {
    id: 'carrental',
    name: 'Luxury Fleet & Chauffeur',
    subtitle: 'Instant Dynamic Distance Routing & Chauffeur Dispatch',
    badge: 'Fleet Dispatch Desk',
    icon: Car,
    tagColor: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    modelUrl: '/models/niche_carrental.glb',
    videoUrl: null,
    photoUrl: '/images/niche_fleet_vip.jpeg',
    avatarF: '/avatars/carrental_female.jpg',
    avatarM: '/avatars/carrental_male.jpg',
    personaName: 'Chloe Bennett (VIP Dispatcher)',
    lossReality: 'Airport VIP travelers require an instant fixed quote in under 15 seconds.',
    toolExecutions: [
      { fn: 'calculate_osrm_route', arg: 'origin="JFK Terminal 4", dest="The Plaza Hotel Manhattan"', result: '18.4 mi • 42 mins', time: '55ms' },
      { fn: 'quote_vehicle_tier', arg: 'tier="Cadillac Escalade ESV", rate_card="VIP_Tier"', result: '$240.00 Flat Rate', time: '30ms' },
      { fn: 'send_stripe_deposit_link', arg: 'amount=$50.00, phone="+1 (917) 555-8821"', result: 'SMS SENT', time: '160ms' }
    ],
    scriptSnippet: '"Thank you for choosing Blackline Transport. For JFK to The Plaza Hotel in a 2026 Cadillac Escalade ESV, your rate is $240 flat. I just texted your confirmation link."'
  },
  {
    id: 'realestate',
    name: 'Real Estate Brokerages',
    subtitle: 'High-Ticket MLS Property Matching & Private Tour Coordination',
    badge: 'Realty Concierge',
    icon: Building2,
    tagColor: 'bg-blue-50 text-blue-800 border-blue-200',
    modelUrl: '/models/niche_realestate.glb',
    videoUrl: null,
    photoUrl: '/images/brand_hero_nexus.jpeg',
    avatarF: '/avatars/realestate_female.jpg',
    avatarM: '/avatars/realestate_male.jpg',
    personaName: 'Marcus Sterling (Listing Specialist)',
    lossReality: 'Zillow & buyer inquiries bounce to the next listing agent if not confirmed immediately.',
    toolExecutions: [
      { fn: 'query_mls_inventory', arg: 'mls_id="NYC-8821", min_price=3500000', result: 'ACTIVE (Penthouse 4B)', time: '75ms' },
      { fn: 'verify_pre_approval', arg: 'financing="Jumbo Pre-Approved / Cash Proof"', result: 'VERIFIED HIGH INTENT', time: '40ms' },
      { fn: 'schedule_showing_tour', arg: 'agent="Julian Vance", time="Thursday 4:00 PM"', result: 'CALENDAR INVITE SENT', time: '120ms' }
    ],
    scriptSnippet: '"Welcome to Prestige Realty. The 5th Avenue Penthouse is available for private viewing. I have scheduled a walkthrough with our listing partner this Thursday at 4:00 PM."'
  },
  {
    id: 'hospitality',
    name: 'Fine Hospitality & Dining',
    subtitle: 'Dynamic Table Inventory & VIP Concierge Booking',
    badge: 'Concierge Engine',
    icon: Hotel,
    tagColor: 'bg-purple-50 text-purple-800 border-purple-200',
    modelUrl: '/models/niche_hospitality.glb',
    videoUrl: null,
    photoUrl: '/images/niche_clinic_lounge.jpeg',
    avatarF: '/avatars/hospitality_female.jpg',
    avatarM: '/avatars/hospitality_male.jpg',
    personaName: 'Julian Rossi (Maitre D)',
    lossReality: 'Peak Friday 7:00 PM phone rings are ignored while hosts are seating dinner parties.',
    toolExecutions: [
      { fn: 'check_table_inventory', arg: 'party_size=4, time="19:30", section="Main Dining"', result: 'AVAILABLE (Table 14)', time: '35ms' },
      { fn: 'log_vip_preferences', arg: 'anniversary=True, dietary="Nut Allergy, Champagne Pref"', result: 'RECORDED IN POS', time: '60ms' },
      { fn: 'dispatch_sms_confirmation', arg: 'phone="+1 (312) 555-4921", dress_code="Smart Casual"', result: 'SMS DISPATCHED', time: '140ms' }
    ],
    scriptSnippet: '"Good evening, The Grand Meridian. I have reserved Table 14 for your party of 4 this evening at 7:30 PM, and logged your champagne anniversary preference with the chef."'
  }
];

export default function NicheShowcase({ onSelectNiche }) {
  const [selectedTab, setSelectedTab] = useState(niches[0].id);
  const activeNiche = niches.find(n => n.id === selectedTab) || niches[0];

  return (
    <section id="niche-showcase" className="py-20 bg-white border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
            <span>Specialized Vertical Toolsets</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Trained on Industry Playbooks, Not Generic Chit-Chat
          </h2>
          <p className="text-sm sm:text-base text-slate-600">
            Each A.L.F.I.E node connects to industry database schemas with deterministic tool calling and compliance guardrails.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center justify-start sm:justify-center gap-2 overflow-x-auto pb-3 mb-8 no-scrollbar">
          {niches.map((n) => {
            const TabIcon = n.icon;
            const isSelected = selectedTab === n.id;
            return (
              <button
                key={n.id}
                onClick={() => setSelectedTab(n.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap cursor-pointer ${
                  isSelected
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70 hover:text-slate-900'
                }`}
              >
                <TabIcon className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-300' : 'text-slate-500'}`} />
                <span>{n.name}</span>
                {n.videoUrl && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" title="Commercial Reel Available" />
                )}
              </button>
            );
          })}
        </div>

        {/* Master Mission Control Display */}
        <ScrollReveal y={20} duration={0.6}>
          <div className="bg-[#FAFAFC] rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
              
              {/* Left Column: Live Tool Execution Console */}
              <div className="lg:col-span-7 space-y-5 flex flex-col justify-between">
                
                <div className="space-y-4">
                  {/* Persona Header */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold border ${activeNiche.tagColor}`}>
                          {activeNiche.badge}
                        </span>
                        <span className="text-xs font-bold text-slate-800">
                          {activeNiche.personaName}
                        </span>
                      </div>
                      <h3 className="text-lg sm:text-xl font-extrabold text-slate-900 mt-1">
                        {activeNiche.subtitle}
                      </h3>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <img 
                        src={activeNiche.avatarF} 
                        alt="Persona Portrait" 
                        className="w-8 h-8 rounded-full object-cover border border-slate-300 shadow-2xs" 
                      />
                      <img 
                        src={activeNiche.avatarM} 
                        alt="Persona Male" 
                        className="w-8 h-8 rounded-full object-cover border border-slate-300 shadow-2xs" 
                      />
                    </div>
                  </div>

                  {/* Natural Spoken Quote */}
                  <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
                    <p className="text-[10px] font-mono font-bold text-blue-600 uppercase tracking-wider flex items-center gap-1.5">
                      <Volume2 className="w-3 h-3 text-blue-600" />
                      <span>Natural Spoken Cadence:</span>
                    </p>
                    <p className="text-slate-800 italic leading-relaxed">
                      {activeNiche.scriptSnippet}
                    </p>
                  </div>

                  {/* Live Tool Execution Terminal */}
                  <div className="bg-slate-900 rounded-2xl p-4 text-white font-mono text-xs space-y-2.5 shadow-inner">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1.5 font-bold text-slate-300">
                        <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Sub-Second Telephony Tool Executions</span>
                      </span>
                      <span className="text-[10px] text-emerald-400 font-semibold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                        Zero Hallucinations
                      </span>
                    </div>

                    <div className="space-y-1.5 text-[11px]">
                      {activeNiche.toolExecutions.map((tool, idx) => (
                        <div key={idx} className="space-y-0.5 bg-slate-950/50 p-2 rounded-lg border border-slate-800/80">
                          <div className="flex items-center justify-between text-slate-300">
                            <span className="text-blue-400 font-bold">▶ {tool.fn}(<span className="text-slate-400 font-normal">{tool.arg}</span>)</span>
                            <span className="text-[10px] text-slate-500">{tool.time}</span>
                          </div>
                          <div className="text-emerald-400 pl-4 font-semibold text-[10px]">
                            ↳ {tool.result}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Bottom CTA */}
                <div className="pt-2">
                  <button
                    onClick={() => {
                      if (onSelectNiche) onSelectNiche(activeNiche.id);
                      const demo = document.getElementById('demo-arena');
                      if (demo) demo.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="btn-primary text-xs py-2.5 px-5 rounded-xl w-full sm:w-auto"
                  >
                    <PhoneCall className="w-3.5 h-3.5 text-blue-300" />
                    <span>Test This {activeNiche.name} Persona in Browser</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

              </div>

              {/* Right Column: High-Impact Video Cinema / Photography Theater */}
              <div className="lg:col-span-5 flex flex-col justify-center">
                <div className="w-full h-full min-h-[320px] rounded-2xl bg-slate-900 border border-slate-800 shadow-md overflow-hidden relative group flex items-center justify-center">
                  
                  {activeNiche.videoUrl ? (
                    <video
                      key={activeNiche.videoUrl}
                      autoPlay
                      loop
                      muted
                      playsInline
                      className="w-full h-full object-cover min-h-[320px]"
                    >
                      <source src={activeNiche.videoUrl} type="video/mp4" />
                    </video>
                  ) : (
                    <img
                      src={activeNiche.photoUrl}
                      alt={activeNiche.name}
                      className="w-full h-full object-cover min-h-[320px]"
                    />
                  )}

                  {/* Cinema Badge Overlay */}
                  <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-3 py-1 rounded-lg border border-white/10 text-white text-[10px] font-mono font-bold flex items-center gap-1.5 z-10">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <span>{activeNiche.videoUrl ? 'Veo 3.1 Commercial Reel' : 'Field Operations Showcase'}</span>
                  </div>

                  <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-slate-950/90 via-slate-950/30 to-transparent p-4 text-white z-10">
                    <p className="text-xs font-bold">{activeNiche.name} Deployment</p>
                    <p className="text-[10px] text-slate-300 font-mono mt-0.5">{activeNiche.lossReality}</p>
                  </div>

                </div>
              </div>

            </div>
          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
