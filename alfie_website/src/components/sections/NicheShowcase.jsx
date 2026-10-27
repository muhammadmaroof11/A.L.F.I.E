import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Scissors,
  Stethoscope, 
  Scale, 
  Car, 
  Building2, 
  Hotel, 
  ArrowRight, 
  PhoneCall, 
  CheckCircle2,
  Volume2,
  Play,
  Square,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import ScrollReveal from '../shared/ScrollReveal';
import SpotlightCard from '../shared/SpotlightCard';
import WaveformEqualizer from '../ui/WaveformEqualizer';
import { Button } from '../ui/button';
import { BorderBeam } from '../ui/border-beam';

const niches = [
  {
    id: 'clinic',
    name: 'Medical & Dental Clinics',
    headline: 'Real-Time Dental Insurance Verification & Chair Booking',
    desc: 'Sarah verifies patient insurance (Delta Dental, Cigna, MetLife) in under 65ms, checks open chair times, and schedules high-margin procedures 24/7.',
    icon: Stethoscope,
    videoUrl: '/assets/robot_avatars/clinic_avatar_2.webm',
    posterUrl: '/assets/posters/clinic_avatar_2.jpg',
    photoUrl: '/assets/industry_photos/clinics/niche_clinic_consult.webp',
    avatar: '/assets/industry_photos/clinics/clinic_female.webp',
    personaName: 'Sarah Jenkins',
    roleTitle: 'Clinical Scheduling Coordinator',
    routePath: '/clinics',
    features: [
      'In-network insurance validation in under 65ms',
      'Direct EMR chair opening check & instant slot lock',
      'Pre-op preparation & clinic parking directions SMS'
    ],
    sampleDialogue: '"Good morning! Yes, your Delta Dental PPO is 100% in-network with Dr. Miller. I have 2:30 PM open today—I’ve reserved that slot and texted your confirmation."'
  },
  {
    id: 'legal',
    name: 'Personal Injury Law',
    headline: 'Qualifies Retainers & Warm-Transfers to Attorney Cell',
    desc: 'Elena triages accident dates, liability merits, and police report status. High-value catastrophic cases trigger an immediate SMS case brief and live phone transfer.',
    icon: Scale,
    videoUrl: '/assets/robot_avatars/law_avatar.webm',
    posterUrl: '/assets/posters/law_avatar.jpg',
    photoUrl: '/assets/industry_photos/law_firms/law2.webp',
    avatar: '/assets/industry_photos/law_firms/law_female.webp',
    personaName: 'Elena Vance',
    roleTitle: 'Intake Paralegal Specialist',
    routePath: '/law-firms',
    features: [
      'Statute of limitations & accident liability assessment',
      'Pre-transfer SMS sent 1s before partner mobile rings',
      'Direct integration with Clio, Smokeball, and Filevine'
    ],
    sampleDialogue: '"I understand completely, Mr. Davis. Since the opposing driver ran the red light, liability is clear. Let me send a brief to Attorney Sterling and connect you right now."'
  },
  {
    id: 'carrental',
    name: 'Luxury Fleet & Chauffeur',
    headline: 'Instant Distance Mileage Pricing & Stripe Deposit Text',
    desc: 'Chloe calculates dynamic flat-rate airport transfers, checks luxury vehicle availability (Escalade ESV, S-Class), and texts instant Stripe deposit links.',
    icon: Car,
    videoUrl: '/assets/robot_avatars/car_rental_avatar.webm',
    posterUrl: '/assets/posters/car_rental_avatar.jpg',
    photoUrl: '/assets/industry_photos/car_rental/niche_fleet_vip.webp',
    avatar: '/assets/industry_photos/car_rental/carrental_female.webp',
    personaName: 'Chloe Bennett',
    roleTitle: 'VIP Fleet Dispatcher',
    routePath: '/car-rental',
    features: [
      'Dynamic mileage and toll calculation in under 65ms',
      'Vehicle tier availability (Cadillac Escalade, Mercedes S-Class)',
      'Automated Stripe deposit SMS with 1-click Apple Pay'
    ],
    sampleDialogue: '"Thank you for choosing Blackline VIP. For JFK Airport to The Plaza Hotel in a 2026 Cadillac Escalade ESV, your rate is $240 flat. I just texted your deposit link."'
  },
  {
    id: 'realestate',
    name: 'Real Estate Brokerages',
    headline: 'MLS Inventory Matching & Private Showing Tour Booking',
    desc: 'Marcus answers buyer inquiries from Zillow and yard signs, validates financing pre-approval, and books private tours into the listing agent’s calendar.',
    icon: Building2,
    videoUrl: '/assets/robot_avatars/real_estate_avatar.webm',
    posterUrl: '/assets/posters/real_estate_avatar.jpg',
    photoUrl: '/assets/industry_photos/real_estate/niche_realestate_luxury.webp',
    avatar: '/assets/industry_photos/real_estate/realestate_male.webp',
    personaName: 'Marcus Sterling',
    roleTitle: 'Listing Concierge Specialist',
    routePath: '/real-estate',
    features: [
      'Real-time MLS database lookup by address and MLS ID',
      'Jumbo pre-approval & cash buyer qualification',
      'Private showing tour calendar coordination & brochure SMS'
    ],
    sampleDialogue: '"Welcome to Prestige Realty. The 5th Avenue Penthouse is available for viewing. I have scheduled a walkthrough this Thursday at 4:00 PM and texted your brochure."'
  },
  {
    id: 'hospitality',
    name: 'Fine Hospitality & Dining',
    headline: 'Table Reservation Intake, VIP Profiling & Special Requests',
    desc: 'Julian handles table reservations, dietary preferences, wine pairings, and private room buyout requests for upscale restaurants and boutique resorts.',
    icon: Hotel,
    videoUrl: '/assets/robot_avatars/hospitality_avatar.webm',
    posterUrl: '/assets/posters/hospitality_avatar.jpg',
    photoUrl: '/assets/industry_photos/hospitality/niche_hospitality_dining.webp',
    avatar: '/assets/industry_photos/hospitality/hospitality_male.webp',
    personaName: 'Julian Rossi',
    roleTitle: 'Maitre D’ & Guest Relations',
    routePath: '/hospitality',
    features: [
      'Real-time table seating allocation & party size check',
      'VIP guest profile & dietary allergy logging',
      'Direct SevenRooms, OpenTable, and Resy calendar sync'
    ],
    sampleDialogue: '"Good evening, The Grand Meridian dining room. I have a booth available for four guests at 7:30 PM this Friday. I’ve reserved your table and noted your anniversary."'
  }
];

