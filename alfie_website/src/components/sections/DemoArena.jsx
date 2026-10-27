import React, { useState, useEffect, useRef } from 'react';
import { 
  Phone, 
  PhoneOff, 
  Mic, 
  MicOff, 
  Scissors,
  Scale, 
  Stethoscope, 
  Building2, 
  Car, 
  Hotel,
  Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Room, RoomEvent } from 'livekit-client';
import ScrollReveal from '../shared/ScrollReveal';
import HolographicVoiceOrb from '../ui/HolographicVoiceOrb';
import { BorderBeam } from '../ui/border-beam';
import { Button } from '../ui/button';
import { playConnectionChime, playHangupTone } from '../../lib/dtmf';

const demoNiches = [
  { id: 'clinic', name: 'Dental & Clinic', icon: Stethoscope, sampleGreeting: "Good morning! Metropolitan Dental. Are you calling to schedule a routine cleaning, or do you have an urgent tooth pain issue?" },
  { id: 'legal', name: 'Personal Injury Law', icon: Scale, sampleGreeting: "Hello, Apex Injury Law 24/7 intake. Were you or a family member injured in an accident recently?" },
  { id: 'realestate', name: 'Real Estate Brokerage', icon: Building2, sampleGreeting: "Hello, welcome to Prestige Global Realty! Are you inquiring about one of our featured listings or scheduling a private showing tour?" },
  { id: 'carrental', name: 'Luxury Fleet Dispatch', icon: Car, sampleGreeting: "Thank you for choosing Blackline VIP Transport. What is your pickup address and desired vehicle tier?" },
  { id: 'hospitality', name: 'Fine Dining & Hospitality', icon: Hotel, sampleGreeting: "Good evening, welcome to Lumière Dining. Would you like to reserve a table for tonight or enquire about our tasting menu?" },
];

