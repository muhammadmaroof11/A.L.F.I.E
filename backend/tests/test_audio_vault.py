"""
Unit and integration tests for A.L.F.I.E Phase 2:
Cloud Audio Vault, SigV4 Presigned URLs, and Asynchronous PCM Waveform Processing.
"""

import io
import math
import os
import pathlib
import struct
import tempfile
import unittest
import urllib.parse
import wave
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure test credentials exist before importing settings
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from audio_vault import (
    AudioVaultClient,
    extract_dual_track_waveform,
    extract_pcm_waveform_peaks,
)


def _generate_synthetic_wav(
    duration_sec: float = 2.0,
    sample_rate: int = 16000,
    num_channels: int = 1,
    frequency: float = 440.0,
) -> bytes:
    """Generates a valid in-memory PCM 16-bit WAV file with tone bursts."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_out:
        wav_out.setnchannels(num_channels)
        wav_out.setsampwidth(2)  # 16-bit
        wav_out.setframerate(sample_rate)

        total_frames = int(sample_rate * duration_sec)
        frames = []
        for i in range(total_frames):
            t = float(i) / sample_rate
            # Active speech burst in first 60% of duration, silence in remaining 40%
            if t < duration_sec * 0.6:
                val = int(20000.0 * math.sin(2.0 * math.pi * frequency * t))
            else:
                val = 0

            if num_channels == 1:
                frames.append(struct.pack("<h", val))
            else:
                # Channel 0 (Caller) speaks in first 30%, Channel 1 (Agent) in 30%-60%
                val_caller = val if t < duration_sec * 0.3 else 0
                val_agent = val if (duration_sec * 0.3 <= t < duration_sec * 0.6) else 0
                frames.append(struct.pack("<hh", val_caller, val_agent))

        wav_out.writeframes(b"".join(frames))
    return buf.getvalue()


class TestAudioVaultWaveform(unittest.TestCase):
    """Verifies exact RMS amplitude envelope extraction across mono and stereo WAV audio."""

    def test_mono_wav_rms_extraction(self):
        wav_bytes = _generate_synthetic_wav(duration_sec=2.0, num_channels=1)
        peaks = extract_pcm_waveform_peaks(wav_bytes, points=100)

        self.assertEqual(len(peaks), 100)
        # All values should be normalized floats in [0.05, 0.95]
        for p in peaks:
            self.assertGreaterEqual(p, 0.05)
            self.assertLessEqual(p, 0.95)

        # Tone burst in first 60 bars should have significantly higher average than silence in last 40 bars
        active_avg = sum(peaks[:50]) / 50.0
        silent_avg = sum(peaks[70:]) / 30.0
        self.assertGreater(active_avg, silent_avg * 2.0)

    def test_stereo_dual_track_extraction(self):
        stereo_bytes = _generate_synthetic_wav(duration_sec=2.0, num_channels=2)
        dual = extract_dual_track_waveform(stereo_bytes, points=100)

        self.assertIn("master", dual)
        self.assertIn("caller", dual)
        self.assertIn("agent", dual)

        self.assertEqual(len(dual["master"]), 100)
        self.assertEqual(len(dual["caller"]), 100)
        self.assertEqual(len(dual["agent"]), 100)

        # Caller spoke in 0%-30% (first 30 bars)
        caller_active_avg = sum(dual["caller"][:25]) / 25.0
        caller_silent_avg = sum(dual["caller"][40:70]) / 30.0
        self.assertGreater(caller_active_avg, caller_silent_avg * 1.5)

        # Agent spoke in 30%-60% (bars 30-60)
        agent_active_avg = sum(dual["agent"][35:55]) / 20.0
        agent_silent_avg = sum(dual["agent"][:25]) / 25.0
        self.assertGreater(agent_active_avg, agent_silent_avg * 1.5)

    def test_silent_audio_handling(self):
        # 1-second pure zero-value audio
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(16000)
            wav_out.writeframes(b"\x00\x00" * 16000)
        silent_bytes = buf.getvalue()

        peaks = extract_pcm_waveform_peaks(silent_bytes, points=100)
        self.assertEqual(len(peaks), 100)
        self.assertTrue(all(p == 0.05 for p in peaks))

    def test_corrupt_and_empty_bytes_fallback(self):
        peaks_empty = extract_pcm_waveform_peaks(b"", points=100)
        self.assertEqual(len(peaks_empty), 100)
        for p in peaks_empty:
            self.assertGreaterEqual(p, 0.05)
            self.assertLessEqual(p, 0.95)

        peaks_corrupt = extract_pcm_waveform_peaks(b"NOT_A_WAV_FILE_CORRUPT_BYTES", points=100)
        self.assertEqual(len(peaks_corrupt), 100)


class TestAudioVaultSigV4Presigning(unittest.TestCase):
    """Verifies pure-Python AWS SigV4 presigned URL generation for Cloudflare R2 and AWS S3."""

    def setUp(self):
        self.vault = AudioVaultClient(
            endpoint_url="https://cf123456789.r2.cloudflarestorage.com",
            access_key_id="test_access_key_id_123",
            secret_access_key="test_secret_access_key_456",
            bucket_name="alfie-recordings",
            region="auto",
        )

    def test_cloud_enabled_flag(self):
        self.assertTrue(self.vault.is_cloud_enabled())

        disabled_vault = AudioVaultClient(access_key_id="", secret_access_key="")
        self.assertFalse(disabled_vault.is_cloud_enabled())

    def test_sigv4_presigned_get_url(self):
        url = self.vault.generate_s3_presigned_url(
            object_key="recordings/tenant_xyz/call_999.wav",
            method="GET",
            expires_in=3600,
        )

        parsed = urllib.parse.urlparse(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "cf123456789.r2.cloudflarestorage.com")
        self.assertTrue(parsed.path.endswith("recordings/tenant_xyz/call_999.wav"))

        qs = urllib.parse.parse_qs(parsed.query)
        self.assertIn("X-Amz-Algorithm", qs)
        self.assertEqual(qs["X-Amz-Algorithm"][0], "AWS4-HMAC-SHA256")
        self.assertIn("X-Amz-Credential", qs)
        self.assertTrue(qs["X-Amz-Credential"][0].startswith("test_access_key_id_123/"))
        self.assertIn("X-Amz-Signature", qs)
        self.assertEqual(len(qs["X-Amz-Signature"][0]), 64)  # SHA256 hex string

    def test_sigv4_presigned_put_url(self):
        url = self.vault.generate_s3_presigned_url(
            object_key="recordings/tenant_xyz/call_999.wav",
            method="PUT",
            expires_in=600,
        )
        self.assertIn("X-Amz-Signature", url)
        self.assertIn("X-Amz-Expires=600", url)

    def test_local_fallback_url_when_cloud_disabled(self):
        local_vault = AudioVaultClient(access_key_id="", secret_access_key="")
        url = local_vault.generate_presigned_audio_url(call_id="call-abc-123", tenant_id="tenant-456")
        self.assertEqual(url, "/api/client/recordings/call-abc-123/audio")


class TestAudioVaultStorageOperations(unittest.IsolatedAsyncioTestCase):
    """Verifies local disk persistence, byte retrieval, and async upload operations."""

    async def test_local_disk_upload_and_retrieval(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            vault = AudioVaultClient(
                access_key_id="",
                secret_access_key="",
                local_dir=tmp_dir,
            )

            test_bytes = b"RIFF" + b"\x00" * 40 + b"WAVEfmt "
            call_id = "test-call-id-local-001"
            tenant_id = "tenant-test-777"

            saved_path = await vault.upload_recording(
                call_id=call_id,
                tenant_id=tenant_id,
                audio_bytes=test_bytes,
                extension="wav",
            )

            self.assertTrue(os.path.exists(saved_path))

            # Retrieve bytes
            read_bytes, ctype = vault.get_recording_bytes(call_id, tenant_id)
            self.assertEqual(read_bytes, test_bytes)
            self.assertEqual(ctype, "audio/wav")


if __name__ == "__main__":
    unittest.main()
