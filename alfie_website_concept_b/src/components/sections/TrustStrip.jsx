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
    <section className="py-8 bg-white border-b border-slate-200/80 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 items-center">
          {badges.map((b, idx) => {
            const BadgeIcon = b.icon;
            return (
              <div 
                key={idx} 
                className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-50/70 border border-slate-200/60 hover:bg-white hover:border-slate-300 transition-all group"
              >
                <div className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-700 group-hover:text-blue-600 transition-colors shadow-2xs shrink-0">
                  <BadgeIcon className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-slate-800 truncate">{b.label}</p>
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
