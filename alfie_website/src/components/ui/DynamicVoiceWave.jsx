import React, { useEffect, useRef } from 'react';

/**
 * High-Performance Dynamic Voice Waveform
 * 
 * Performance & Architecture Optimizations:
 * 1. Zero React re-renders: Replaces 192 DOM <div> nodes with a single GPU-accelerated Canvas 2D context.
 * 2. 60-120 FPS buttery smooth motion: Eliminates main-thread React reconciliation and CSS transition clashes.
 * 3. HiDPI / Retina Crisp: Automatically scales with window.devicePixelRatio (capped at 2 for GPU efficiency).
 * 4. IntersectionObserver: Automatically pauses the animation loop when scrolled out of view.
 * 5. Responsive ResizeObserver: Smoothly recalculates bar widths and coordinates on window resize.
 */
export default function DynamicVoiceWave({ className = "" }) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    let animationFrameId;
    let isVisible = true;
    let phase = 0;

    let width = 0;
    let height = 0;
    let dpr = 1;

    // Pre-create gradient caches
    let upperGradient = null;
    let lowerGradient = null;

    const updateDimensions = () => {
      if (!container || !canvas) return;
      const rect = container.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      if (width === 0 || height === 0) return;

      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);

      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      const centerY = height / 2;

      // Upper wave gradient (Electric Blue -> Cyan)
      upperGradient = ctx.createLinearGradient(0, centerY, 0, 0);
      upperGradient.addColorStop(0, '#3b82f6');
      upperGradient.addColorStop(0.55, '#22d3ee');
      upperGradient.addColorStop(1, '#67e8f9');

      // Lower reflection gradient (Blue -> Deep Indigo)
      lowerGradient = ctx.createLinearGradient(0, centerY, 0, height);
      lowerGradient.addColorStop(0, '#3b82f6');
      lowerGradient.addColorStop(0.5, '#6366f1');
      lowerGradient.addColorStop(1, 'rgba(79, 70, 229, 0.7)');
    };

    updateDimensions();

    // ResizeObserver for responsive recalculation
    const resizeObserver = new ResizeObserver(() => {
      updateDimensions();
    });
    resizeObserver.observe(container);

    // Pause animation when scrolled off-screen to preserve CPU/GPU
    const intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        isVisible = entry.isIntersecting;
        if (isVisible && !animationFrameId) {
          render();
        }
      },
      { threshold: 0.05 }
    );
    intersectionObserver.observe(container);

    const render = () => {
      if (!isVisible) {
        animationFrameId = null;
        return;
      }

      phase = (phase + 0.022) % (Math.PI * 2);
      ctx.clearRect(0, 0, width, height);

      if (width > 0 && height > 0) {
        const centerY = height / 2;
        // Edge-to-edge full screen width with zero side margins
        const gap = width < 640 ? 2.5 : width < 1024 ? 3.5 : 4;
        const targetBarWidth = width < 640 ? 3 : width < 1024 ? 4 : 5;
        const targetPitch = targetBarWidth + gap;
        const barCount = Math.max(32, Math.round((width - gap) / targetPitch));
        const barWidth = Math.max(1.5, (width - (barCount - 1) * gap) / barCount);
        const radius = Math.min(barWidth / 2, 3);
        const maxBarHalfHeight = (height / 2) - 3;

        for (let i = 0; i < barCount; i++) {
          const x = i * (barWidth + gap);
          const normalizedX = i / barCount;

          // Harmonic wave equation
          const primaryWave = Math.sin(normalizedX * Math.PI * 4.5 + phase);
          const harmonicWave = Math.sin(normalizedX * Math.PI * 2.2 - phase * 0.4) * 0.35;
          const combined = (primaryWave + harmonicWave + 1.35) / 2.7;

          // Upper bar height & opacity
          const upperHeight = Math.max(4, Math.min(maxBarHalfHeight, combined * maxBarHalfHeight));
          const waveOpacity = Math.max(0.45, Math.min(0.95, 0.75 + Math.sin(normalizedX * Math.PI + phase) * 0.2));

          // Draw Upper Bar (growing upwards from centerY)
          ctx.save();
          ctx.globalAlpha = waveOpacity;
          ctx.fillStyle = upperGradient || '#008BC5';
          ctx.beginPath();
          if (typeof ctx.roundRect === 'function') {
            ctx.roundRect(x, centerY - upperHeight, barWidth, upperHeight, [radius, radius, 0, 0]);
          } else {
            ctx.rect(x, centerY - upperHeight, barWidth, upperHeight);
          }
          ctx.fill();

          // Draw Lower Inverted Bar (reflection growing downwards from centerY)
          const lowerHeight = Math.max(3, upperHeight * 0.72);
          ctx.globalAlpha = waveOpacity * 0.8;
          ctx.fillStyle = lowerGradient || '#4338ca';
          ctx.beginPath();
          if (typeof ctx.roundRect === 'function') {
            ctx.roundRect(x, centerY, barWidth, lowerHeight, [0, 0, radius, radius]);
          } else {
            ctx.rect(x, centerY, barWidth, lowerHeight);
          }
          ctx.fill();
          ctx.restore();
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      intersectionObserver.disconnect();
    };
  }, []);

  return (
    <div ref={containerRef} className={`relative w-full overflow-hidden pointer-events-none ${className}`}>
      <canvas ref={canvasRef} className="block w-full h-full" />
    </div>
  );
}
