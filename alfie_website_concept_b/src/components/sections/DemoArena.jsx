import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Mic, MicOff, Volume2, Activity, Shield, Scale, Stethoscope, Building2, Car, Hotel, CheckCircle, ArrowRight, Zap, RefreshCw, Radio } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';

const demoNiches = [
  { id: 'legal', name: 'Personal Injury Law', icon: Scale, sampleGreeting: "Hello, thank you for calling Apex Injury Law. I am your 24/7 intake paralegal. Were you injured in an accident recently?" },
  { id: 'clinic', name: 'Dental & Medical Clinic', icon: Stethoscope, sampleGreeting: "Good morning! Thank you for calling Metropolitan Dental. Are you calling to book a routine cleaning or do you have an urgent dental issue?" },
  { id: 'realestate', name: 'Real Estate Brokerage', icon: Building2, sampleGreeting: "Hello, welcome to Prestige Global Realty! Are you inquiring about one of our featured listings or scheduling a private showing?" },
  { id: 'carrental', name: 'Luxury Fleet Dispatch', icon: Car, sampleGreeting: "Thank you for choosing Blackline VIP Transport. What is your pickup address and desired vehicle tier?" },
  { id: 'hospitality', name: 'Fine Hospitality Concierge', icon: Hotel, sampleGreeting: "Good evening, The Grand Meridian dining room. How many guests will be joining us this evening?" },
];

