import React, { useRef } from 'react';
import { motion } from 'motion/react';
import { Phone, Radio, Cpu, Calendar, MessageSquare } from 'lucide-react';
import { AnimatedBeam } from './animated-beam';

export default function TelephonySignalFlow({ className = '' }) {
  const containerRef = useRef(null);
  const callerRef = useRef(null);
  const carrierRef = useRef(null);
  const coreRef = useRef(null);
  const calendarRef = useRef(null);
  const smsRef = useRef(null);

  const nodes = [
    {
      id: 'caller',
      ref: callerRef,
      icon: Phone,
      label: 'Inbound Call',
      sub: 'Customer dials line',
      color: 'border-slate-200/80 bg-white text-slate-900 shadow-2xs',
      iconBg: 'bg-slate-100 text-slate-700'
    },
    {
      id: 'carrier',
      ref: carrierRef,
      icon: Radio,
      label: 'Carrier Network',
      sub: 'Instant SIP routing',
      color: 'border-slate-200/80 bg-white text-slate-900 shadow-2xs',
      iconBg: 'bg-slate-100 text-slate-700'
    },
    {
      id: 'core',
      ref: coreRef,
      icon: Cpu,
      label: 'A.L.F.I.E. Receptionist',
      sub: 'Sub-second intelligence',
      color: 'border-[#1D293D] bg-[#1D293D] text-white shadow-xs',
      iconBg: 'bg-white/10 text-white'
    },
    {
      id: 'calendar',
      ref: calendarRef,
      icon: Calendar,
      label: 'Calendar Sync',
      sub: 'Direct slot reservation',
      color: 'border-slate-200/80 bg-white text-slate-900 shadow-2xs',
      iconBg: 'bg-slate-100 text-slate-700'
    },
    {
      id: 'sms',
      ref: smsRef,
      icon: MessageSquare,
      label: 'SMS Confirmation',
      sub: 'Instant text dispatch',
      color: 'border-slate-200/80 bg-white text-slate-900 shadow-2xs',
      iconBg: 'bg-slate-100 text-slate-700'
    }
  ];

  return (
    <div
      ref={containerRef}
      className={`relative w-full overflow-hidden rounded-3xl bg-white p-6 sm:p-10 border border-slate-200/70 shadow-xs ${className}`}
    >
      {/* Subtle Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a04_1px,transparent_1px),linear-gradient(to_bottom,#0f172a04_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <span className="text-xs font-medium text-slate-400 block mb-1">
            System Architecture
          </span>
          <h3 className="text-lg sm:text-xl font-semibold text-slate-900">
            How A.L.F.I.E. handles every call
          </h3>
        </div>
        <div className="text-xs font-medium text-slate-500 bg-slate-50 border border-slate-200/70 px-3.5 py-1.5 rounded-full">
          Real-Time Intake & Sync
        </div>
      </div>

      {/* Node Pathway */}
      <div className="relative z-10 py-10 flex flex-col lg:flex-row items-center justify-between gap-6 lg:gap-3">
        {nodes.map((node, index) => {
          const IconComp = node.icon;
          return (
            <motion.div
              key={node.id}
              ref={node.ref}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.4 }}
              className={`relative z-20 flex flex-col items-center text-center p-4 sm:p-5 rounded-2xl border transition-all duration-200 max-w-[190px] w-full ${node.color}`}
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 transition-colors ${node.iconBg}`}>
                <IconComp className="w-4 h-4" />
              </div>
              <h4 className={`text-xs sm:text-sm font-semibold leading-tight ${node.id === 'core' ? 'text-white' : 'text-slate-900'}`}>
                {node.label}
              </h4>
              <p className={`text-xs mt-1 leading-tight ${node.id === 'core' ? 'text-slate-300' : 'text-slate-500'}`}>
                {node.sub}
              </p>
            </motion.div>
          );
        })}
      </div>

      {/* Animated Beams connecting nodes in sequence */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={callerRef}
        toRef={carrierRef}
        curvature={-10}
        pathColor="rgba(226, 232, 240, 0.8)"
        gradientStartColor="#94A3B8"
        gradientStopColor="#0F172A"
        duration={3.5}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={carrierRef}
        toRef={coreRef}
        curvature={10}
        pathColor="rgba(226, 232, 240, 0.8)"
        gradientStartColor="#0F172A"
        gradientStopColor="#0F172A"
        duration={3.2}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={coreRef}
        toRef={calendarRef}
        curvature={-10}
        pathColor="rgba(226, 232, 240, 0.8)"
        gradientStartColor="#0F172A"
        gradientStopColor="#0F172A"
        duration={3.4}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={calendarRef}
        toRef={smsRef}
        curvature={10}
        pathColor="rgba(226, 232, 240, 0.8)"
        gradientStartColor="#0F172A"
        gradientStopColor="#94A3B8"
        duration={3.6}
      />

      {/* Bottom Summary Strip */}
      <div className="relative z-10 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
        <span>Zero server buffering • Instant two-way calendar sync</span>
        <span className="font-medium text-slate-900">Sub-second response SLA</span>
      </div>
    </div>
  );
}
