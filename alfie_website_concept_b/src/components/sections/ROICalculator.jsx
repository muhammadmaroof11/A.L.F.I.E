import React, { useState } from 'react';
import { DollarSign, TrendingUp, Users, PhoneCall, ShieldCheck, ArrowRight, Calculator, CheckCircle2 } from 'lucide-react';
import ScrollReveal from '../shared/ScrollReveal';

export default function ROICalculator() {
  const [callsPerDay, setCallsPerDay] = useState(30);
  const [dealValue, setDealValue] = useState(3500);
  const [currentMissRate, setCurrentMissRate] = useState(25);

  // Financial calculations
  const monthlyInboundCalls = callsPerDay * 30;
  const monthlyMissedCalls = Math.round(monthlyInboundCalls * (currentMissRate / 100));
  const recoveredRetainers = Math.max(1, Math.round(monthlyMissedCalls * 0.20)); // conservative 20% conversion
  const monthlyRecoveredValue = recoveredRetainers * dealValue;
  const yearlyRecoveredValue = monthlyRecoveredValue * 12;
  const alfieMonthlyCost = 499;
  const netMonthlyGain = monthlyRecoveredValue - alfieMonthlyCost;
  const netRoiMultiplier = (netMonthlyGain / alfieMonthlyCost).toFixed(1);

  return (
    <section id="roi-calculator" className="py-20 bg-white border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
            <Calculator className="w-3.5 h-3.5 text-blue-600" />
            <span>Institutional Revenue Recovery Model</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Calculate Your Recoverable Inbound Revenue
          </h2>
          <p className="text-sm sm:text-base text-slate-600">
            See how much revenue your practice or firm is actively losing to after-hours voicemail, and see your exact projected return on investment.
          </p>
        </div>

        <ScrollReveal y={20} duration={0.6}>
          <div className="max-w-5xl mx-auto bg-[#FAFAFC] rounded-3xl border border-slate-200 p-6 sm:p-10 shadow-xs">
            
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
              
              {/* Sliders Left */}
              <div className="lg:col-span-7 space-y-6">
                
                {/* Slider 1 */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-800">
                    <label>Average Inbound Calls / Day:</label>
                    <span className="text-blue-600 font-extrabold text-sm bg-white px-2.5 py-0.5 rounded-lg border border-slate-200 shadow-2xs font-mono">
                      {callsPerDay} calls/day
                    </span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="150"
                    step="5"
                    value={callsPerDay}
                    onChange={(e) => setCallsPerDay(Number(e.target.value))}
                    className="w-full accent-slate-900 h-2 bg-slate-200 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>5 calls (Solo Practice)</span>
                    <span>150 calls (Multi-Partner Firm)</span>
                  </div>
                </div>

                {/* Slider 2 */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-800">
                    <label>Average Retainer / Transaction Value:</label>
                    <span className="text-amber-800 font-extrabold text-sm bg-amber-50 px-2.5 py-0.5 rounded-lg border border-amber-200 font-mono">
                      ${dealValue.toLocaleString()}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="200"
                    max="15000"
                    step="100"
                    value={dealValue}
                    onChange={(e) => setDealValue(Number(e.target.value))}
                    className="w-full accent-amber-600 h-2 bg-slate-200 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>$200 (Clinic Visit)</span>
                    <span>$15,000+ (Personal Injury Retainer)</span>
                  </div>
                </div>

                {/* Slider 3 */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-800">
                    <label>Current Unanswered / After-Hours Rate:</label>
                    <span className="text-red-700 font-extrabold text-sm bg-red-50 px-2.5 py-0.5 rounded-lg border border-red-200 font-mono">
                      {currentMissRate}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="60"
                    step="2"
                    value={currentMissRate}
                    onChange={(e) => setCurrentMissRate(Number(e.target.value))}
                    className="w-full accent-red-600 h-2 bg-slate-200 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>10% (Low)</span>
                    <span>60% (High after-hours & weekend load)</span>
                  </div>
                </div>

                {/* Comparison Snapshot */}
                <div className="pt-2">
                  <div className="bg-white p-3.5 rounded-2xl border border-slate-200 text-xs space-y-2 shadow-2xs">
                    <p className="font-bold text-slate-800 flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-slate-500">
                      <span>Benchmark Comparison:</span>
                    </p>
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div className="bg-red-50/70 p-2 rounded-lg border border-red-200/60 text-red-900">
                        <p className="font-bold">Human Front Desk:</p>
                        <p className="text-[10px] text-red-700">~$4,800/mo + Benefits</p>
                        <p className="text-[10px] text-red-700 font-semibold mt-0.5">34% Calls Missed (Nights/Lunch)</p>
                      </div>
                      <div className="bg-emerald-50/70 p-2 rounded-lg border border-emerald-200/60 text-emerald-900">
                        <p className="font-bold">A.L.F.I.E Voice AI:</p>
                        <p className="text-[10px] text-emerald-700 font-bold">$499/mo Fixed</p>
                        <p className="text-[10px] text-emerald-700 font-semibold mt-0.5">0% Calls Missed (24/7/365)</p>
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* Terminal Summary Output Right */}
              <div className="lg:col-span-5 bg-slate-900 rounded-3xl p-7 text-white shadow-xl flex flex-col justify-between space-y-6">
                
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                    Projected Annual Revenue Add
                  </span>
                  <div className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-mono">
                    +${yearlyRecoveredValue.toLocaleString()}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Recovers ~{monthlyMissedCalls} missed calls/month
                  </p>
                </div>

                <div className="space-y-2 py-4 border-y border-slate-800 text-xs font-mono">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Monthly Recovered Deals:</span>
                    <span className="font-bold text-emerald-400">+{recoveredRetainers} retainers/mo</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Gross Monthly Recovery:</span>
                    <span className="font-bold text-white">+${monthlyRecoveredValue.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">A.L.F.I.E Software Cost:</span>
                    <span className="font-bold text-slate-300">-$499/mo</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-800/80 text-emerald-400 font-bold">
                    <span>Projected ROI:</span>
                    <span>{netRoiMultiplier}x Return</span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    const demo = document.getElementById('demo-arena');
                    if (demo) demo.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="w-full py-3 rounded-xl font-bold text-xs bg-white text-slate-900 hover:bg-slate-100 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-md"
                >
                  <span>Lock In This Revenue With A.L.F.I.E</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

              </div>

            </div>

          </div>
        </ScrollReveal>

      </div>
    </section>
  );
}
