import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Terminal, Copy, Check } from 'lucide-react';

const mockLogs = [
  {
    timestamp: '00:00.142',
    event: 'VAD_TRIGGER',
    level: 'INFO',
    detail: 'Silero voice activity detected (confidence: 0.982, SNR: 24dB)'
  },
  {
    timestamp: '00:00.285',
    event: 'INTENT_CLASSIFIED',
    level: 'INFO',
    detail: 'Intent: "book_appointment", slot: { service: "skin_fade", stylist: "Marcus", time: "16:30" }'
  },
  {
    timestamp: '00:00.340',
    event: 'TOOL_INVOKE',
    level: 'EXEC',
    detail: 'Calling check_calendar_availability(provider="square", time="2026-09-16T16:30:00Z")'
  },
  {
    timestamp: '00:00.395',
    event: 'TOOL_RESULT',
    level: 'SUCCESS',
    detail: 'Square API 200 OK: Chair available, reserved slot ID: sq_res_884920'
  },
  {
    timestamp: '00:00.460',
    event: 'TTS_STREAM',
    level: 'INFO',
    detail: 'Cartesia Sonic 3.0 streaming chunk 0 (TTFB: 78ms, Opus 48kHz)'
  },
  {
    timestamp: '00:00.520',
    event: 'DISPATCH_SMS',
    level: 'EXEC',
    detail: 'Calling send_sms_confirmation(to="+1-555-0199", body="Marcus locked for 4:30 PM...")'
  }
];

export default function LiveExecutionTerminal({ activeNiche = 'clinic', className = '' }) {
  const [logs, setLogs] = useState(() => mockLogs.slice(0, 3));
  const [isLive, setIsLive] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isLive) return;

    let currentIndex = 3;
    const interval = setInterval(() => {
      const nextLog = mockLogs[currentIndex % mockLogs.length];
      if (nextLog) {
        setLogs(prev => {
          const safePrev = Array.isArray(prev) ? prev.filter(Boolean) : [];
          if (safePrev.length >= 6) {
            return [...safePrev.slice(1), nextLog];
          }
          return [...safePrev, nextLog];
        });
      }
      currentIndex = (currentIndex + 1) % mockLogs.length;
    }, 2200);

    return () => clearInterval(interval);
  }, [isLive, activeNiche]);

  const handleCopy = () => {
    const text = (logs || [])
      .filter(Boolean)
      .map(l => `[${l?.timestamp || ''}] [${l?.event || ''}] ${l?.detail || ''}`)
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`rounded-2xl bg-slate-50/90 border border-slate-200/90 shadow-sm overflow-hidden font-mono text-xs text-slate-700 flex flex-col ${className}`}>
      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-slate-200/80 select-none">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-300 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-slate-300 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-slate-300 inline-block" />
          </div>
          <div className="flex items-center gap-1.5 ml-2 text-slate-700 text-[11px] font-bold">
            <Terminal className="w-3.5 h-3.5 text-blue-600" />
            <span>ALFIE_TELEPHONY_LOGS</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsLive(!isLive)}
            className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              isLive ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
            <span>{isLive ? 'STREAMING' : 'PAUSED'}</span>
          </button>

          <button
            type="button"
            onClick={handleCopy}
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            title="Copy logs"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div className="p-4 space-y-2 h-64 overflow-y-auto bg-white/60 text-[11px] leading-relaxed">
        <AnimatePresence>
          {(logs || []).filter(Boolean).map((log, index) => {
            if (!log || !log.timestamp) return null;
            return (
              <motion.div
                key={`${log.event}-${index}`}
                initial={{ opacity: 0, x: -4 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
                className="flex items-start gap-2"
              >
                <span className="text-slate-400 shrink-0 select-none">[{log.timestamp}]</span>
                <span
                  className={`font-bold shrink-0 px-1.5 py-0.5 rounded text-[10px] ${
                    log.level === 'SUCCESS'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : log.level === 'EXEC'
                      ? 'bg-amber-50 text-amber-800 border border-amber-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}
                >
                  {log.event}
                </span>
                <span className="text-slate-700 break-all">{log.detail}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>
        <div className="flex items-center gap-1.5 text-blue-600 pt-1">
          <span className="animate-pulse font-bold">›</span>
          <span className="text-slate-400 italic">Listening for inbound telephony SIP payload...</span>
        </div>
      </div>

      {/* Terminal Footer */}
      <div className="px-4 py-2.5 bg-white border-t border-slate-200/80 flex items-center justify-between text-[10px] text-slate-500">
        <div className="flex items-center gap-2">
          <span className="text-emerald-600 font-semibold">● LiveKit SIP Gateway</span>
          <span className="text-slate-300">|</span>
          <span>Groq Llama 3.3 70B</span>
        </div>
        <span className="text-slate-400 font-medium">Latency: ~342ms</span>
      </div>
    </div>
  );
}
