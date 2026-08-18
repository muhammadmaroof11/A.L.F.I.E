# Concept B: "CINEMA DISPATCH" — Full Implementation Guide

> **Target Executor**: Gemini Flash 3.7 (labor) — supervised by Gemini 2.5 Pro (harder tasks)  
> **Stack**: Vite + React 19 + Tailwind v4 (`@import "tailwindcss"`) + Three.js/R3F + GSAP + Lucide

---

## Architecture Summary

Full-dark cinematic immersion. The **entire page** lives on a dark navy-black canvas. Every single section gets dark-mode treatment. The hero features an ambient video background (`hero_bg.mp4`), a continuously flowing SVG soundwave, and the 3D headset with the waveform badge inside its arch. Before/After uses full-bleed photography with dramatic gradient overlays.

> [!CAUTION]
> This concept requires modifying **every component** to use dark color tokens. This is significantly more work than Concept A. Recommend doing the full CSS system first, then updating components one at a time.

## Files Changed (Priority Order)

| Priority | File | Change Type | Difficulty |
|:---:|:---|:---|:---|
| 1 | `src/index.css` | **MAJOR REWRITE** — Dark tokens + new utility classes | Flash 3.7 |
| 2 | `src/pages/HomePage.jsx` | **EDIT** — Dark page container | Flash 3.7 |
| 3 | `src/components/hero/HeroSection.jsx` | **REWRITE** — Full-dark cinematic hero | Flash 3.7 |
| 4 | `src/components/layout/Navbar.jsx` | **EDIT** — Always-dark frosted glass | Flash 3.7 |
| 5 | `src/components/sections/TrustStrip.jsx` | **REWRITE** — Dark glowing pills | Flash 3.7 |
| 6 | `src/components/sections/ProblemSolution.jsx` | **REWRITE** — Dark photo theater | Flash 3.7 |
| 7 | `src/components/sections/NicheShowcase.jsx` | **EDIT** — Dark surface + tab pills | Flash 3.7 |
| 8 | `src/components/sections/HowItWorks.jsx` | **EDIT** — Dark surface + glow connectors | Flash 3.7 |
| 9 | `src/components/sections/ROICalculator.jsx` | **EDIT** — Dark surface + glow numbers | Flash 3.7 |
| 10 | `src/components/sections/DemoArena.jsx` | **EDIT** — Dark WebRTC panel | Flash 3.7 |
| 11 | `src/components/sections/Pricing.jsx` | **EDIT** — Dark glass cards | Flash 3.7 |
| 12 | `src/components/layout/Footer.jsx` | **EDIT** — Dark footer | Flash 3.7 |
| 13 | `src/components/3d/ModelViewer.jsx` | **EDIT** — Dark lighting env | **2.5 Pro** |

---

## Dark Color System (Reference for all files)

Every file below uses this color mapping. Memorize this before starting:

| Token Name | Hex | CSS Variable | Usage |
|:---|:---|:---|:---|
| `bg-depth-0` | `#060A13` | `--cd-bg-0` | Deepest background (footer) |
| `bg-depth-1` | `#091728` | `--cd-bg-1` | Primary section background |
| `bg-depth-2` | `#0B0F17` | `--cd-bg-2` | Hero / main canvas |
| `bg-depth-3` | `#111726` | `--cd-bg-3` | Elevated cards, trust strip |
| `bg-depth-4` | `#182238` | `--cd-bg-4` | Interactive card hover |
| `text-bright` | `#F8FAFC` | — | Primary text |
| `text-mid` | `#CBD5E1` | — | Body text |
| `text-muted` | `#94A3B8` | — | Secondary text |
| `text-dim` | `#64748B` | — | Tertiary / mono text |
| `accent-cyan` | `#38BDF8` | — | Waveforms, live indicators |
| `accent-blue` | `#60A5FA` | — | Links, secondary accents |
| `accent-indigo` | `#818CF8` | — | Tertiary accents |
| `border-glass` | `rgba(255,255,255,0.08)` | — | All borders |
| `border-glow` | `rgba(56,189,248,0.25)` | — | Hover glow borders |

---

## 1. `src/index.css` — Full Specification

