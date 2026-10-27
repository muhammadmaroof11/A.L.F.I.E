import React, { useEffect, useRef } from 'react';

export default function WaveformEqualizer({
  isActive = false,
  barCount = 28,
  className = "h-12 w-full",
  activeColor = "bg-blue-600",
  idleColor = "bg-zinc-200",
}) {
  const barsRef = useRef([]);

  useEffect(() => {
    let animationFrame;
    let phase = 0;

    const animate = () => {
      phase += 0.08;
      barsRef.current.forEach((bar, i) => {
        if (!bar) return;
        if (isActive) {
          // Compound sine waves for realistic organic voice audio spectrum
          const s1 = Math.sin(phase + i * 0.35);
          const s2 = Math.cos(phase * 1.5 + i * 0.2);
          const s3 = Math.sin(phase * 0.7 - i * 0.15);
          const normalized = (s1 + s2 + s3 + 3) / 6; // 0 to 1
          const heightPercent = Math.max(15, Math.min(100, normalized * 90 + 10));
          bar.style.height = `${heightPercent}%`;
          bar.style.opacity = `${0.6 + normalized * 0.4}`;
        } else {
          // Idle ambient gentle breathing
          const idleH = Math.sin(phase * 0.3 + i * 0.2) * 8 + 18;
          bar.style.height = `${idleH}%`;
          bar.style.opacity = '0.4';
        }
      });

      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [isActive]);

  return (
    <div className={`flex items-center justify-center gap-1 overflow-hidden select-none ${className}`}>
      {Array.from({ length: barCount }).map((_, idx) => (
        <div
          key={idx}
          ref={(el) => (barsRef.current[idx] = el)}
          className={`w-1 rounded-full transition-all duration-75 ${
            isActive ? activeColor : idleColor
          }`}
          style={{ height: '20%' }}
        />
      ))}
    </div>
  );
}
