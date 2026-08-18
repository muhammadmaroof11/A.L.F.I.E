import React, { useState, useEffect } from 'react';
import { Phone, ArrowRight, Activity, Menu, X, Shield, Lock } from 'lucide-react';

export default function Navbar({ onOpenDemo }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 15);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
        scrolled 
          ? 'bg-[#0B0F17]/90 backdrop-blur-xl border-b border-white/[0.06] py-3 shadow-[0_4px_20px_rgba(0,0,0,0.5)]' 
          : 'bg-transparent py-4 sm:py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          
          {/* Logo & System Brand */}
          <div 
            className="flex items-center gap-2.5 cursor-pointer select-none" 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <img 
              src="/logo.png" 
              alt="A.L.F.I.E Logo" 
              className="h-8 w-auto object-contain rounded-lg"
            />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-white">A.L.F.I.E</span>
                <span className="cd-badge-live text-[10px] py-0.5 px-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  WebRTC Live
                </span>
              </div>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-white/[0.05] p-1 rounded-xl border border-white/[0.08] text-xs font-semibold text-slate-300">
            <button 
              onClick={() => scrollToSection('niche-showcase')}
              className="px-3.5 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all cursor-pointer"
            >
              Domain Engines
            </button>
            <button 
              onClick={() => scrollToSection('how-it-works')}
              className="px-3.5 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all cursor-pointer"
            >
              Telephony Pipeline
            </button>
            <button 
              onClick={() => scrollToSection('roi-calculator')}
              className="px-3.5 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all cursor-pointer"
            >
              ROI Modeler
            </button>
            <button 
              onClick={() => scrollToSection('pricing')}
              className="px-3.5 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all cursor-pointer"
            >
              Enterprise SaaS
            </button>
          </nav>

          {/* Action CTAs */}
          <div className="hidden sm:flex items-center gap-2.5">
            <a
              href="http://localhost:5174" 
              target="_blank" 
              rel="noreferrer"
              className="px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Lock className="w-3.5 h-3.5 text-slate-500" />
              <span>Tenant Portal</span>
            </a>
            <button
              onClick={() => {
                if (onOpenDemo) onOpenDemo();
                else scrollToSection('demo-arena');
              }}
              className="cd-btn-primary text-xs py-2 px-4 rounded-xl"
            >
              <Phone className="w-3.5 h-3.5 text-blue-200" />
              <span>Launch Live Call</span>
              <ArrowRight className="w-3 h-3 opacity-70" />
            </button>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => scrollToSection('demo-arena')}
              className="cd-btn-primary p-2 rounded-lg text-xs"
              aria-label="Call Demo"
            >
              <Phone className="w-4 h-4" />
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 rounded-lg hover:bg-white/10"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 pb-3 border-t border-white/[0.06] bg-[#111726]/95 backdrop-blur-lg rounded-2xl p-4 shadow-xl flex flex-col gap-2.5">
            <button 
              onClick={() => scrollToSection('niche-showcase')}
              className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-300 hover:bg-white/[0.06]"
            >
              Domain Engines (Legal, Clinics, Fleets)
            </button>
            <button 
              onClick={() => scrollToSection('how-it-works')}
              className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-300 hover:bg-white/[0.06]"
            >
              Telephony Pipeline
            </button>
            <button 
              onClick={() => scrollToSection('roi-calculator')}
              className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-300 hover:bg-white/[0.06]"
            >
              ROI Modeler
            </button>
            <button 
              onClick={() => scrollToSection('pricing')}
              className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-300 hover:bg-white/[0.06]"
            >
              Enterprise SaaS
            </button>
            <div className="pt-2 border-t border-white/[0.08] flex flex-col gap-2">
              <a
                href="http://localhost:5174"
                className="cd-btn-secondary py-2 rounded-xl text-center text-xs font-semibold"
              >
                Tenant Portal Login
              </a>
              <button
                onClick={() => scrollToSection('demo-arena')}
                className="cd-btn-primary py-2 rounded-xl text-center text-xs font-semibold"
              >
                Launch Live 90s Call
              </button>
            </div>
          </div>
        )}

      </div>
    </header>
  );
}