export default function DemoArena({ initialNiche = 'legal' }) {
  const [selectedNiche, setSelectedNiche] = useState(initialNiche);
  const [isCalling, setIsCalling] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [transcripts, setTranscripts] = useState([]);
  const [simulatedState, setSimulatedState] = useState('idle');

  const activeDemo = demoNiches.find(n => n.id === selectedNiche) || demoNiches[0];
  const timerRef = useRef(null);

  useEffect(() => {
    if (initialNiche) {
      setSelectedNiche(initialNiche);
    }
  }, [initialNiche]);

  useEffect(() => {
    if (isCalling) {
      setSimulatedState('connecting');
      timerRef.current = setInterval(() => {
        setCallDuration(d => {
          if (d >= 90) {
            handleEndCall();
            return 90;
          }
          return d + 1;
        });
      }, 1000);

      const t1 = setTimeout(() => {
        setSimulatedState('speaking');
        setTranscripts([
          { speaker: 'A.L.F.I.E', text: activeDemo.sampleGreeting, time: '0:02' }
        ]);
      }, 1200);

      const t2 = setTimeout(() => {
        setSimulatedState('listening');
      }, 4500);

      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
      };
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setCallDuration(0);
      setSimulatedState('idle');
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isCalling, selectedNiche]);

  const handleStartCall = () => {
    setIsCalling(true);
  };

  const handleEndCall = () => {
    setIsCalling(false);
    setSimulatedState('idle');
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <section id="demo-arena" className="py-20 bg-[#091728] border-b border-white/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white/[0.05] text-[#CBD5E1] border border-white/[0.06]">
            <Radio className="w-3.5 h-3.5 text-[#38BDF8] animate-pulse" />
            <span>Interactive WebRTC Telephony Sandbox</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC] tracking-tight">
            Test A.L.F.I.E Live In Your Browser
          </h2>
          <p className="text-sm sm:text-base text-[#94A3B8]">
            Select a specialized vertical, enable your microphone, and experience sub-second human conversational voice AI in real time.
          </p>
        </div>

        {/* Niche Selector Pills */}
        <div className="flex items-center justify-center gap-2 flex-wrap mb-8">
          {demoNiches.map((n) => {
            const Icon = n.icon;
            const isSelected = selectedNiche === n.id;
            return (
              <button
                key={n.id}
                disabled={isCalling}
                onClick={() => {
                  setSelectedNiche(n.id);
                  setTranscripts([]);
                }}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-slate-900 text-white shadow-[0_2px_8px_rgba(0,0,0,0.3)]'
                    : 'bg-white/[0.05] text-[#94A3B8] hover:bg-slate-200 hover:text-[#F8FAFC]'
                } ${isCalling ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-300' : 'text-[#64748B]'}`} />
                <span>{n.name}</span>
              </button>
            );
          })}
        </div>

        {/* Live Call Console Card */}
        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-3xl mx-auto bg-[#0B0F17] rounded-3xl border border-white/[0.06] p-6 sm:p-8 shadow-[0_2px_8px_rgba(0,0,0,0.3)]">
            
            {/* Top Console Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-white/[0.06]">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-sm">
                  A
                </div>
                <div>
                  <h3 className="font-extrabold text-[#F8FAFC] text-sm sm:text-base">
                    {activeDemo.name} Voice Node
                  </h3>
                  <p className="text-[11px] text-[#64748B] font-mono">
                    Deepgram Nova-2 + LiveKit Cloud SIP Bridge
                  </p>
                </div>
              </div>

              {/* Timer Pill */}
              <div className="flex items-center gap-2">
                {isCalling && (
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/15 text-xs font-mono font-bold">
                    <span className="w-2 h-2 rounded-full bg-red-600 animate-ping" />
                    <span>{formatTime(callDuration)} / 1:30</span>
                  </div>
                )}
                <div className="text-[11px] font-mono font-semibold text-[#64748B] bg-[#091728] px-2.5 py-1 rounded-lg border border-white/[0.06]">
                  TTFT: 390ms
                </div>
              </div>
            </div>

            {/* Middle Stage Area */}
            <div className="py-8 min-h-[200px] flex flex-col justify-center items-center">
              {!isCalling ? (
                <div className="text-center space-y-3">
                  <div className="w-14 h-14 rounded-2xl bg-[#091728] border border-white/[0.06] text-[#E2E8F0] mx-auto flex items-center justify-center shadow-none">
                    <Phone className="w-6 h-6 text-[#38BDF8] animate-pulse" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-[#F8FAFC]">Ready to initiate live WebRTC call</p>
                    <p className="text-xs text-[#64748B] max-w-sm mx-auto mt-0.5">
                      Click below to speak into your microphone. A.L.F.I.E will answer with {activeDemo.name} protocols.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4 w-full">
                  {/* Status Indicator Bar */}
                  <div className="flex items-center justify-center gap-2 p-2.5 rounded-xl bg-[#091728] border border-white/[0.06] text-xs text-[#E2E8F0] font-semibold shadow-none">
                    {simulatedState === 'speaking' && (
                      <>
                        <Volume2 className="w-4 h-4 text-[#38BDF8] animate-bounce" />
                        <span>A.L.F.I.E Speaking (24kHz Opus Full-Duplex)...</span>
                      </>
                    )}
                    {simulatedState === 'listening' && (
                      <>
                        <Mic className="w-4 h-4 text-emerald-400 animate-pulse" />
                        <span>Listening to your microphone... (Speak now)</span>
                      </>
                    )}
                    {simulatedState === 'connecting' && (
                      <>
                        <RefreshCw className="w-4 h-4 text-[#38BDF8] animate-spin" />
                        <span>Establishing WebRTC Media Stream...</span>
                      </>
                    )}
                  </div>

                  {/* Transcript Display */}
                  <div className="space-y-2 max-h-[160px] overflow-y-auto p-1">
                    {transcripts.map((t, idx) => (
                      <div key={idx} className="bg-[#091728] p-3 rounded-xl border border-white/[0.06] text-xs shadow-none space-y-1">
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 font-bold">
                          <span className="text-[#38BDF8] font-bold">{t.speaker}</span>
                          <span>{t.time}</span>
                        </div>
                        <p className="text-[#E2E8F0] leading-relaxed italic">
                          "{t.text}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Action Footer */}
            <div className="pt-5 border-t border-white/[0.06] flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-1.5 text-xs text-[#64748B] font-medium">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                <span>Encrypted WebRTC Audio Session</span>
              </div>

              <div className="flex items-center gap-2.5">
                {isCalling ? (
                  <>
                    <button
                      onClick={() => setIsMuted(!isMuted)}
                      className={`p-2.5 rounded-xl border transition-colors cursor-pointer text-xs ${
                        isMuted 
                          ? 'bg-red-500/10 border-red-300 text-red-400' 
                          : 'bg-[#091728] border-white/[0.06] text-[#CBD5E1] hover:bg-white/[0.05]'
                      }`}
                      title={isMuted ? "Unmute" : "Mute"}
                    >
                      {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>

                    <button
                      onClick={handleEndCall}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-red-600 hover:bg-red-700 text-white cursor-pointer transition-colors shadow-[0_2px_8px_rgba(0,0,0,0.3)]"
                    >
                      <PhoneOff className="w-3.5 h-3.5" />
                      <span>End Call</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleStartCall}
                    className="btn-primary text-xs py-2.5 px-6 rounded-xl"
                  >
                    <Phone className="w-3.5 h-3.5 text-blue-300" />
                    <span>Start 90-Second Demo Call</span>
                    <ArrowRight className="w-3.5 h-3.5 opacity-70" />
                  </button>
                )}
              </div>
            </div>

          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
