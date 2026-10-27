import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, PhoneMissed, PhoneCall, TrendingDown, TrendingUp, Sparkles } from 'lucide-react';
import WaveformEqualizer from './WaveformEqualizer';

export default function BeforeAfterAudioPlayer({ 
  className = '',
  customTracks = null,
  title = 'Hear the difference in call experience',
  subtitle = 'Audio Demonstration',
  badge = null
}) {
  const [activeTrack, setActiveTrack] = useState('alfie'); // 'legacy' | 'alfie'
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackProgress, setPlaybackProgress] = useState(0);

  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setPlaybackProgress(prev => {
          if (prev >= 100) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 5;
        });
      }, 300);
    } else {
      if (interval) clearInterval(interval);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying]);

  const toggleTrack = (track) => {
    setActiveTrack(track);
    setIsPlaying(false);
    setPlaybackProgress(0);
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setPlaybackProgress(0);
  };

  const defaultTrackInfo = {
    legacy: {
      title: 'Standard Voicemail Drop',
      subtitle: '4 Rings • Automated Recording • High Drop-Off',
      transcript: '"You have reached Modern Studio. No one is available to take your call. Please leave a message after the tone..." [Caller hangs up]',
      icon: PhoneMissed,
      color: 'border-slate-200/80 bg-slate-100/60 text-slate-700',
      tagColor: 'bg-slate-100 text-slate-600 border-slate-200/60',
      impact: 'Lost appointment to competitor down the street',
      latency: 'Delayed / No Response',
      impactIcon: TrendingDown
    },
    alfie: {
      title: 'A.L.F.I.E. Receptionist',
      subtitle: 'First Ring Pickup • Natural Human Voice • Calendar Sync',
      transcript: '"Good afternoon! Yes, Marcus has an open chair at 4:30 PM for a skin fade and beard trim. I have booked your slot in Square and texted your confirmation!"',
      icon: PhoneCall,
      color: 'border-[#008BC5] bg-[#008BC5] text-white',
      tagColor: 'bg-emerald-50 text-emerald-800 border-emerald-200/60',
      impact: '100% Captured Booking & SMS Confirmation Sent',
      latency: 'Sub-second response',
      impactIcon: TrendingUp
    }
  };

  const trackInfo = customTracks ? {
    legacy: { ...defaultTrackInfo.legacy, ...customTracks.legacy },
    alfie: { ...defaultTrackInfo.alfie, ...customTracks.alfie }
  } : defaultTrackInfo;

  const current = trackInfo[activeTrack];

  return (
    <div className={`rounded-3xl bg-white border border-slate-200/70 p-6 sm:p-8 shadow-xs ${className}`}>
      {/* Top Controls: Track Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <span className="text-xs font-medium text-slate-400 block mb-1">
            {subtitle}
          </span>
          <h3 className="text-lg sm:text-xl font-semibold text-slate-900">
            {title}
          </h3>
        </div>

        {/* Minimal Toggle Pill */}
        <div className="inline-flex p-1 rounded-xl bg-slate-100/90 text-xs font-medium">
          <button
            type="button"
            onClick={() => toggleTrack('legacy')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all cursor-pointer ${
              activeTrack === 'legacy' ? 'bg-white text-slate-900 shadow-2xs border border-slate-200/80' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <PhoneMissed className="w-3.5 h-3.5" />
            <span>Legacy Voicemail</span>
          </button>
          <button
            type="button"
            onClick={() => toggleTrack('alfie')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all cursor-pointer ${
              activeTrack === 'alfie' ? 'bg-[#008BC5] text-white shadow-2xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>With A.L.F.I.E</span>
          </button>
        </div>
      </div>

      {/* Main Player Display */}
      <div className="my-6 p-5 sm:p-6 rounded-2xl bg-slate-50/70 border border-slate-200/60 relative">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center border transition-colors ${current.color}`}>
              <current.icon className="w-4 h-4" />
            </div>
            <div>
              <h4 className="font-semibold text-sm sm:text-base text-slate-900">
                {current.title}
              </h4>
              <p className="text-xs text-slate-500">
                {current.subtitle}
              </p>
            </div>
          </div>

          <span className={`px-2.5 py-1 rounded-full text-xs font-medium border self-start sm:self-auto ${current.tagColor}`}>
            {current.latency}
          </span>
        </div>

        {/* 3D Robot Video Preview matching active track */}
        <div className="relative w-full h-48 sm:h-56 rounded-xl bg-white overflow-hidden mb-5 border border-slate-200/70 flex items-center justify-center">
          <video
            key={activeTrack}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-contain pointer-events-none"
          >
            <source
              src={activeTrack === 'legacy' ? '/assets/brand_mascot/2.webm' : '/assets/brand_mascot/3.webm'}
              type="video/webm"
            />
          </video>
        </div>

        {/* Audio Waveform Equalizer */}
        <div className="py-3.5 px-4 rounded-xl bg-white border border-slate-200/70 flex items-center justify-between gap-4 shadow-2xs">
          <button
            type="button"
            onClick={handlePlayPause}
            className="w-9 h-9 rounded-lg bg-[#008BC5] text-white flex items-center justify-center transition-transform hover:scale-105 active:scale-95 cursor-pointer shadow-xs"
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
          </button>

          <div className="flex-1">
            <WaveformEqualizer
              isActive={isPlaying}
              barCount={28}
              className="h-6"
              activeColor="bg-[#008BC5]"
              idleColor="bg-slate-200"
            />
          </div>

          <button
            type="button"
            onClick={handleReset}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
            title="Replay"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Transcript Dialogue Box */}
        <div className="mt-4 p-4 rounded-xl bg-white border border-slate-200/70 text-xs">
          <p className="text-xs text-slate-700 leading-relaxed font-sans">
            {current.transcript}
          </p>
        </div>
      </div>

      {/* Outcome Footer */}
      <div className="flex items-center justify-between pt-1 text-xs">
        <span className="text-slate-500 font-medium">Outcome:</span>
        <span className={`font-semibold ${activeTrack === 'alfie' ? 'text-slate-900' : 'text-slate-600'}`}>
          {current.impact}
        </span>
      </div>
    </div>
  );
}
