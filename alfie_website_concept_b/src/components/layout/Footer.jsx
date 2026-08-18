import React from 'react';
import { Shield, Zap, Lock, CheckCircle2, PhoneCall, Cpu, ArrowUpRight } from 'lucide-react';

export default function Footer() {
  const scrollTo = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-white border-t border-slate-200/90 pt-16 pb-12 text-fg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-slate-100">
          
          {/* Brand Col */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <img 
                src="/logo.png" 
                alt="A.L.F.I.E Logo" 
                className="h-8 w-auto object-contain rounded-lg"
              />
              <span className="font-extrabold text-2xl text-slate-900 tracking-tight">A.L.F.I.E</span>
            </div>
            <p className="text-sm text-fg-muted max-w-sm leading-relaxed">
              Autonomous, hyper-realistic Voice AI receptionist infrastructure engineered for high-ticket law firms, medical clinics, luxury fleet operators, and enterprise service verticals.
            </p>
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/60 rounded-full px-3 py-1.5 w-fit">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>All 5 Voice Pipelines Operational (99.99% SLA)</span>
            </div>
          </div>

          {/* Vertical Solutions */}
          <div>
            <h4 className="font-bold text-sm text-primary uppercase tracking-wider mb-4">Verticals</h4>
            <ul className="space-y-2.5 text-sm text-fg-muted">
              <li>
                <button onClick={() => scrollTo('niche-showcase')} className="hover:text-secondary transition-colors cursor-pointer text-left">
                  Personal Injury Law
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('niche-showcase')} className="hover:text-secondary transition-colors cursor-pointer text-left">
                  Medical & Dental Clinics
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('niche-showcase')} className="hover:text-secondary transition-colors cursor-pointer text-left">
                  Luxury Transport & Fleets
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('niche-showcase')} className="hover:text-secondary transition-colors cursor-pointer text-left">
                  Real Estate Brokerages
                </button>
              </li>
              <li>
                <button onClick={() => scrollTo('niche-showcase')} className="hover:text-secondary transition-colors cursor-pointer text-left">
                  Fine Hospitality & Dining
                </button>
              </li>
            </ul>
          </div>

          {/* Architecture & Tech */}
          <div>
            <h4 className="font-bold text-sm text-primary uppercase tracking-wider mb-4">Architecture</h4>
            <ul className="space-y-2.5 text-sm text-fg-muted">
              <li className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-secondary" />
                <span>LiveKit WebRTC Stack</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-accent" />
                <span>Deepgram Nova-2 Streaming</span>
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-emerald-600" />
                <span>Redis Stack Caching</span>
              </li>
              <li className="flex items-center gap-1.5">
                <PhoneCall className="w-3.5 h-3.5 text-primary" />
                <span>SIP Trunk Cold-Transfer</span>
              </li>
            </ul>
          </div>

          {/* Portals & Security */}
          <div>
            <h4 className="font-bold text-sm text-primary uppercase tracking-wider mb-4">Portals & Access</h4>
            <ul className="space-y-2.5 text-sm text-fg-muted">
              <li>
                <a 
                  href="http://localhost:5174" 
                  target="_blank" 
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-secondary transition-colors font-medium text-primary"
                >
                  <span>Client Admin Portal</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </a>
              </li>
              <li>
                <a 
                  href="http://localhost:5173" 
                  target="_blank" 
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-secondary transition-colors font-medium text-primary"
                >
                  <span>Super Admin Portal</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </a>
              </li>
              <li className="pt-2">
                <div className="flex items-center gap-1 text-xs text-slate-500 font-medium">
                  <Shield className="w-3.5 h-3.5 text-emerald-600" />
                  <span>SOC2 & HIPAA Compliant Data Flow</span>
                </div>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-fg-muted">
          <p>© {new Date().getFullYear()} A.L.F.I.E Voice AI Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="cursor-pointer hover:text-primary transition-colors">Privacy Policy</span>
            <span className="cursor-pointer hover:text-primary transition-colors">Terms of Service</span>
            <span className="cursor-pointer hover:text-primary transition-colors">Security Architecture</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
