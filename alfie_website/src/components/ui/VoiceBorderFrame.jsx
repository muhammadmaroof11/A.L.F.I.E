import React from 'react';

/**
 * VoiceBorderFrame (Siri Circular Lively Voice Border)
 * 
 * Replaces all previous telemetry, ticks, badges, and boxes with a pure,
 * mesmerizing circular border that moves lively like Apple Siri.
 * 
 * Features:
 * 1. 100% geometric circular portal (rounded-full aspect-square).
 * 2. Multi-layer lively chromatic Siri aura:
 *    - Ambient breathing bloom (blur-2xl with breathing scale and rotation).
 *    - Counter-rotating mid aura (blur-md with fluid reverse rotation).
 *    - Crisp, vivid 3px rotating border ring with chromatic pulse.
 * 3. Pristine white interior:
 *    - Children / mascot video is 100% uncropped, centered, and unobstructed.
 * 4. Pure minimalism: nothing else.
 */
export default function VoiceBorderFrame({
  children,
  className = "",
}) {
  const siriGradient1 = `conic-gradient(
    from 0deg,
    #008BC5 0deg,
    #38BDF8 45deg,
    #818CF8 105deg,
    #C084FC 165deg,
    #F43F5E 220deg,
    #06B6D4 280deg,
    #38BDF8 330deg,
    #008BC5 360deg
  )`;

  const siriGradient2 = `conic-gradient(
    from 180deg,
    #38BDF8 0deg,
    #F43F5E 65deg,
    #C084FC 130deg,
    #818CF8 190deg,
    #008BC5 250deg,
    #06B6D4 310deg,
    #38BDF8 360deg
  )`;

  return (
    <div className={`relative rounded-full aspect-square flex items-center justify-center select-none ${className}`}>
      
      {/* ── Layer 1: Ambient Outer Siri Bloom (Breathing & Rotating Glow) ── */}
      <div
        className="absolute -inset-3.5 sm:-inset-4 rounded-full blur-xl sm:blur-2xl opacity-70 animate-siri-breathe animate-siri-spin pointer-events-none"
        style={{ background: siriGradient1 }}
      />

      {/* ── Layer 2: Fluid Counter-Rotating Mid Glow ── */}
      <div
        className="absolute -inset-2 rounded-full blur-md opacity-80 animate-siri-spin-reverse pointer-events-none"
        style={{ background: siriGradient2 }}
      />

      {/* ── Layer 3: Crisp Lively Circular Siri Border Ring ── */}
      <div
        className="absolute -inset-[3px] rounded-full animate-siri-spin animate-siri-pulse-ring pointer-events-none shadow-[0_0_20px_rgba(0,139,197,0.4)]"
        style={{ background: siriGradient1 }}
      />

      {/* ── Inner Portal: Pristine White Circular Container ── */}
      <div className="relative w-full h-full rounded-full bg-white overflow-hidden shadow-[inset_0_0_20px_rgba(0,139,197,0.06),0_12px_36px_rgba(0,0,0,0.06)] flex items-center justify-center p-2.5 sm:p-3 z-10">
        {children}
      </div>

    </div>
  );
}