**Instruction**: Keep the `@import "tailwindcss"` and `@theme` block. REPLACE everything after `@theme { ... }` with the following. The `@theme` block should be kept but its values don't need changing (they're overridden by component-level classes).

### Append AFTER existing `@theme` block (keep `@theme` + `@import "tailwindcss"`)

```css
/* ═══════════════════════════════════════════════════════════════
   CONCEPT B: CINEMA DISPATCH — Full-Dark Cinematic Tokens
   ═══════════════════════════════════════════════════════════════ */

:root {
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --cd-bg-0: #060A13;
  --cd-bg-1: #091728;
  --cd-bg-2: #0B0F17;
  --cd-bg-3: #111726;
  --cd-bg-4: #182238;
  --cd-accent: #38BDF8;
  --cd-glow: rgba(56, 189, 248, 0.15);
}

html {
  scroll-behavior: smooth;
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
}

body {
  background-color: var(--cd-bg-2);
  color: #F8FAFC;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── Section Surface Classes ── */
.cd-section {
  background-color: var(--cd-bg-1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.cd-section-alt {
  background-color: var(--cd-bg-2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ── Card Surfaces ── */
.cd-card {
  background-color: var(--cd-bg-3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border-radius: 1rem;
  transition: border-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.cd-card:hover {
  border-color: rgba(56, 189, 248, 0.2);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 20px var(--cd-glow);
  transform: translateY(-2px);
}

.cd-card-static {
  background-color: var(--cd-bg-3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border-radius: 1rem;
}

/* ── Glassmorphism ── */
.cd-glass {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px) saturate(1.3);
  -webkit-backdrop-filter: blur(20px) saturate(1.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* ── Buttons ── */
.cd-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: #2563EB;
  color: #FFFFFF;
  font-weight: 700;
  font-size: 0.875rem;
  padding: 0.75rem 1.375rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(37, 99, 235, 0.6);
  box-shadow: 0 0 20px rgba(37, 99, 235, 0.2), 0 2px 4px rgba(0, 0, 0, 0.3);
  transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.cd-btn-primary:hover {
  background-color: #1D4ED8;
  box-shadow: 0 0 30px rgba(37, 99, 235, 0.35), 0 4px 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-1px);
}

.cd-btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: transparent;
  color: #CBD5E1;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.cd-btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  color: #F8FAFC;
  transform: translateY(-1px);
}

/* ── Badges ── */
.cd-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: rgba(255, 255, 255, 0.05);
  color: #CBD5E1;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.cd-badge-live {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: rgba(5, 150, 105, 0.12);
  color: #34D399;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

/* ── Glow Border on Hover ── */
.cd-glow-border {
  transition: box-shadow 0.3s ease;
}

.cd-glow-border:hover {
  box-shadow: 0 0 20px var(--cd-glow);
}

/* ── Animated Audio Spectrum ── */
@keyframes spectrum-pulse {
  0% { transform: scaleY(0.15); }
  50% { transform: scaleY(1); }
  100% { transform: scaleY(0.25); }
}

.spectrum-bar {
  transform-origin: bottom;
  animation: spectrum-pulse 0.9s ease-in-out infinite alternate;
}

/* ── Continuous Flowing Soundwave ── */
@keyframes wave-travel-1 {
  0% { transform: translateX(0) translateZ(0); }
  100% { transform: translateX(-50%) translateZ(0); }
}

@keyframes wave-travel-2 {
  0% { transform: translateX(-50%) translateZ(0); }
  100% { transform: translateX(0) translateZ(0); }
}

@keyframes wave-breathe {
  0%, 100% { transform: translateY(0) scaleY(1); }
  50% { transform: translateY(-10px) scaleY(1.04); }
}

.animate-wave-travel-1 {
  animation: wave-travel-1 22s linear infinite;
}

.animate-wave-travel-2 {
  animation: wave-travel-2 28s linear infinite;
}

.animate-wave-breathe {
  animation: wave-breathe 7s ease-in-out infinite;
}

/* ── Latency Pulse ── */
@keyframes latency-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.latency-counter {
  animation: latency-pulse 2s ease-in-out infinite;
}

/* ── Dark Grid Pattern ── */
.bg-grid-dark {
  background-size: 32px 32px;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
}

/* ── Hide scrollbar ── */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* ── Keep existing btn-primary/btn-secondary for any leftover usage ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: #2563EB;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.75rem 1.375rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(37, 99, 235, 0.5);
  box-shadow: 0 0 16px rgba(37, 99, 235, 0.15);
  transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #1D4ED8;
  box-shadow: 0 0 24px rgba(37, 99, 235, 0.3);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: transparent;
  color: #CBD5E1;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* ── Badge ── */
.badge-live {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: rgba(5, 150, 105, 0.12);
  color: #34D399;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.badge-neutral {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.05);
  color: #94A3B8;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

> [!IMPORTANT]
> The `@import "tailwindcss"` line and the entire `@theme { ... }` block at the top of the file must remain unchanged. The `@theme` block defines Tailwind v4 design tokens. Everything AFTER the closing `}` of `@theme` should be replaced with the CSS above.

---

## 2. `src/pages/HomePage.jsx` — Edit Specification

**Change**: The page container's className.

```
BEFORE: className="min-h-screen bg-bg text-fg font-sans selection:bg-secondary selection:text-white relative"
AFTER:  className="min-h-screen bg-[#0B0F17] text-[#F8FAFC] font-sans selection:bg-blue-600 selection:text-white relative"
```

Everything else in this file stays identical.

---

## 3. `src/components/hero/HeroSection.jsx` — Full Rewrite

**Instruction**: Replace the ENTIRE file. This is the cinematic dark hero with:
- Ambient `hero_bg.mp4` video background at low opacity
- Flowing SVG soundwave
- 3D headset with waveform inside arch (preserved from current design)

```jsx
import React from 'react';
import { Phone, ArrowRight, Zap, Play, CheckCircle2, Radio } from 'lucide-react';
import ModelViewer from '../3d/ModelViewer';
import ScrollReveal from '../shared/ScrollReveal';

