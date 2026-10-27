import React, { useEffect, useRef } from 'react';

/**
 * Minimal & Calm Ambient Wave Canvas
 * Renders an ultra-subtle, serene soundwave ripple on clean white
 * giving a tactile organic feel without any harsh sci-fi/neon aesthetics.
 */
export default function InteractiveSoundwaveGrid({ className = "" }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.parentElement.offsetWidth);
    let height = (canvas.height = canvas.parentElement.offsetHeight);

    const mouse = {
      x: width * 0.5,
      y: height * 0.35,
      targetX: width * 0.5,
      targetY: height * 0.35,
      radius: 180,
      active: false
    };

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
    };

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.targetX = e.clientX - rect.left;
      mouse.targetY = e.clientY - rect.top;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.targetX = width * 0.5;
      mouse.targetY = height * 0.35;
      mouse.active = false;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    let time = 0;

    const render = () => {
      time += 0.008;

      // Smooth mouse interpolation
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      ctx.clearRect(0, 0, width, height);

      // Subtle, calm horizontal waves in soft slate
      const waveCount = 3;
      const waveStep = height / (waveCount + 2);

      for (let w = 0; w < waveCount; w++) {
        const baseY = waveStep * (w + 1.2);
        const waveSpeed = 0.01 + w * 0.004;
        const baseAmplitude = 10 + w * 5;
        const waveColor = w === 0 
          ? 'rgba(15, 23, 42, 0.04)' 
          : w === 1 
          ? 'rgba(15, 23, 42, 0.03)' 
          : 'rgba(15, 23, 42, 0.02)';

        ctx.beginPath();

        const xStep = 16;
        let started = false;

        for (let x = 0; x <= width + xStep; x += xStep) {
          const dx = x - mouse.x;
          const dy = baseY - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          const mouseInfluence = Math.max(0, 1 - dist / mouse.radius);
          const mouseOffset = Math.sin(dist * 0.04 - time * 2) * mouseInfluence * 14;

          const harmonic1 = Math.sin(x * 0.002 + time * waveSpeed + w) * baseAmplitude;
          const harmonic2 = Math.cos(x * 0.005 - time * 0.5) * (baseAmplitude * 0.35);

          const y = baseY + harmonic1 + harmonic2 + mouseOffset;

          if (!started) {
            ctx.moveTo(x, y);
            started = true;
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.strokeStyle = waveColor;
        ctx.lineWidth = 1.0;
        ctx.stroke();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className={`absolute inset-0 pointer-events-none z-0 overflow-hidden ${className}`}>
      <canvas ref={canvasRef} className="w-full h-full block opacity-60" />
    </div>
  );
}
