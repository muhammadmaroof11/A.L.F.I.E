import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Menu, 
  X, 
  ChevronDown, 
  PhoneCall, 
  ArrowUpRight,
  Stethoscope,
  Scale,
  Building2,
  Car,
  UtensilsCrossed,
  Scissors,
  Zap,
  CalendarCheck,
  MessageSquareCheck,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from '../ui/button';

const dedicatedSolutionPages = [
  { 
    name: 'Medical & Dental Clinics', 
    path: '/clinics', 
    badge: 'EHR Sync', 
    desc: 'Insurance verification & patient chair lock', 
    icon: Stethoscope,
    iconBg: 'bg-blue-50 text-blue-600 border-blue-200/80'
  },
  { 
    name: 'Personal Injury Law', 
    path: '/law-firms', 
    badge: 'Retainer Triage', 
    desc: 'Case qualification & attorney transfer', 
    icon: Scale,
    iconBg: 'bg-indigo-50 text-indigo-600 border-indigo-200/80'
  },
  { 
    name: 'Real Estate Brokerages', 
    path: '/real-estate', 
    badge: 'Showing Tours', 
    desc: 'MLS inventory matching & showing scheduling', 
    icon: Building2,
    iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-200/80'
  },
  { 
    name: 'Luxury Transport & Fleets', 
    path: '/car-rental', 
    badge: 'Stripe Deposit', 
    desc: 'Instant distance quotes & fleet dispatch', 
    icon: Car,
    iconBg: 'bg-amber-50 text-amber-600 border-amber-200/80'
  },
  { 
    name: 'Fine Hospitality & Dining', 
    path: '/hospitality', 
    badge: 'VIP Booking', 
    desc: 'Table reservations & VIP concierge', 
    icon: UtensilsCrossed,
    iconBg: 'bg-rose-50 text-rose-600 border-rose-200/80'
  }
];

const capabilitySolutions = [
  {
    name: '24/7 Autonomous Booking',
    path: '#signal-pipeline',
    desc: 'Sub-second voice intercept with zero hold time',
    icon: Zap
  },
  {
    name: 'Live Calendar & CRM Sync',
    path: '#how-it-works',
    desc: 'Direct 2-way sync into Square, EHR & Salesforce',
    icon: CalendarCheck
  },
  {
    name: 'Instant Omni-Lock SMS',
    path: '#demo-arena',
    desc: 'Automated post-call SMS receipts & direction links',
    icon: MessageSquareCheck
  }
];

