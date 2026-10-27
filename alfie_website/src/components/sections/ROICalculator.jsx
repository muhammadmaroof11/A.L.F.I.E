import React, { useState } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  PhoneCall, 
  ArrowRight, 
  Calculator,
  Scissors,
  Stethoscope, 
  Scale, 
  Building2,
  Sparkles
} from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';
import SpotlightCard from '../shared/SpotlightCard';
import { Button } from '../ui/button';
import { NumberTicker } from '../ui/number-ticker';
import { BorderBeam } from '../ui/border-beam';

const presets = [
  { id: 'clinic', name: 'Dental / Clinic', icon: Stethoscope, calls: 35, deal: 250, missRate: 25 },
  { id: 'legal', name: 'Law Firm', icon: Scale, calls: 25, deal: 4000, missRate: 20 },
  { id: 'enterprise', name: 'Enterprise Hub', icon: Building2, calls: 120, deal: 800, missRate: 15 },
];

export default function ROICalculator() {
  const [activePreset, setActivePreset] = useState('clinic');
  const [callsPerDay, setCallsPerDay] = useState(35);
  const [dealValue, setDealValue] = useState(250);
  const [currentMissRate, setCurrentMissRate] = useState(25);

  const applyPreset = (p) => {
    setActivePreset(p.id);
    setCallsPerDay(p.calls);
    setDealValue(p.deal);
    setCurrentMissRate(p.missRate);
  };

  // Financial calculations
  const monthlyInboundCalls = callsPerDay * 30;
  const monthlyMissedCalls = Math.round(monthlyInboundCalls * (currentMissRate / 100));
  const recoveredBookings = Math.max(1, Math.round(monthlyMissedCalls * 0.28)); // 28% recovery conversion
  const monthlyRecoveredValue = recoveredBookings * dealValue;
  const yearlyRecoveredValue = monthlyRecoveredValue * 12;
  const alfieMonthlyCost = 99; // Starter local baseline
  const netMonthlyGain = Math.max(0, monthlyRecoveredValue - alfieMonthlyCost);
  const netRoiMultiplier = Number((monthlyRecoveredValue / (alfieMonthlyCost || 1)).toFixed(1));

  return (
    <section id="roi-calculator" className="py-24 bg-slate-50/50 text-slate-900 relative overflow-hidden border-b border-slate-200">
      
      {/* Ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-6xl h-[600px] bg-slate-100/50 rounded-full blur-3xl pointer-events-none opacity-40" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            ROI Calculator
          </p>
          
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight font-heading">
            Calculate your recovered revenue
          </h2>
          
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            See how much revenue your business captures each month by answering every call on the first ring.
          </p>

          {/* 1-Click Industry Presets */}
          <div className="flex flex-wrap justify-center gap-2 pt-4">
            {presets.map((p) => {
              const Icon = p.icon;
              const isSelected = activePreset === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900 text-white'
                      : 'bg-white/[0.04] text-slate-600 hover:bg-white/[0.08] hover:text-slate-900 border border-slate-200'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-slate-700'}`} />
                  <span>{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-5xl mx-auto">
            <SpotlightCard className="p-8 sm:p-10 border-slate-200 shadow-2xl relative">
              <BorderBeam size={160} duration={12} colorFrom="#94a3b8" colorTo="#cbd5e1" />

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
                
                {/* Sliders Column Left */}
                <div className="lg:col-span-7 space-y-8">
                  
                  {/* Slider 1: Average Calls / Day */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-xs font-bold text-slate-900">
                      <label className="flex items-center gap-2 font-heading">
                        <PhoneCall className="w-4 h-4 text-slate-700" />
                        <span>Average Inbound Calls / Day:</span>
                      </label>
                      <span className="text-slate-700 font-extrabold text-sm font-mono bg-cyan-950/40 px-2.5 py-0.5 rounded-lg border border-cyan-500/30">
                        {callsPerDay} calls/day
                      </span>
                    </div>
                    <input
                      type="range"
                      min="5"
                      max="150"
                      step="5"
                      value={callsPerDay}
                      onChange={(e) => {
                        setActivePreset('');
                        setCallsPerDay(Number(e.target.value));
                      }}
                      className="tactile-slider w-full"
                    />
                    <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                      <span>5 calls (Solo Shop)</span>
                      <span>150 calls (Enterprise Hub)</span>
                    </div>
                  </div>

                  {/* Slider 2: Average Ticket / Appointment Value */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-xs font-bold text-slate-900">
                      <label className="flex items-center gap-2 font-heading">
                        <DollarSign className="w-4 h-4 text-emerald-400" />
                        <span>Average Service Ticket Value:</span>
                      </label>
                      <span className="text-emerald-400 font-extrabold text-sm font-mono bg-emerald-500/10 px-2.5 py-0.5 rounded-lg border border-emerald-500/30">
                        ${dealValue.toLocaleString()}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="20"
                      max="5000"
                      step="5"
                      value={dealValue}
                      onChange={(e) => {
                        setActivePreset('');
                        setDealValue(Number(e.target.value));
                      }}
                      className="tactile-slider w-full"
                    />
                    <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                      <span>$20 (Cut / Blowout)</span>
                      <span>$5,000 (Legal Retainer)</span>
                    </div>
                  </div>

                  {/* Slider 3: Estimated Missed Call Rate */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-xs font-bold text-slate-900">
                      <label className="flex items-center gap-2 font-heading">
                        <TrendingUp className="w-4 h-4 text-amber-400" />
                        <span>Estimated Missed Call Rate:</span>
                      </label>
                      <span className="text-amber-400 font-extrabold text-sm font-mono bg-amber-500/10 px-2.5 py-0.5 rounded-lg border border-amber-500/30">
                        {currentMissRate}% missed
                      </span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="50"
                      step="5"
                      value={currentMissRate}
                      onChange={(e) => {
                        setActivePreset('');
                        setCurrentMissRate(Number(e.target.value));
                      }}
                      className="tactile-slider w-full"
                    />
                    <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                      <span>10% (Low Leakage)</span>
                      <span>50% (High Leakage)</span>
                    </div>
                  </div>

                  {/* Quick Insight Bar */}
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs flex items-center justify-between text-slate-600 font-mono">
                    <span>Monthly Calls Lost to Voicemail:</span>
                    <span className="font-bold text-rose-400">{monthlyMissedCalls} calls/mo</span>
                  </div>

                </div>

                {/* Executive Outcome Card Right */}
                <div className="lg:col-span-5">
                  <div className="p-8 sm:p-9 rounded-3xl bg-slate-50 border border-slate-200 shadow-sm text-slate-900 flex flex-col justify-between space-y-6 relative overflow-hidden">
                    
                    {/* Background glow */}
                    <div className="absolute top-0 right-0 w-48 h-48 bg-slate-200/50 rounded-full blur-2xl pointer-events-none" />

                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-700">
                          Projected Recovered Revenue
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono font-bold text-[11px] border border-emerald-500/30">
                          {netRoiMultiplier}x ROI
                        </span>
                      </div>
                      
                      <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight font-mono ">
                          $<NumberTicker value={monthlyRecoveredValue} />
                        </span>
                        <span className="text-xs text-slate-500 font-mono font-medium">/ month</span>
                      </div>
                      
                      <p className="text-xs text-slate-600 mt-3 leading-relaxed">
                        Recovers approximately <span className="text-blue-600 font-bold">{recoveredBookings} appointments/month</span> that would have otherwise hung up and booked elsewhere.
                      </p>
                    </div>

                    {/* Annualized Projection */}
                    <div className="pt-4 border-t border-slate-200 space-y-2 relative z-10 text-xs font-mono">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-500">Annual Run-Rate Saved:</span>
                        <span className="font-bold text-emerald-400 text-sm">
                          ${yearlyRecoveredValue.toLocaleString()}/yr
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[11px] text-slate-500">
                        <span>Net Monthly Gain:</span>
                        <span className="font-semibold text-slate-600">
                          +${netMonthlyGain.toLocaleString()}/mo
                        </span>
                      </div>
                    </div>

                    {/* CTA */}
                    <Button
                      variant="primary"
                      className="w-full gap-2 text-xs font-bold py-5 shadow-sm cursor-pointer relative z-10"
                      onClick={() => {
                        const el = document.getElementById('pricing');
                        if (el) el.scrollIntoView({ behavior: 'smooth' });
                      }}
                    >
                      <span>Lock In Your Recovered Revenue</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>

              </div>
            </SpotlightCard>
          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
