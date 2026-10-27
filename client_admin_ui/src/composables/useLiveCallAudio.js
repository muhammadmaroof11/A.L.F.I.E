import { ref, onUnmounted } from 'vue';

export function useLiveCallAudio() {
  const isListening = ref(false);
  const isMicMuted = ref(true);
  const volumeLevel = ref(0.8);
  const audioContext = ref(null);
  const audioElement = ref(null);

  function startListening(callId, livekitToken) {
    isListening.value = true;
    if (!audioElement.value) {
      audioElement.value = new Audio();
      audioElement.value.autoplay = true;
    }
    audioElement.value.volume = volumeLevel.value;
  }

  function stopListening() {
    isListening.value = false;
    if (audioElement.value) {
      audioElement.value.pause();
      audioElement.value.src = '';
    }
  }

  function toggleMuteMic() {
    isMicMuted.value = !isMicMuted.value;
  }

  function setVolume(val) {
    volumeLevel.value = Math.max(0, Math.min(1, val));
    if (audioElement.value) {
      audioElement.value.volume = volumeLevel.value;
    }
  }

  onUnmounted(() => {
    stopListening();
  });

  return {
    isListening,
    isMicMuted,
    volumeLevel,
    startListening,
    stopListening,
    toggleMuteMic,
    setVolume,
  };
}
