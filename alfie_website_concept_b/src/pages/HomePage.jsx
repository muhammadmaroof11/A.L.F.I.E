import React, { useState } from 'react';
import Navbar from '../components/layout/Navbar';
import HeroSection from '../components/hero/HeroSection';
import TrustStrip from '../components/sections/TrustStrip';
import ProblemSolution from '../components/sections/ProblemSolution';
import NicheShowcase from '../components/sections/NicheShowcase';
import HowItWorks from '../components/sections/HowItWorks';
import ROICalculator from '../components/sections/ROICalculator';
import DemoArena from '../components/sections/DemoArena';
import Pricing from '../components/sections/Pricing';
import Footer from '../components/layout/Footer';

export default function HomePage() {
  const [activeDemoNiche, setActiveDemoNiche] = useState('legal');

  const handleStartDemo = (niche = 'legal') => {
    setActiveDemoNiche(niche);
    const element = document.getElementById('demo-arena');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-[#F8FAFC] font-sans selection:bg-blue-600 selection:text-white relative">
      
      {/* Sticky Navigation */}
      <Navbar onOpenDemo={() => handleStartDemo('legal')} />

      {/* Main Flow */}
      <main>
        {/* 1. Hero Section with 3D Headset Model */}
        <HeroSection onStartDemo={() => handleStartDemo('legal')} />

        {/* 2. Trust Marquee */}
        <TrustStrip />

        {/* 3. Problem -> Solution Transformation */}
        <ProblemSolution />

        {/* 4. 5 Vertical Showcase with 3D Badges */}
        <NicheShowcase onSelectNiche={(nicheId) => handleStartDemo(nicheId)} />

        {/* 5. How It Works (3-Step Pipeline with 3D Models) */}
        <HowItWorks />

        {/* 6. Interactive ROI Calculator */}
        <ROICalculator />

        {/* 7. Live 90-Second Browser Voice Call Arena */}
        <DemoArena initialNiche={activeDemoNiche} />

        {/* 8. 3-Tier SaaS Pricing Cards */}
        <Pricing />
      </main>

      {/* Enterprise Footer */}
      <Footer />

    </div>
  );
}
