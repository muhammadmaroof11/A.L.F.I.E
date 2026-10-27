<template>
  <div class="glass-panel p-4 rounded-xl border border-border/60 shadow-lg relative overflow-hidden group">
    <!-- Ambient glowing background on play -->
    <div 
      class="absolute inset-0 bg-gradient-to-r from-primary/10 via-accent/5 to-transparent transition-opacity duration-700 pointer-events-none"
      :class="isPlaying ? 'opacity-100' : 'opacity-0'"
    ></div>

    <audio 
      ref="audioEl"
      :src="audioUrl"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      @error="onAudioError"
      class="hidden"
    ></audio>

    <div class="relative flex flex-col gap-3">
      <!-- Waveform Canvas & Scrubber Area -->
      <div 
        class="relative h-16 w-full cursor-pointer select-none flex items-center bg-background/50 rounded-lg px-2 border border-border/40 hover:border-primary/40 transition-colors"
        ref="waveformContainer"
        @mousemove="onWaveformHover"
        @mouseleave="hoverProgress = null"
        @click="onWaveformClick"
      >
        <!-- Hover Scrubber Tooltip -->
        <div 
          v-if="hoverProgress !== null"
          class="absolute -top-7 px-2 py-0.5 rounded bg-popover text-popover-foreground text-[10px] font-mono shadow-md border border-border/60 pointer-events-none transform -translate-x-1/2 z-10"
          :style="{ left: `${hoverProgress * 100}%` }"
        >
          {{ formatTime(hoverProgress * durationSec) }}
        </div>

        <!-- Waveform Bars -->
        <div class="flex items-center justify-between w-full h-12 gap-[2px]">
          <div 
            v-for="(peak, idx) in normalizedPeaks" 
            :key="idx"
            class="flex-1 rounded-full transition-colors duration-150"
            :style="{ height: `${Math.max(12, peak * 100)}%` }"
            :class="idx / normalizedPeaks.length <= currentProgress 
              ? 'bg-primary shadow-[0_0_8px_hsl(var(--primary)/0.6)]' 
              : hoverProgress !== null && idx / normalizedPeaks.length <= hoverProgress
                ? 'bg-primary/40'
                : 'bg-muted-foreground/25 hover:bg-muted-foreground/40'"
          ></div>
        </div>

        <!-- Playhead Line -->
        <div 
          class="absolute top-0 bottom-0 w-[2px] bg-primary pointer-events-none shadow-[0_0_10px_hsl(var(--primary))] transition-all duration-75"
          :style="{ left: `${currentProgress * 100}%` }"
        >
          <div class="w-2.5 h-2.5 rounded-full bg-primary -ml-1 -top-1 shadow-[0_0_8px_hsl(var(--primary))]"></div>
        </div>
      </div>

      <!-- Controls & Metadata Strip -->
      <div class="flex items-center justify-between gap-3 text-xs">
        <!-- Left: Play/Pause, Times, and Live status -->
        <div class="flex items-center gap-3">
          <button 
            @click="togglePlay"
            :title="isPlaying ? 'Pause (Space)' : 'Play (Space)'"
            class="w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 shadow-sm cursor-pointer"
            :class="isPlaying ? 'bg-primary text-primary-foreground shadow-[0_0_12px_hsl(var(--primary)/0.4)] scale-105' : 'bg-primary/15 text-primary hover:bg-primary/25'"
          >
            <svg v-if="isPlaying" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" rx="1"></rect>
              <rect x="14" y="4" width="4" height="16" rx="1"></rect>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="translate-x-0.5">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </button>

          <!-- Time Display -->
          <div class="font-mono text-xs flex items-center gap-1.5 text-foreground">
            <span class="font-semibold">{{ formatTime(currentTimeSec) }}</span>
            <span class="text-muted-foreground/60">/</span>
            <span class="text-muted-foreground">{{ formatTime(durationSec) }}</span>
          </div>
        </div>

        <!-- Right: Speed, Volume, Download -->
        <div class="flex items-center gap-2">
          <!-- Playback Speed Toggle Pill -->
          <button 
            @click="cycleSpeed"
            title="Cycle Playback Speed"
            class="px-2 py-1 rounded-md text-[11px] font-mono font-semibold bg-background/80 hover:bg-muted border border-border/60 text-foreground transition-all cursor-pointer"
          >
            {{ playbackRate }}x
          </button>

          <!-- Mute / Volume -->
          <button 
            @click="toggleMute"
            title="Toggle Mute"
            class="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            <svg v-if="isMuted || volume === 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="1" y1="1" x2="23" y2="23"></line>
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
            </svg>
          </button>

          <!-- Download Audio File -->
          <a 
            :href="audioUrl" 
            download 
            title="Download Recording"
            class="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  audioUrl: {
    type: String,
    required: true
  },
  waveformData: {
    type: Array,
    default: () => []
  },
  duration: {
    type: [Number, String],
    default: 0
  },
  autoplay: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['timeupdate', 'seek', 'play', 'pause']);

