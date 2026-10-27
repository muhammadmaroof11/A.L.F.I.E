import { ref, onMounted, onUnmounted } from 'vue';

export function useWaveform(canvasRef, speakerStateRef) {
  let animId = null;
  const isAnimating = ref(false);

  function startAnimation() {
    isAnimating.value = true;
    const canvas = canvasRef.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const bars = 24;

    function draw() {
      if (!canvas || !ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const isActive = speakerStateRef && speakerStateRef.value && speakerStateRef.value !== 'idle';
      const isCaller = speakerStateRef && speakerStateRef.value === 'caller_speaking';
      const isAgent = speakerStateRef && speakerStateRef.value === 'agent_speaking';

      const barWidth = canvas.width / bars - 2;
      for (let i = 0; i < bars; i++) {
        let height = 4;
        if (isActive) {
          const wave = Math.sin(Date.now() / 150 + i * 0.4);
          height = Math.max(4, Math.abs(wave) * (canvas.height * 0.8));
        }

        const x = i * (barWidth + 2);
        const y = (canvas.height - height) / 2;

        if (isCaller) {
          ctx.fillStyle = '#38bdf8'; // Sky blue
        } else if (isAgent) {
          ctx.fillStyle = '#34d399'; // Emerald
        } else {
          ctx.fillStyle = '#52525b'; // Zinc neutral
        }

        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, height, 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(draw);
    }

    draw();
  }

  function stopAnimation() {
    isAnimating.value = false;
    if (animId) {
      cancelAnimationFrame(animId);
      animId = null;
    }
  }

  onMounted(() => {
    startAnimation();
  });

  onUnmounted(() => {
    stopAnimation();
  });

  return {
    isAnimating,
    startAnimation,
    stopAnimation,
  };
}
