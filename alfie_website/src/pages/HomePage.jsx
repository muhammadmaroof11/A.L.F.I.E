import React, { useState } from 'react';
import Navbar from '../components/layout/Navbar';
import HeroSection from '../components/hero/HeroSection';
import TrustStrip from '../components/sections/TrustStrip';
import BusinessScaleSection from '../components/sections/BusinessScaleSection';
import ProblemSolution from '../components/sections/ProblemSolution';
import HowItWorks from '../components/sections/HowItWorks';
import NicheShowcase from '../components/sections/NicheShowcase';
import ROICalculator from '../components/sections/ROICalculator';
import DemoArena from '../components/sections/DemoArena';
import Pricing from '../components/sections/Pricing';
import Footer from '../components/layout/Footer';
import ScrollProgress from '../components/ui/ScrollProgress';

export default function HomePage() {
  const [activeDemoNiche, setActiveDemoNiche] = useState('clinic');

  const handleStartDemo = (niche = 'clinic') => {
    setActiveDemoNiche(niche);
    const element = document.getElementById('demo-arena');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-slate-900 selection:text-white relative overflow-x-hidden">
      
      {/* Top Reading Progress Bar */}
      <ScrollProgress />

      {/* Sticky Navigation */}
      <Navbar onOpenDemo={() => handleStartDemo('clinic')} />

      {/* Main Flow */}
      <main>
        {/* 1. Hero Section: Autonomous Telephony Command Center */}
        <HeroSection onStartDemo={(niche) => handleStartDemo(niche)} />

        {/* 2. Global Telephony Network Benchmarks */}
        <TrustStrip />

        {/* 3. Interactive Signal Flow Architecture */}
        <ProblemSolution />

        {/* 4. Dual-Audience Scale (Solo Shop to Enterprise) */}
        <BusinessScaleSection />

        {/* 5. Frictionless 3-Step Setup */}
        <HowItWorks />

        {/* 6. Industry Solutions Showcase & Persona Studio */}
        <NicheShowcase onSelectNiche={(nicheId) => handleStartDemo(nicheId)} />

        {/* 7. Interactive ROI Impact Calculator */}
        <ROICalculator />

        {/* 8. Live WebRTC Voice Call Sandbox with Holographic Orb */}
        <DemoArena initialNiche={activeDemoNiche} />

        {/* 9. Transparent Predictable SaaS Pricing & FAQ */}
        <Pricing />
      </main>

      {/* Enterprise Matrix Footer */}
      <Footer />

    </div>
  );
}