const audioEl = ref(null);
const waveformContainer = ref(null);
const isPlaying = ref(false);
const currentTimeSec = ref(0);
const durationSec = ref(typeof props.duration === 'number' && props.duration > 0 ? props.duration : 60);
const hoverProgress = ref(null);
const playbackRate = ref(1.0);
const volume = ref(1.0);
const isMuted = ref(false);

// Normalize peaks to 100 points
const normalizedPeaks = computed(() => {
  if (Array.isArray(props.waveformData) && props.waveformData.length >= 20) {
    return props.waveformData;
  }
  // Fallback synthetic 100-bar waveform
  const fallback = [];
  let cadence = 0.0;
  for (let i = 0; i < 100; i++) {
    cadence += 0.18;
    const base = 0.35 + 0.3 * Math.sin(cadence);
    const jitter = ((i * 17) % 29) / 100 - 0.14;
    if (i % 14 in [0, 1] || i % 23 in [0, 1]) {
      fallback.push(0.06);
    } else {
      fallback.push(Math.max(0.08, Math.min(0.95, base + jitter)));
    }
  }
  return fallback;
});

const currentProgress = computed(() => {
  if (!durationSec.value || durationSec.value <= 0) return 0;
  return Math.min(1, Math.max(0, currentTimeSec.value / durationSec.value));
});

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
};

const togglePlay = () => {
  if (!audioEl.value) return;
  if (isPlaying.value) {
    audioEl.value.pause();
  } else {
    audioEl.value.play().catch(() => {
      // Autoplay or decode blocked
      isPlaying.value = false;
    });
  }
};

const onTimeUpdate = () => {
  if (!audioEl.value) return;
  currentTimeSec.value = audioEl.value.currentTime;
  const currentMs = Math.floor(currentTimeSec.value * 1000);
  emit('timeupdate', currentTimeSec.value, currentMs);
};

const onLoadedMetadata = () => {
  if (!audioEl.value) return;
  if (audioEl.value.duration && !isNaN(audioEl.value.duration) && audioEl.value.duration !== Infinity) {
    durationSec.value = audioEl.value.duration;
  }
  if (props.autoplay) {
    togglePlay();
  }
};

const onEnded = () => {
  isPlaying.value = false;
  currentTimeSec.value = 0;
  if (audioEl.value) {
    audioEl.value.currentTime = 0;
  }
};

const onAudioError = () => {
  isPlaying.value = false;
};

const onWaveformHover = (e) => {
  if (!waveformContainer.value) return;
  const rect = waveformContainer.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  hoverProgress.value = Math.max(0, Math.min(1, x / rect.width));
};

const onWaveformClick = (e) => {
  if (!waveformContainer.value || !audioEl.value) return;
  const rect = waveformContainer.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const progress = Math.max(0, Math.min(1, x / rect.width));
  const targetTime = progress * durationSec.value;
  seekToTime(targetTime);
};

const seekToTime = (targetSec) => {
  if (!audioEl.value) return;
  audioEl.value.currentTime = targetSec;
  currentTimeSec.value = targetSec;
  emit('seek', targetSec);
};

// Method exposed to parent for synchronized transcript turn jumping
const seekToMs = (targetMs) => {
  seekToTime(targetMs / 1000);
  if (!isPlaying.value && audioEl.value) {
    audioEl.value.play().catch(() => {});
  }
};

const cycleSpeed = () => {
  if (playbackRate.value === 1.0) playbackRate.value = 1.25;
  else if (playbackRate.value === 1.25) playbackRate.value = 1.5;
  else if (playbackRate.value === 1.5) playbackRate.value = 2.0;
  else playbackRate.value = 1.0;

  if (audioEl.value) {
    audioEl.value.playbackRate = playbackRate.value;
  }
};

const toggleMute = () => {
  if (!audioEl.value) return;
  isMuted.value = !isMuted.value;
  audioEl.value.muted = isMuted.value;
};

// Global spacebar listener for play/pause when audio player is active
const handleKeydown = (e) => {
  if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    if (waveformContainer.value && waveformContainer.value.contains(document.activeElement)) {
      e.preventDefault();
      togglePlay();
    }
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  if (props.duration && typeof props.duration === 'number' && props.duration > 0) {
    durationSec.value = props.duration;
  }
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  if (audioEl.value) {
    audioEl.value.pause();
  }
});

defineExpose({
  seekToMs,
  seekToTime,
  togglePlay,
  isPlaying
});
</script>
