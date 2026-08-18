import React from 'react';
import { ShieldCheck, Lock, Activity, Award, CheckCircle, Server } from 'lucide-react';

const badges = [
  { icon: ShieldCheck, label: 'SOC-2 Type II Certified', sub: 'Audited Telephony Vault' },
  { icon: Lock, label: 'HIPAA & BAA Compliant', sub: 'Zero-EHR Exposure' },
  { icon: Server, label: 'Tier-1 SIP Interconnect', sub: '99.99% Carrier SLA' },
  { icon: Award, label: 'Sub-400ms Loop Latency', sub: 'WebRTC Full-Duplex' },
  { icon: CheckCircle, label: 'Zero-Data-Retain Mode', sub: 'Ephemeral Speech Audio' },
  { icon: Activity, label: '500+ Concurrent Lines', sub: 'Auto-Scaling Pods' },
];

export default function TrustStrip() {
  return (
    <section className="py-8 bg-[#111726] border-b border-white/[0.05] overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 items-center">
          {badges.map((b, idx) => {
            const BadgeIcon = b.icon;
            return (
              <div 
                key={idx} 
                className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-white/[0.08] hover:border-[#38BDF8]/30 transition-all group cd-glow-border"
              >
                <div className="w-8 h-8 rounded-lg bg-white/[0.06] border border-white/[0.08] flex items-center justify-center text-slate-400 group-hover:text-[#38BDF8] transition-colors shrink-0">
                  <BadgeIcon className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-slate-200 truncate">{b.label}</p>
                  <p className="text-[10px] text-slate-500 font-medium truncate">{b.sub}</p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