export default function NicheShowcase({ onSelectNiche }) {
  const [activeNicheId, setActiveNicheId] = useState('clinic');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const activeNiche = niches.find(n => n.id === activeNicheId) || niches[0];

  useEffect(() => {
    setIsPlayingAudio(false);
  }, [activeNicheId]);

  const handleTestVoice = (nicheId) => {
    if (onSelectNiche) {
      onSelectNiche(nicheId);
    } else {
      const el = document.getElementById('demo-arena');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="niche-showcase" className="py-24 bg-white text-slate-900 relative overflow-hidden border-b border-slate-200">
      
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-6xl h-[600px] bg-slate-100/50 rounded-full blur-3xl pointer-events-none opacity-30" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Industry Voice Personas
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Trained for your specific business vertical
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Pre-configured with industry terminology, booking calendars, and custom service menus right out of the box.
          </p>

          {/* Clean Segmented Tab Switcher with Motion layoutId */}
          <div className="flex flex-wrap justify-center gap-2 pt-6">
            {niches.map((niche) => {
              const Icon = niche.icon;
              const isSelected = activeNicheId === niche.id;
              return (
                <button
                  key={niche.id}
                  type="button"
                  onClick={() => setActiveNicheId(niche.id)}
                  className={`relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                    isSelected
                      ? 'text-white'
                      : 'text-slate-400 hover:text-slate-900'
                  }`}
                >
                  {isSelected && (
                    <motion.div
                      layoutId="nicheStudioTab"
                      className="absolute inset-0 bg-slate-900 rounded-xl -z-10"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-white' : 'text-slate-600'}`} />
                  <span>{niche.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Industry Studio Card */}
        <ScrollReveal y={20} duration={0.6}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeNiche.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
              className="max-w-5xl mx-auto"
            >
              <SpotlightCard className="p-8 sm:p-10 border-slate-200/80 shadow-sm relative bg-white">
                <BorderBeam size={160} duration={10} colorFrom="#94a3b8" colorTo="#cbd5e1" />

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
                  
                  {/* Left Column: Persona Details & Voice Player */}
                  <div className="lg:col-span-7 space-y-6">
                    
                    {/* Persona Header */}
                    <div className="flex items-center gap-3">
                      <img
                        src={activeNiche.avatar}
                        alt={activeNiche.personaName}
                        className="w-12 h-12 rounded-2xl object-cover border-2 border-slate-300 shadow-sm"
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-extrabold text-base text-slate-900 font-heading">
                            {activeNiche.personaName}
                          </h4>
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        </div>
                        <p className="text-xs text-slate-600 font-semibold font-mono">{activeNiche.roleTitle}</p>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-heading leading-snug">
                        {activeNiche.headline}
                      </h3>
                      <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                        {activeNiche.desc}
                      </p>
                    </div>

                    {/* 3 Features */}
                    <div className="space-y-2.5 pt-2 border-t border-slate-200">
                      {activeNiche.features.map((feat, idx) => (
                        <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>

                    {/* Interactive Spoken Voice Player Box */}
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 relative">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-slate-900 font-mono">
                          <Volume2 className="w-4 h-4 text-slate-600" />
                          <span>Spoken Voice Simulation:</span>
                        </div>

                        {/* Interactive Waveform & Play Trigger */}
                        <div className="flex items-center gap-3">
                          <div className="w-24">
                            <WaveformEqualizer 
                              isActive={isPlayingAudio} 
                              barCount={14} 
                              className="h-4"
                              activeColor="bg-slate-800" 
                              idleColor="bg-slate-300"
                            />
                          </div>

                          <button
                            type="button"
                            onClick={() => setIsPlayingAudio(!isPlayingAudio)}
                            className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-700 hover:text-blue-600 hover:border-blue-300 flex items-center gap-1 shadow-sm cursor-pointer"
                          >
                            {isPlayingAudio ? (
                              <>
                                <Square className="w-3 h-3 fill-current text-rose-400" />
                                <span>Pause</span>
                              </>
                            ) : (
                              <>
                                <Play className="w-3 h-3 fill-current text-slate-600" />
                                <span>Sample</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>

                      <p className={`text-xs italic leading-relaxed transition-colors ${
                        isPlayingAudio ? 'text-blue-700 font-medium' : 'text-slate-600'
                      }`}>
                        {activeNiche.sampleDialogue}
                      </p>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-wrap items-center gap-3 pt-2">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleTestVoice(activeNiche.id)}
                        className="gap-2 text-xs font-bold shadow-sm cursor-pointer"
                      >
                        <PhoneCall className="w-3.5 h-3.5 text-white" />
                        <span>Test Voice in Browser</span>
                      </Button>

                      {activeNiche.routePath.startsWith('/') && !activeNiche.routePath.startsWith('/#') && (
                        <Link to={activeNiche.routePath}>
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 border-white/15"
                          >
                            <span>Learn More About {activeNiche.name.split(' ')[0]}</span>
                            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                          </Button>
                        </Link>
                      )}
                    </div>

                  </div>

                  {/* Right Column: Visual Preview */}
                  <div className="lg:col-span-5 flex flex-col justify-center">
                    <div className="rounded-3xl overflow-hidden border border-slate-200/80 bg-slate-50 relative shadow-sm aspect-4/3 group flex items-center justify-center">
                      {activeNiche.videoUrl ? (
                        <video
                          key={activeNiche.videoUrl}
                          autoPlay
                          loop
                          muted
                          playsInline
                          poster={activeNiche.posterUrl}
                          className="w-full h-full object-contain pointer-events-none"
                        >
                          <source src={activeNiche.videoUrl} type="video/webm" />
                        </video>
                      ) : (
                        <img 
                          src={activeNiche.photoUrl} 
                          alt={activeNiche.name} 
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105 opacity-90"
                        />
                      )}
                      <div className="absolute inset-0 bg-gradient-to-t from-white/90 via-transparent to-transparent flex items-end p-5 pointer-events-none">
                        <div className="text-slate-900">
                          <span className="text-[10px] font-mono font-bold text-cyan-700 uppercase tracking-wider block mb-0.5">
                            {activeNiche.name}
                          </span>
                          <p className="text-sm font-extrabold font-heading text-slate-900">{activeNiche.personaName}</p>
                          <p className="text-[11px] text-slate-500 font-mono">{activeNiche.roleTitle}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </SpotlightCard>
            </motion.div>
          </AnimatePresence>
        </ScrollReveal>

      </div>
    </section>
  );
}