export default function Navbar({ onOpenDemo }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const dropdownRef = useRef(null);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    setDropdownOpen(false);

    if (location.pathname !== '/') {
      navigate('/#' + id);
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } else {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const handleLogoClick = () => {
    if (location.pathname !== '/') {
      navigate('/');
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <header className={`fixed top-0 inset-x-0 z-50 transition-all duration-200 ${scrolled
      ? 'bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs h-14'
      : 'bg-white/90 backdrop-blur-md border-b border-slate-200/60 h-14'
      }`}>
      <div className="w-full px-4 sm:px-6 lg:px-8 flex items-center justify-between h-full">

        {/* Left: Logo + Vibrant Gradient Brand Title */}
        <div
          className="flex items-center gap-4 sm:gap-5 cursor-pointer select-none shrink-0 group"
          onClick={handleLogoClick}
        >
          <img
            src="/logo.webp"
            onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = '/logo.png'; }}
            alt="A.L.F.I.E Logo"
            className="h-8 sm:h-9 w-auto object-contain transition-transform scale-105"
          />
          <span className="font-black text-lg sm:text-xl tracking-[0.24em] sm:tracking-[0.32em] text-[#008BC5] font-heading uppercase inline-block scale-x-[1.04] origin-left">
            A.L.F.I.E
          </span>
        </div>

        {/* Center: Meaningful Navigation Links */}
        <nav className="hidden lg:flex items-center gap-8 text-sm font-semibold text-slate-600">

          {/* Solutions Dropdown (2-Column Mega-Menu) */}
          <div className="relative" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-1.5 hover:text-slate-900 transition-colors cursor-pointer py-2 text-slate-600 group"
            >
              <span>Solutions</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform text-slate-400 group-hover:text-slate-900 ${dropdownOpen ? 'rotate-180 text-slate-900' : ''}`} />
            </button>

            <AnimatePresence>
              {dropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.98 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                  className="absolute top-full left-0 mt-2 w-[640px] rounded-3xl bg-white border border-slate-200 shadow-2xl overflow-hidden p-4 sm:p-5 z-50 ring-1 ring-slate-900/5"
                >
                  <div className="grid grid-cols-12 gap-5">
                    
                    {/* Left Column (7 cols): Dedicated Industry Pages */}
                    <div className="col-span-7 space-y-2.5">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
                          <span>Dedicated Industry Pages</span>
                        </span>
                        <span className="text-[10px] text-blue-600 font-mono font-semibold bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200/70">
                          Turnkey Apps
                        </span>
                      </div>

                      <div className="grid grid-cols-1 gap-1">
                        {dedicatedSolutionPages.map((item) => {
                          const IconComp = item.icon;
                          return (
                            <Link
                              key={item.path}
                              to={item.path}
                              onClick={() => setDropdownOpen(false)}
                              className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-slate-50 transition-all group border border-transparent hover:border-slate-200/80"
                            >
                              <div className={`w-7 h-7 rounded-lg border flex items-center justify-center shrink-0 ${item.iconBg}`}>
                                <IconComp className="w-3.5 h-3.5" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                  <span className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors font-heading truncate">
                                    {item.name}
                                  </span>
                                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 group-hover:text-blue-600 transition-all shrink-0 ml-1" />
                                </div>
                                <span className="text-[10px] text-slate-500 block truncate leading-tight">
                                  {item.desc}
                                </span>
                              </div>
                            </Link>
                          );
                        })}
                      </div>
                    </div>

                    {/* Right Column (5 cols): Platform Capabilities */}
                    <div className="col-span-5 bg-slate-50/80 rounded-2xl p-3.5 border border-slate-200/60 flex flex-col justify-between space-y-3">
                      <div>
                        <div className="pb-2 border-b border-slate-200/60 mb-2.5">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                            Core Engine Solutions
                          </span>
                        </div>

                        <div className="space-y-2">
                          {capabilitySolutions.map((item, idx) => {
                            const IconComp = item.icon;
                            return (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => scrollToSection(item.path.replace('#', ''))}
                                className="w-full text-left p-2 rounded-xl bg-white border border-slate-200/80 hover:border-slate-300 shadow-2xs hover:shadow-xs transition-all group block cursor-pointer"
                              >
                                <div className="flex items-center gap-2 mb-0.5">
                                  <IconComp className="w-3.5 h-3.5 text-cyan-600 shrink-0" />
                                  <span className="text-xs font-bold text-slate-900 group-hover:text-cyan-600 transition-colors">
                                    {item.name}
                                  </span>
                                </div>
                                <p className="text-[10px] text-slate-500 leading-snug pl-5">
                                  {item.desc}
                                </p>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      <div className="pt-2 border-t border-slate-200/60 text-[10px] font-mono text-slate-500 text-center">
                        <span>Sub-Second Intake • 24/7 Sync</span>
                      </div>
                    </div>

                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            type="button"
            onClick={() => scrollToSection('how-it-works')}
            className="hover:text-slate-900 transition-colors cursor-pointer text-slate-600"
          >
            How It Works
          </button>

          <button
            type="button"
            onClick={() => scrollToSection('niche-showcase')}
            className="hover:text-slate-900 transition-colors cursor-pointer text-slate-600"
          >
            Industries
          </button>

          <button
            type="button"
            onClick={() => scrollToSection('roi-calculator')}
            className="hover:text-slate-900 transition-colors cursor-pointer text-slate-600"
          >
            ROI Calculator
          </button>

          <button
            type="button"
            onClick={() => scrollToSection('pricing')}
            className="hover:text-slate-900 transition-colors cursor-pointer text-slate-600"
          >
            Pricing
          </button>

        </nav>

        {/* Right: Query / Sign Up + Try Live Demo Buttons */}
        <div className="hidden sm:flex items-center gap-2.5 shrink-0">
          <Button
            size="sm"
            variant="outline"
            onClick={() => scrollToSection('pricing')}
            className="text-xs font-semibold text-slate-700 hover:text-slate-900 border-slate-200 hover:bg-slate-50 px-3 py-1.5 h-8.5 rounded-lg cursor-pointer"
          >
            <span>Inquire / Sign Up</span>
          </Button>

          <Button
            size="sm"
            variant="primary"
            onClick={() => {
              if (onOpenDemo) onOpenDemo();
              else scrollToSection('demo-arena');
            }}
            className="gap-1.5 text-xs font-semibold bg-[#008BC5] text-white hover:bg-[#007cae] px-3.5 py-1.5 h-8.5 rounded-lg cursor-pointer shadow-xs border-0"
          >
            <PhoneCall className="w-3.5 h-3.5 text-white" />
            <span>Try Live Demo</span>
          </Button>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex lg:hidden items-center">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="text-slate-600 hover:text-slate-900 p-2 cursor-pointer"
            aria-label="Toggle Menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6 text-slate-900" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-white/98 backdrop-blur-2xl border-b border-slate-200 px-6 py-6 space-y-4 shadow-xl overflow-hidden"
          >
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 font-mono">
              Dedicated Solutions
            </div>

            <div className="space-y-1">
              {dedicatedSolutionPages.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className="py-2 px-3 rounded-xl hover:bg-slate-50 text-slate-700 hover:text-slate-900 transition-colors flex items-center justify-between text-xs font-semibold"
                >
                  <span>{item.name}</span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
                </Link>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-200 flex flex-col gap-3 text-xs font-semibold text-slate-600">
              <button
                type="button"
                onClick={() => scrollToSection('how-it-works')}
                className="text-left py-2 hover:text-slate-900"
              >
                How It Works
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('niche-showcase')}
                className="text-left py-2 hover:text-slate-900"
              >
                Industries
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('roi-calculator')}
                className="text-left py-2 hover:text-slate-900"
              >
                ROI Calculator
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('pricing')}
                className="text-left py-2 hover:text-slate-900"
              >
                Pricing
              </button>
            </div>

            <div className="pt-4 flex flex-col gap-2">
              <Button
                variant="outline"
                onClick={() => scrollToSection('pricing')}
                className="w-full text-xs font-semibold text-slate-700 border-slate-200"
              >
                <span>Inquire / Sign Up</span>
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  if (onOpenDemo) onOpenDemo();
                  else scrollToSection('demo-arena');
                }}
                className="w-full gap-2 text-xs font-bold bg-[#008BC5] text-white hover:bg-[#007cae] border-0"
              >
                <PhoneCall className="w-4 h-4 text-white" />
                <span>Try Live Demo</span>
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </header>
  );
}