export default function HeroSection({ onStartDemo }) {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  // 18 harmonic spectrum bars for the audio visualizer inside the headphones
  const spectrumDelays = [
    0.1, 0.35, 0.6, 0.2, 0.75, 0.4, 0.15, 0.85, 0.3,
    0.5, 0.25, 0.65, 0.18, 0.8, 0.38, 0.55, 0.28, 0.12
  ];

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-28 pb-16 bg-[#091728] overflow-hidden">
      
      {/* ── LAYER 1: Ambient Video Background ── */}
      <div className="absolute inset-0 z-0">
        <video 
          autoPlay 
          loop 
          muted 
          playsInline
          className="w-full h-full object-cover opacity-[0.12]"
        >
          <source src="/videos/hero_bg.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-[#091728]/60 via-[#091728]/40 to-[#091728]" />
      </div>

      {/* ── LAYER 2: Dark Grid Pattern ── */}
      <div className="absolute inset-0 bg-grid-dark pointer-events-none z-[1]" />

      {/* ── LAYER 3: Flowing SVG Soundwave ── */}
      <div className="absolute inset-0 pointer-events-none z-[2] overflow-hidden flex items-center">
        <div className="w-[200%] h-full flex shrink-0 animate-wave-travel-1 opacity-50">
          <svg 
            viewBox="0 0 2880 500" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg" 
            className="w-full h-full object-cover"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="cyanWaveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.5" />
                <stop offset="25%" stopColor="#60A5FA" stopOpacity="0.7" />
                <stop offset="50%" stopColor="#818CF8" stopOpacity="0.55" />
                <stop offset="75%" stopColor="#38BDF8" stopOpacity="0.65" />
                <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.5" />
              </linearGradient>

              <linearGradient id="dimWaveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.15" />
                <stop offset="50%" stopColor="#818CF8" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#38BDF8" stopOpacity="0.15" />
              </linearGradient>

              <filter id="waveGlow" x="-10%" y="-10%" width="120%" height="120%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Primary wave */}
            <path
              d="M 0,260 C 360,160 720,380 1080,330 C 1440,280 1800,160 2160,380 C 2520,330 2880,260 2880,260"
              stroke="url(#cyanWaveGrad)"
              strokeWidth="2.5"
              fill="none"
              strokeLinecap="round"
              filter="url(#waveGlow)"
            />

            {/* Secondary wave (dimmer, dashed) */}
            <path
              d="M 0,290 C 400,380 800,240 1200,350 C 1600,420 2000,240 2400,350 C 2800,420 2880,290 2880,290"
              stroke="url(#dimWaveGrad)"
              strokeWidth="1.75"
              strokeDasharray="5 7"
              fill="none"
            />
          </svg>
        </div>
      </div>

      {/* ── LAYER 4: Content ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-4 items-center">
          
          {/* Left Column: Editorial Typography */}
          <div className="lg:col-span-7 space-y-6 text-left">
            
            {/* Telemetry Pill */}
            <ScrollReveal y={15} duration={0.5}>
              <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-white/[0.05] backdrop-blur-md border border-white/[0.08] text-slate-300">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-mono text-slate-500 text-[11px]">TELEPHONY GATEWAY</span>
                <span className="text-slate-600">/</span>
                <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" /> 390ms Sub-Second TTFT
                </span>
              </div>
            </ScrollReveal>

            {/* Headline */}
            <ScrollReveal y={20} duration={0.6} delay={0.08}>
              <h1 className="text-4xl sm:text-5xl lg:text-[72px] font-black tracking-[-0.04em] text-white leading-[1.02]">
                Never Miss a $10,000+ Inbound Call Again.
              </h1>
            </ScrollReveal>

            {/* Sub-copy */}
            <ScrollReveal y={20} duration={0.6} delay={0.14}>
              <p className="text-base sm:text-lg text-slate-400 font-normal leading-relaxed max-w-xl">
                Autonomous, conversational voice AI infrastructure built for personal injury law practices, dental & medical clinics, and luxury fleet dispatch. Answers on the first ring, verifies case merits and insurance, and warm-transfers qualified leads to your cell.
              </p>
            </ScrollReveal>

            {/* CTAs */}
            <ScrollReveal y={15} duration={0.6} delay={0.2}>
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
                <button
                  onClick={() => {
                    if (onStartDemo) onStartDemo();
                    else scrollTo('demo-arena');
                  }}
                  className="cd-btn-primary w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5"
                >
                  <Phone className="w-4 h-4 text-blue-200" />
                  <span>Launch Live Call Demo</span>
                  <ArrowRight className="w-4 h-4 opacity-70" />
                </button>

                <button
                  onClick={() => scrollTo('niche-showcase')}
                  className="cd-btn-secondary w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2"
                >
                  <Play className="w-3.5 h-3.5 text-slate-400" />
                  <span>View Architecture Spec</span>
                </button>
              </div>
            </ScrollReveal>

            {/* Trust checklist */}
            <ScrollReveal y={10} duration={0.5} delay={0.25}>
              <div className="pt-2 flex flex-wrap items-center gap-5 text-xs text-slate-500 font-medium">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Zero Hardware Required</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Twilio / Telnyx SIP BYOK</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>SOC-2 & HIPAA Ready</span>
                </div>
              </div>
            </ScrollReveal>
          </div>

          {/* Right Column: 3D Headset + Waveform Inside */}
          <div className="lg:col-span-5 relative flex items-center justify-center">
            <div className="w-full aspect-[4/3] max-w-[460px] min-h-[340px] sm:min-h-[380px] relative flex items-center justify-center">
              
              <ModelViewer
                url="/models/hero_headset.glb"
                scale={1.32}
                rotation={[0.08, 0.42, -0.06]}
                autoRotate={false}
                enableFloat={false}
                cameraPosition={[0, 0, 4.5]}
                className="w-full h-full min-h-[340px] sm:min-h-[380px]"
              />

              {/* Waveform Badge Inside Headphone Arch */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 pt-6">
                <div className="w-fit max-w-[210px] bg-[#111726]/85 backdrop-blur-md px-3 py-2 rounded-xl border border-white/[0.08] shadow-sm flex flex-col items-center gap-1 pointer-events-auto transition-transform hover:scale-105">
                  
                  <div className="flex items-center gap-1.5 text-[9px] font-mono font-bold text-slate-300">
                    <Radio className="w-2.5 h-2.5 text-[#38BDF8] animate-pulse" />
                    <span>Live Channel • Opus 48k</span>
                  </div>

                  <div className="w-[170px] h-4 flex items-end justify-between gap-[2px] px-1 bg-white/[0.04] rounded p-0.5 border border-white/[0.06]">
                    {spectrumDelays.map((delay, idx) => (
                      <span
                        key={idx}
                        className="flex-1 rounded-full spectrum-bar"
                        style={{
                          height: '100%',
                          animationDelay: `${delay}s`,
                          backgroundColor: idx % 3 === 0 ? '#38BDF8' : idx % 2 === 0 ? '#60A5FA' : '#818CF8'
                        }}
                      />
                    ))}
                  </div>

                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

    </section>
  );
}
```

---

## 4. `src/components/layout/Navbar.jsx` — Edit Specification

The navbar is always over dark content now, so simplify: always use dark-mode styles.

### Changes (targeted line edits):

**Scrolled state className (line 27-29)**:
```
BEFORE: scrolled ? 'bg-white/95 backdrop-blur-md border-b border-slate-200/80 py-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-transparent py-4 sm:py-5'
AFTER:  scrolled ? 'bg-[#0B0F17]/90 backdrop-blur-xl border-b border-white/[0.06] py-3' : 'bg-transparent py-4 sm:py-5'
```

**A.L.F.I.E text (line 47)**:
```
BEFORE: className="font-extrabold text-lg tracking-tight text-slate-900"
AFTER:  className="font-extrabold text-lg tracking-tight text-white"
```

**Nav pill container (line 57)**:
```
BEFORE: className="hidden md:flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/70 text-xs font-semibold text-slate-600"
AFTER:  className="hidden md:flex items-center gap-1 bg-white/[0.05] p-1 rounded-xl border border-white/[0.08] text-xs font-semibold text-slate-400"
```

**Each nav button (lines 60, 66, 72, 78)**:
```
BEFORE: className="px-3.5 py-1.5 rounded-lg hover:text-slate-900 hover:bg-white transition-all cursor-pointer"
AFTER:  className="px-3.5 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all cursor-pointer"
```

**Tenant Portal link (line 90)**:
```
BEFORE: className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors flex items-center gap-1.5"
AFTER:  className="px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
```

**Lock icon (line 92)**:
```
BEFORE: className="w-3.5 h-3.5 text-slate-400"
AFTER:  className="w-3.5 h-3.5 text-slate-500"
```

**Mobile dropdown (line 129)**:
```
BEFORE: className="md:hidden mt-3 pt-3 pb-3 border-t border-slate-200 bg-white/98 backdrop-blur-lg rounded-2xl p-4 shadow-lg flex flex-col gap-2.5"
AFTER:  className="md:hidden mt-3 pt-3 pb-3 border-t border-white/[0.06] bg-[#111726]/95 backdrop-blur-lg rounded-2xl p-4 shadow-lg flex flex-col gap-2.5"
```

**Mobile menu buttons text (lines 132, 137, 142, 148)**:
```
BEFORE: className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
AFTER:  className="text-left py-2 px-3 rounded-lg text-xs font-semibold text-slate-300 hover:bg-white/[0.06]"
```

---

## 5-11. Section Components — Color Token Swap Guide

For **every remaining section component**, apply this systematic find-and-replace:

### Universal Color Token Mapping (apply to ALL sections)

| Find (Current) | Replace With (Cinema Dispatch) |
|:---|:---|
| `bg-white` | `bg-[#091728]` |
| `bg-[#FAFAFC]` | `bg-[#0B0F17]` |
| `bg-white/60` | `bg-[#111726]/60` |
| `bg-white/90` | `bg-[#111726]/90` |
| `bg-slate-50` | `bg-[#111726]` |
| `bg-slate-100` | `bg-white/[0.05]` |
| `bg-slate-100/80` | `bg-white/[0.05]` |
| `bg-amber-50` | `bg-amber-500/10` |
| `bg-sky-50` | `bg-sky-500/10` |
| `bg-emerald-50` | `bg-emerald-500/10` |
| `bg-emerald-50/70` | `bg-emerald-500/10` |
| `bg-red-50/70` | `bg-red-500/10` |
| `border-slate-200/80` | `border-white/[0.05]` |
| `border-slate-200/60` | `border-white/[0.04]` |
| `border-slate-200/70` | `border-white/[0.06]` |
| `border-slate-200` | `border-white/[0.06]` |
| `border-slate-100` | `border-white/[0.04]` |
| `border-red-200/90` | `border-red-500/20` |
| `border-red-200` | `border-red-500/15` |
| `border-red-100` | `border-red-500/10` |
| `border-blue-200/90` | `border-blue-500/20` |
| `border-blue-200` | `border-blue-500/15` |
| `border-blue-100` | `border-blue-500/10` |
| `text-slate-900` | `text-[#F8FAFC]` |
| `text-slate-800` | `text-[#E2E8F0]` |
| `text-slate-700` | `text-[#CBD5E1]` |
| `text-slate-600` | `text-[#94A3B8]` |
| `text-slate-500` | `text-[#64748B]` |
| `text-red-700` | `text-red-400` |
| `text-red-800` | `text-red-300` |
| `text-red-600` | `text-red-400` |
| `text-amber-800` | `text-amber-300` |
| `text-sky-800` | `text-sky-300` |
| `text-emerald-700` | `text-emerald-400` |
| `text-emerald-800` | `text-emerald-300` |
| `text-blue-600` | `text-[#38BDF8]` |
| `shadow-2xs` | `shadow-none` (or remove) |
| `shadow-xs` | `shadow-[0_2px_8px_rgba(0,0,0,0.3)]` |
| `shadow-sm` | `shadow-[0_4px_12px_rgba(0,0,0,0.3)]` |
| `ring-2 ring-slate-900/10` | `ring-2 ring-[#38BDF8]/20` |

### Per-Section Specifics:

#### `TrustStrip.jsx`
- Section: `bg-white border-b border-slate-200/80` → `bg-[#111726] border-b border-white/[0.05]`
- Badge container: `bg-slate-50/70 border border-slate-200/60` → `bg-white/[0.04] border border-white/[0.06]`
- Badge icon box: `bg-white border border-slate-200` → `bg-white/[0.06] border border-white/[0.08]`
- Icon default: `text-slate-700` → `text-slate-400`; hover: `text-blue-600` → `text-[#38BDF8]`

#### `ProblemSolution.jsx`
- Section: `bg-white` → `bg-[#091728]`
- Cards: `bg-[#FAFAFC]` → `bg-[#111726]`
- Photo overlays: keep the `from-slate-950/90` gradient (already dark)
- All text swaps per mapping above

#### `NicheShowcase.jsx`
- Section: `bg-[#FAFAFC]` → `bg-[#0B0F17]`
- Tab buttons active: `bg-white border-slate-900` → `bg-[#182238] border-[#38BDF8]/30`
- Tab buttons inactive: `bg-white/60 border-slate-200` → `bg-[#111726]/60 border-white/[0.06]`
- Tab active ring: `ring-2 ring-slate-900/10` → `ring-2 ring-[#38BDF8]/20`

#### `HowItWorks.jsx`
- Section: `bg-[#FAFAFC]` → `bg-[#091728]`
- Console card: `bg-white rounded-3xl border border-slate-200` → `bg-[#111726] rounded-3xl border border-white/[0.06]`
- Step buttons: same tab pattern as NicheShowcase
- Watermark badge: `bg-white/90` → `bg-[#111726]/90 border-white/[0.08]`

#### `ROICalculator.jsx`
- Section: `bg-white` → `bg-[#0B0F17]`
- Calculator card: `bg-[#FAFAFC]` → `bg-[#111726]`
- Slider value badges: `bg-white px-2.5 py-0.5 rounded-lg border border-slate-200` → `bg-white/[0.06] border-white/[0.08]`
- Revenue output text: Make the big number `text-[#38BDF8]` for glow effect

#### `DemoArena.jsx`
- Section: its bg → `bg-[#091728]`
- Call panel: apply dark card treatment
- All status text: per mapping above

#### `Pricing.jsx`
- Section: `bg-[#FAFAFC]` → `bg-[#0B0F17]`
- Cards: `bg-white` → `bg-[#111726] border border-white/[0.06]`
- Popular card: Add `border-[#38BDF8]/20 shadow-[0_0_20px_rgba(56,189,248,0.1)]`
- Check icons: `text-emerald-600` → `text-emerald-400`

#### `Footer.jsx`
- Footer: `bg-white border-t border-slate-200/90` → `bg-[#060A13] border-t border-white/[0.05]`
- Brand text: `text-slate-900` → `text-white`
- Body text: `text-fg-muted` → `text-slate-500`
- Links: `hover:text-secondary` → `hover:text-[#38BDF8]`
- Bottom bar: `text-fg-muted` → `text-slate-600`

---

## 12. `src/components/3d/ModelViewer.jsx` — Edit Specification

**Instruction**: Change the lighting to suit dark backgrounds.

**Line 52-55** — Lighting:
```
BEFORE:
<ambientLight intensity={0.95} />
<directionalLight position={[6, 8, 6]} intensity={1.5} color="#FFFFFF" />
<directionalLight position={[-6, 2, -4]} intensity={0.65} color="#E2E8F0" />
<pointLight position={[0, 4, 3]} intensity={0.7} color="#FFFFFF" />

AFTER:
<ambientLight intensity={0.6} />
<directionalLight position={[6, 8, 6]} intensity={1.8} color="#E2E8F0" />
<directionalLight position={[-6, 2, -4]} intensity={0.5} color="#38BDF8" />
<pointLight position={[0, 4, 3]} intensity={0.4} color="#818CF8" />
```

This gives the 3D models a cinematic blue-indigo rim light on dark backgrounds.

**Line 77** — Contact shadow color:
```
BEFORE: color="#0F2744"
AFTER:  color="#000000"
```

**Line 81** — Environment preset:
```
BEFORE: <Environment preset="city" />
AFTER:  <Environment preset="night" />
```

> [!WARNING]
> This ModelViewer change affects ALL 3D models site-wide (hero headset, HowItWorks pipeline models). Assign this to **Gemini 2.5 Pro** since lighting tuning may need visual iteration.

---

## Visual Verification Checklist

- [ ] Entire page is dark — no white sections visible
- [ ] Hero has ambient video playing at ~12% opacity behind content
- [ ] Flowing SVG soundwave animates continuously across hero
- [ ] 3D headset is tilted, static, with waveform badge inside arch
- [ ] Waveform bars animate with cyan/blue/indigo colors
- [ ] Navbar text is always light (white/slate-300)
- [ ] Scrolled navbar has dark glass background
- [ ] TrustStrip badges have subtle glow on dark surface
- [ ] Before/After cards have dark backgrounds with photo overlays
- [ ] Pricing popular card has cyan glow border
- [ ] Footer is darkest surface (#060A13)
- [ ] No white text on white background (contrast check)
- [ ] No console errors, no missing imports

---

## Model Recommendation for Execution

| Task | Recommended Model | Rationale |
|:---|:---|:---|
| `index.css` rewrite | **Flash 3.7** | Large CSS block but purely copy-paste |
| `HomePage.jsx` edit | **Flash 3.7** | 1 line change |
| `HeroSection.jsx` rewrite | **Flash 3.7** | Full JSX provided, just paste |
| `Navbar.jsx` targeted edits | **Flash 3.7** | ~10 line changes |
| All section color swaps | **Flash 3.7** | Systematic find-replace with mapping table |
| `ModelViewer.jsx` lighting | **Gemini 2.5 Pro** | May need visual iteration |
| Visual QA / final polish | **Gemini 2.5 Pro** | Debug any contrast or layout issues |

> [!TIP]
> **Execution order**: Do `index.css` first → `HomePage.jsx` → `HeroSection.jsx` → `Navbar.jsx` → then all sections top-to-bottom. This way the CSS utility classes exist before the components reference them.
