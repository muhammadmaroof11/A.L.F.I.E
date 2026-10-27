import { ref } from 'vue';
import { api } from '../services/api';

export function useSupervisorControl() {
  const isWhispering = ref(false);
  const isTakingOver = ref(false);
  const isSendingDTMF = ref(false);
  const isSendingSMS = ref(false);
  const lastActionStatus = ref(null);

  async function sendGhostWhisper(callId, prompt) {
    if (!callId || !prompt) return false;
    isWhispering.value = true;
    try {
      await api.post(`/api/client/calls/${callId}/whisper`, { prompt });
      lastActionStatus.value = { success: true, message: 'Whisper directive dispatched' };
      return true;
    } catch (err) {
      console.error('Ghost whisper dispatch error:', err);
      lastActionStatus.value = { success: false, message: 'Failed to dispatch whisper' };
      return false;
    } finally {
      isWhispering.value = false;
    }
  }

  async function takeOverCall(callId, supervisorName = 'Supervisor') {
    if (!callId) return false;
    isTakingOver.value = true;
    try {
      await api.post(`/api/client/calls/${callId}/takeover`, { supervisor_name: supervisorName });
      lastActionStatus.value = { success: true, message: 'Call takeover active' };
      return true;
    } catch (err) {
      console.error('Takeover dispatch error:', err);
      lastActionStatus.value = { success: false, message: 'Failed to initiate takeover' };
      return false;
    } finally {
      isTakingOver.value = false;
    }
  }

  async function releaseTakeover(callId) {
    if (!callId) return false;
    try {
      await api.post(`/api/client/calls/${callId}/release-takeover`, {});
      lastActionStatus.value = { success: true, message: 'Takeover released back to AI agent' };
      return true;
    } catch (err) {
      console.error('Release takeover error:', err);
      return false;
    }
  }

  async function sendDTMFTones(callId, digits, reason = 'Supervisor Keypad') {
    if (!callId || !digits) return false;
    isSendingDTMF.value = true;
    try {
      await api.post(`/api/client/calls/${callId}/dtmf`, { digits, reason });
      lastActionStatus.value = { success: true, message: `Transmitted DTMF: ${digits}` };
      return true;
    } catch (err) {
      console.error('DTMF transmission error:', err);
      lastActionStatus.value = { success: false, message: 'Failed to transmit DTMF' };
      return false;
    } finally {
      isSendingDTMF.value = false;
    }
  }

  async function sendInstantSMS(callId, toPhone, message) {
    if (!toPhone || !message) return false;
    isSendingSMS.value = true;
    try {
      await api.post('/api/client/sms/send', {
        to_phone: toPhone,
        message: message,
        call_id: callId,
      });
      lastActionStatus.value = { success: true, message: `SMS sent to ${toPhone}` };
      return true;
    } catch (err) {
      console.error('Instant SMS dispatch error:', err);
      lastActionStatus.value = { success: false, message: 'Failed to dispatch SMS' };
      return false;
    } finally {
      isSendingSMS.value = false;
    }
  }

  return {
    isWhispering,
    isTakingOver,
    isSendingDTMF,
    isSendingSMS,
    lastActionStatus,
    sendGhostWhisper,
    takeOverCall,
    releaseTakeover,
    sendDTMFTones,
    sendInstantSMS,
  };
}