export default function DemoArena({ initialNiche = 'clinic' }) {
  const [selectedNiche, setSelectedNiche] = useState(initialNiche);
  const [isCalling, setIsCalling] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [transcripts, setTranscripts] = useState([]);
  const [simulatedState, setSimulatedState] = useState('idle'); // 'idle' | 'connecting' | 'listening' | 'speaking'

  const activeDemo = demoNiches.find(n => n.id === selectedNiche) || demoNiches[0];
  const timerRef = useRef(null);
  const roomRef = useRef(null);
  const audioElementsRef = useRef([]);

  useEffect(() => {
    if (initialNiche) {
      setSelectedNiche(initialNiche);
    }
  }, [initialNiche]);

  useEffect(() => {
    if (isCalling) {
      timerRef.current = setInterval(() => {
        setCallDuration(d => {
          if (d >= 90) {
            handleEndCall();
            return 90;
          }
          return d + 1;
        });
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setCallDuration(0);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isCalling]);

  const handleStartCall = async () => {
    playConnectionChime();
    setIsCalling(true);
    setSimulatedState('connecting');
    setTranscripts([]);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/public/demo/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche: selectedNiche, visitor_name: 'Demo Prospect' }),
      });

      if (!res.ok) {
        throw new Error(`Token fetch failed: ${res.status}`);
      }

      const data = await res.json();
      const wsUrl = data.url || 'wss://alfie-ai-9ngpqe5q.livekit.cloud';
      const token = data.token;

      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });
      roomRef.current = room;

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === 'audio') {
          const audioEl = track.attach();
          audioEl.autoplay = true;
          document.body.appendChild(audioEl);
          audioElementsRef.current.push(audioEl);
        }
      });

      room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        if (speakers.length > 0) {
          const isAgent = speakers.some(s => s.identity?.includes('agent') || s.identity?.includes('alfie'));
          setSimulatedState(isAgent ? 'speaking' : 'listening');
        } else {
          setSimulatedState('listening');
        }
      });

      room.on(RoomEvent.DataReceived, (payload) => {
        try {
          const str = new TextDecoder().decode(payload);
          const parsed = JSON.parse(str);
          if (parsed.type === 'transcript') {
            setTranscripts(prev => [...prev, { speaker: parsed.speaker, text: parsed.text, time: new Date().toLocaleTimeString() }]);
          }
        } catch (e) {
          // ignore
        }
      });

      await room.connect(wsUrl, token);
      await room.localParticipant.enableCameraAndMicrophone(false, true);

      setSimulatedState('speaking');
      setTranscripts([
        { speaker: 'A.L.F.I.E', text: activeDemo.sampleGreeting, time: 'Just now' }
      ]);

    } catch (err) {
      // Fallback to simulated audio mode for pure browser testing
      setTimeout(() => {
        setSimulatedState('speaking');
        setTranscripts([
          { speaker: 'A.L.F.I.E', text: activeDemo.sampleGreeting, time: '00:01' }
        ]);
        setTimeout(() => {
          setSimulatedState('listening');
        }, 3400);
      }, 700);
    }
  };

  const handleEndCall = async () => {
    playHangupTone();
    setIsCalling(false);
    setSimulatedState('idle');
    if (roomRef.current) {
      try {
        await roomRef.current.disconnect();
      } catch (e) {
        // ignore
      }
      roomRef.current = null;
    }
    audioElementsRef.current.forEach(el => {
      try { el.remove(); } catch (e) {}
    });
    audioElementsRef.current = [];
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (roomRef.current) {
      roomRef.current.localParticipant.setMicrophoneEnabled(isMuted);
    }
  };

  const formatDuration = (sec) => {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = (sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <section id="demo-arena" className="py-24 bg-white relative overflow-hidden border-b border-slate-200/80">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Interactive Voice Demo
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Experience What Your Callers Hear
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Test A.L.F.I.E. directly through your microphone. Experience the immediate empathy, patient listening, and instant resolution that keeps clients from ever hanging up.
          </p>
        </div>

        {/* High-Tech Voice Console Container */}
        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-5xl mx-auto rounded-3xl bg-white border border-slate-200/80 shadow-lg backdrop-blur-2xl p-6 sm:p-10 relative overflow-hidden">
            
            {/* Glowing Border Beam on Container */}
            <BorderBeam size={160} duration={12} colorFrom="#94a3b8" colorTo="#cbd5e1" />

            {/* Top Bar: Selector & Connection Status */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-slate-200 relative z-10">
              
              {/* Persona Selector Tabs */}
              <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-slate-100 border border-slate-200">
                {demoNiches.map((n) => {
                  const Icon = n.icon;
                  const isSelected = selectedNiche === n.id;
                  return (
                    <button
                      key={n.id}
                      type="button"
                      disabled={isCalling}
                      onClick={() => {
                        setSelectedNiche(n.id);
                        setTranscripts([]);
                      }}
                      className={`relative flex items-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                        isSelected
                          ? 'text-white font-bold'
                          : 'text-slate-500 hover:text-slate-900 disabled:opacity-50'
                      }`}
                    >
                      {isSelected && (
                        <motion.div
                          layoutId="demoArenaTab"
                          className="absolute inset-0 bg-slate-900 rounded-lg -z-10"
                          transition={{ type: "spring", stiffness: 350, damping: 30 }}
                        />
                      )}
                      <Icon className="w-3.5 h-3.5" />
                      <span>{n.name.split(' ')[0]}</span>
                    </button>
                  );
                })}
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-200">
                <span className={`w-2 h-2 rounded-full ${
                  isCalling 
                    ? simulatedState === 'speaking' 
                    ? 'bg-blue-500 animate-pulse' 
                    : 'bg-emerald-500 animate-pulse' 
                    : 'bg-slate-400'
                }`} />
                <span className="text-xs font-mono font-bold text-slate-600">
                  {isCalling 
                    ? (simulatedState === 'speaking' ? 'A.L.F.I.E Speaking' : 'Listening...') 
                    : 'Ready to Connect'}
                </span>
              </div>
            </div>

            {/* Main Interactive Grid: Voice Orb + Understandable Caller Resolution Flow */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 my-8 items-stretch">
              
              {/* Left: Calling Screen Area with Holographic Voice Orb (7 cols) */}
              <div className="lg:col-span-7 py-8 px-6 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col items-center justify-between text-center relative overflow-hidden">
                
                {/* Central Holographic Voice Orb */}
                <div className="my-2 relative">
                  <HolographicVoiceOrb
                    state={isCalling ? simulatedState : 'idle'}
                    size={190}
                  />
                </div>

                {/* Persona Headline & Call State */}
                <div className="space-y-1 relative z-10 my-4">
                  <h3 className="font-extrabold text-xl sm:text-2xl text-slate-900 font-heading">
                    {activeDemo.name}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {isCalling 
                      ? `Call Connected • Duration: ${formatDuration(callDuration)} • Warm Human Cadence` 
                      : 'Click Start Test Call to speak via your microphone in natural full-duplex voice'}
                  </p>
                </div>

                {/* Interactive Call Actions */}
                <div className="flex items-center gap-4 relative z-10">
                  {!isCalling ? (
                    <Button
                      size="lg"
                      variant="primary"
                      onClick={handleStartCall}
                      className="gap-2.5 px-8 py-5 rounded-2xl font-extrabold text-sm cursor-pointer"
                    >
                      <Phone className="w-5 h-5 text-white animate-pulse" />
                      <span>Start Test Call in Browser</span>
                    </Button>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={toggleMute}
                        className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                          isMuted 
                            ? 'bg-amber-100 border-amber-200 text-amber-600' 
                            : 'bg-slate-100 border-slate-200 text-slate-600 hover:bg-slate-200'
                        }`}
                        title={isMuted ? 'Unmute microphone' : 'Mute microphone'}
                      >
                        {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                      </button>

                      <button
                        type="button"
                        onClick={handleEndCall}
                        className="p-3.5 rounded-2xl bg-rose-600 text-white hover:bg-rose-700 shadow-xl shadow-rose-600/30 transition-all cursor-pointer flex items-center gap-2 px-6 font-bold text-xs"
                      >
                        <PhoneOff className="w-4 h-4" />
                        <span>End Call</span>
                      </button>
                    </>
                  )}
                </div>

              </div>

              {/* Right: Relatable Caller Resolution Card (5 cols) */}
              <div className="lg:col-span-5 flex flex-col justify-between">
                <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/90 h-full flex flex-col justify-between space-y-4">
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
                      What Your Callers Experience
                    </span>
                    <h4 className="font-bold text-slate-900 text-base font-heading">
                      Immediate Human Relief
                    </h4>
                  </div>

                  {/* 4 Empathy Steps */}
                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                        1
                      </span>
                      <div>
                        <span className="font-bold text-slate-800 text-xs block">Zero Hold Time (Ring 1 Pickup)</span>
                        <span className="text-[11px] text-slate-500 leading-snug">No elevator music, no robot menus, no "press 1 for English".</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                        2
                      </span>
                      <div>
                        <span className="font-bold text-slate-800 text-xs block">Patient, Active Listening</span>
                        <span className="text-[11px] text-slate-500 leading-snug">Understands anxious or distressed callers without rushing or interrupting.</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                        3
                      </span>
                      <div>
                        <span className="font-bold text-slate-800 text-xs block">Instant Real-Time Resolution</span>
                        <span className="text-[11px] text-slate-500 leading-snug">Locks calendar appointments, qualifies cases, or warm-transfers to staff.</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                        4
                      </span>
                      <div>
                        <span className="font-bold text-slate-800 text-xs block">Immediate SMS Confirmation</span>
                        <span className="text-[11px] text-slate-500 leading-snug">Sends directions, confirmation links, or case briefs straight to the caller's phone.</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-200/70 flex items-center justify-between text-[11px] font-mono text-slate-500">
                    <span>Trained on your industry</span>
                    <span className="text-emerald-600 font-bold">● 24/7/365 Always Ready</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Live Transcript Stream Cards */}
            <AnimatePresence>
              {transcripts.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-6 p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-2.5 max-h-48 overflow-y-auto"
                >
                  <div className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Live Conversation Transcript</span>
                    <span className="text-emerald-500">● Streaming</span>
                  </div>
                  {transcripts.map((t, idx) => (
                    <motion.div 
                      key={idx} 
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-start gap-2 text-slate-700"
                    >
                      <span className="font-bold font-mono text-slate-900 shrink-0">{t.speaker}:</span>
                      <span className="leading-relaxed">{t.text}</span>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Relatable Business Relief Strip */}
            <div className="mt-8 pt-6 border-t border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-xs font-mono text-slate-600">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 shadow-2xs">
                <span className="block text-[10px] text-slate-400 uppercase font-semibold">First-Ring Response</span>
                <span className="font-bold text-slate-900 text-sm sm:text-base">0s Hold Time</span>
                <span className="text-[10px] text-slate-500 block">Never hits voicemail</span>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 shadow-2xs">
                <span className="block text-[10px] text-slate-400 uppercase font-semibold">After-Hours Capture</span>
                <span className="font-bold text-slate-900 text-sm sm:text-base">100% Coverage</span>
                <span className="text-[10px] text-slate-500 block">Nights, weekends & holidays</span>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 shadow-2xs">
                <span className="block text-[10px] text-slate-400 uppercase font-semibold">Staff Burnout</span>
                <span className="font-bold text-emerald-600 text-sm sm:text-base">Eliminated</span>
                <span className="text-[10px] text-slate-500 block">Front desk focus on in-person</span>
              </div>
              <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 shadow-2xs">
                <span className="block text-[10px] text-emerald-600 font-semibold uppercase">Lost Revenue</span>
                <span className="font-extrabold text-sm sm:text-base text-emerald-700">$0 Given Away</span>
                <span className="text-[10px] text-emerald-600 block">Captures ready-to-buy callers</span>
              </div>
            </div>

          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
