import React from 'react';
import { Shield, Zap, Lock, PhoneCall, Cpu, ArrowUpRight, Radio } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-slate-50 border-t border-slate-200/80 pt-16 pb-12 text-slate-600 relative overflow-hidden">
      
      {/* Background ambient lighting */}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-slate-200">
          
          {/* Brand Col */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <img 
                  src="/logo.webp" 
                  alt="A.L.F.I.E Logo" 
                  className="h-8 w-auto object-contain"
                />
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              <span className="font-extrabold text-xl text-slate-900 tracking-tight font-heading">A.L.F.I.E</span>
            </div>
            <p className="text-xs text-slate-600 max-w-sm leading-relaxed">
              Autonomous Voice AI receptionist and telephony cloud infrastructure engineered for local shops, medical clinics, law firms, and multi-location enterprises.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-3 py-1 w-fit font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>All Telephony Systems Operational (99.99% SLA)</span>
            </div>
          </div>

          {/* Solutions */}
          <div>
            <h4 className="font-bold text-xs text-slate-900 uppercase tracking-wider mb-3 font-mono">
              Industry Verticals
            </h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li>
                <Link to="/law-firms" className="hover:text-blue-600 transition-colors">
                  Personal Injury Law
                </Link>
              </li>
              <li>
                <Link to="/clinics" className="hover:text-blue-600 transition-colors">
                  Medical & Dental Clinics
                </Link>
              </li>
              <li>
                <Link to="/car-rental" className="hover:text-blue-600 transition-colors">
                  Luxury Transport & Fleets
                </Link>
              </li>
              <li>
                <Link to="/real-estate" className="hover:text-blue-600 transition-colors">
                  Real Estate Brokerages
                </Link>
              </li>
              <li>
                <Link to="/hospitality" className="hover:text-blue-600 transition-colors">
                  Fine Hospitality & Dining
                </Link>
              </li>
            </ul>
          </div>

          {/* Telephony Core */}
          <div>
            <h4 className="font-bold text-xs text-slate-900 uppercase tracking-wider mb-3 font-mono">
              Infrastructure
            </h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-slate-600" />
                <span>LiveKit WebRTC 48kHz</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-slate-600" />
                <span>Deepgram Nova-2 STT</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-slate-600" />
                <span>Redis Stack Memory</span>
              </li>
              <li className="flex items-center gap-1.5">
                <PhoneCall className="w-3.5 h-3.5 text-slate-600" />
                <span>BYOK Carrier SIP Trunking</span>
              </li>
            </ul>
          </div>

          {/* Portals & Security */}
          <div>
            <h4 className="font-bold text-xs text-slate-900 uppercase tracking-wider mb-3 font-mono">
              Portals & Security
            </h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li>
                <a 
                  href="http://localhost:5174" 
                  target="_blank" 
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-blue-600 transition-colors font-semibold text-slate-700"
                >
                  <span>Client Admin Portal</span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
                </a>
              </li>
              <li>
                <a 
                  href="http://localhost:5173" 
                  target="_blank" 
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-blue-600 transition-colors font-semibold text-slate-700"
                >
                  <span>Super Admin Portal</span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
                </a>
              </li>
              <li className="pt-2 flex items-center gap-1.5 text-xs text-emerald-600 font-mono">
                <Shield className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>SOC-2 & HIPAA Compliant</span>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400 font-mono">
          <p>© {new Date().getFullYear()} A.L.F.I.E Voice AI Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="cursor-pointer hover:text-slate-900 transition-colors">Privacy Policy</span>
            <span className="cursor-pointer hover:text-slate-900 transition-colors">Terms of Service</span>
            <span className="cursor-pointer hover:text-slate-900 transition-colors">Security Architecture</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
