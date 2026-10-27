import React, { useEffect, useRef } from 'react';

export default function HolographicVoiceOrb({
  state = 'idle', // 'idle' | 'connecting' | 'listening' | 'speaking'
  size = 220,
  className = ""
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrame;
    let phase = 0;

    // Retina display scaling
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);

    const render = () => {
      ctx.clearRect(0, 0, size, size);
      const centerX = size / 2;
      const centerY = size / 2;
      phase += state === 'speaking' ? 0.07 : state === 'connecting' ? 0.09 : 0.035;

      // Dynamic color palette based on voice state
      let color1, color2, color3;
      if (state === 'speaking') {
        // Vibrant electric blue & cyan & purple
        color1 = 'rgba(37, 99, 235, 0.7)';
        color2 = 'rgba(56, 189, 248, 0.8)';
        color3 = 'rgba(129, 140, 248, 0.6)';
      } else if (state === 'listening') {
        // Emerald & mint green
        color1 = 'rgba(16, 185, 129, 0.7)';
        color2 = 'rgba(52, 211, 153, 0.8)';
        color3 = 'rgba(110, 231, 183, 0.6)';
      } else if (state === 'connecting') {
        // Amber & gold pulse
        color1 = 'rgba(245, 158, 11, 0.7)';
        color2 = 'rgba(251, 191, 36, 0.8)';
        color3 = 'rgba(217, 119, 6, 0.6)';
      } else {
        // Idle gentle blue & indigo
        color1 = 'rgba(59, 130, 246, 0.35)';
        color2 = 'rgba(99, 102, 241, 0.4)';
        color3 = 'rgba(147, 197, 253, 0.3)';
      }

      // Draw background ambient bloom
      const bloomGrad = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, size * 0.45);
      bloomGrad.addColorStop(0, color2);
      bloomGrad.addColorStop(0.5, color1);
      bloomGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = bloomGrad;
      ctx.beginPath();
      ctx.arc(centerX, centerY, size * 0.45, 0, Math.PI * 2);
      ctx.fill();

      // Multi-layer deformed fluid wave rings
      const ringCount = state === 'speaking' ? 4 : 3;
      const baseRadius = size * 0.28;

      for (let r = 0; r < ringCount; r++) {
        ctx.beginPath();
        const rOffset = (r * Math.PI) / ringCount;
        const currentRadius = baseRadius + (state === 'speaking' ? Math.sin(phase * 2 + r) * 12 : Math.sin(phase + r) * 4);

        for (let angle = 0; angle <= Math.PI * 2; angle += 0.08) {
          const waveFreq = state === 'speaking' ? 5 : 3;
          const waveAmp = state === 'speaking' ? 8 + r * 2 : state === 'listening' ? 5 : 2.5;
          const offset = Math.sin(angle * waveFreq + phase + rOffset) * waveAmp;
          const radius = currentRadius + offset;

          const x = centerX + Math.cos(angle) * radius;
          const y = centerY + Math.sin(angle) * radius;

          if (angle === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.closePath();
        ctx.strokeStyle = r === 0 ? color2 : r === 1 ? color1 : color3;
        ctx.lineWidth = 2.2;
        ctx.stroke();
      }

      // Center luminous core
      const coreGrad = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, baseRadius * 0.7);
      coreGrad.addColorStop(0, '#FFFFFF');
      coreGrad.addColorStop(0.4, color2);
      coreGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(centerX, centerY, baseRadius * 0.7, 0, Math.PI * 2);
      ctx.fill();

      animationFrame = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrame);
  }, [state, size]);

  return (
    <div className={`relative flex items-center justify-center select-none ${className}`}>
      <canvas
        ref={canvasRef}
        style={{ width: size, height: size }}
        className="block"
      />
    </div>
  );
}
