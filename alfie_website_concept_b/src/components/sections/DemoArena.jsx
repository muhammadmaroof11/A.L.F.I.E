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
    <section id="demo-arena" className="py-20 bg-white border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
            <Radio className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
            <span>Interactive WebRTC Telephony Sandbox</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Test A.L.F.I.E Live In Your Browser
          </h2>
          <p className="text-sm sm:text-base text-slate-600">
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
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
                } ${isCalling ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-300' : 'text-slate-500'}`} />
                <span>{n.name}</span>
              </button>
            );
          })}
        </div>

        {/* Live Call Console Card */}
        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-3xl mx-auto bg-[#FAFAFC] rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs">
            
            {/* Top Console Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-slate-200">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-sm">
                  A
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                    {activeDemo.name} Voice Node
                  </h3>
                  <p className="text-[11px] text-slate-500 font-mono">
                    Deepgram Nova-2 + LiveKit Cloud SIP Bridge
                  </p>
                </div>
              </div>

              {/* Timer Pill */}
              <div className="flex items-center gap-2">
                {isCalling && (
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-50 text-red-700 border border-red-200 text-xs font-mono font-bold">
                    <span className="w-2 h-2 rounded-full bg-red-600 animate-ping" />
                    <span>{formatTime(callDuration)} / 1:30</span>
                  </div>
                )}
                <div className="text-[11px] font-mono font-semibold text-slate-500 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
                  TTFT: 390ms
                </div>
              </div>
            </div>

            {/* Middle Stage Area */}
            <div className="py-8 min-h-[200px] flex flex-col justify-center items-center">
              {!isCalling ? (
                <div className="text-center space-y-3">
                  <div className="w-14 h-14 rounded-2xl bg-white border border-slate-200 text-slate-800 mx-auto flex items-center justify-center shadow-2xs">
                    <Phone className="w-6 h-6 text-blue-600 animate-pulse" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900">Ready to initiate live WebRTC call</p>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto mt-0.5">
                      Click below to speak into your microphone. A.L.F.I.E will answer with {activeDemo.name} protocols.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4 w-full">
                  {/* Status Indicator Bar */}
                  <div className="flex items-center justify-center gap-2 p-2.5 rounded-xl bg-white border border-slate-200 text-xs text-slate-800 font-semibold shadow-2xs">
                    {simulatedState === 'speaking' && (
                      <>
                        <Volume2 className="w-4 h-4 text-blue-600 animate-bounce" />
                        <span>A.L.F.I.E Speaking (24kHz Opus Full-Duplex)...</span>
                      </>
                    )}
                    {simulatedState === 'listening' && (
                      <>
                        <Mic className="w-4 h-4 text-emerald-600 animate-pulse" />
                        <span>Listening to your microphone... (Speak now)</span>
                      </>
                    )}
                    {simulatedState === 'connecting' && (
                      <>
                        <RefreshCw className="w-4 h-4 text-blue-600 animate-spin" />
                        <span>Establishing WebRTC Media Stream...</span>
                      </>
                    )}
                  </div>

                  {/* Transcript Display */}
                  <div className="space-y-2 max-h-[160px] overflow-y-auto p-1">
                    {transcripts.map((t, idx) => (
                      <div key={idx} className="bg-white p-3 rounded-xl border border-slate-200 text-xs shadow-2xs space-y-1">
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 font-bold">
                          <span className="text-blue-600 font-bold">{t.speaker}</span>
                          <span>{t.time}</span>
                        </div>
                        <p className="text-slate-800 leading-relaxed italic">
                          "{t.text}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Action Footer */}
            <div className="pt-5 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                <Shield className="w-3.5 h-3.5 text-emerald-600" />
                <span>Encrypted WebRTC Audio Session</span>
              </div>

              <div className="flex items-center gap-2.5">
                {isCalling ? (
                  <>
                    <button
                      onClick={() => setIsMuted(!isMuted)}
                      className={`p-2.5 rounded-xl border transition-colors cursor-pointer text-xs ${
                        isMuted 
                          ? 'bg-red-50 border-red-300 text-red-700' 
                          : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                      title={isMuted ? "Unmute" : "Mute"}
                    >
                      {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>

                    <button
                      onClick={handleEndCall}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-red-600 hover:bg-red-700 text-white cursor-pointer transition-colors shadow-xs"
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
