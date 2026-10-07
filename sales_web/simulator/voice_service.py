"""
Voice Service — Whisper STT + Kokoro TTS

Runs 100% locally, free of cost.

Whisper   : faster-whisper (CTranslate2 backend)
Kokoro    : kokoro (local neural TTS)

Both models are loaded lazily on first use
and cached for subsequent requests.
"""

import io
import os
import tempfile
import traceback
import wave
import struct

# Will be imported lazily
_whisper_model = None
_kokoro_pipeline = None
_kokoro_available = False
_whisper_available = False


# ============================================================
# WHISPER STT
# ============================================================

def _load_whisper():
    """
    Load faster-whisper model.
    Falls back to base model if tiny is unavailable.
    """

    global _whisper_model
    global _whisper_available

    if _whisper_model is not None:
        return _whisper_model

    try:

        from faster_whisper import (
            WhisperModel,
        )

        # Use "base" for balance of
        # speed vs accuracy on CPU.
        # Use "tiny" if you need faster.

        model_size = os.environ.get(
            "WHISPER_MODEL",
            "base",
        )

        print(
            f"[VOICE] Loading Whisper "
            f"model: {model_size}"
        )

        _whisper_model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

        _whisper_available = True

        print(
            "[VOICE] Whisper model loaded."
        )

        return _whisper_model

    except ImportError:

        print(
            "[VOICE] faster-whisper not "
            "installed. Run:\n"
            "  pip install faster-whisper"
        )

        _whisper_available = False

        return None

    except Exception as e:

        print(
            f"[VOICE] Whisper load error: {e}"
        )

        traceback.print_exc()

        _whisper_available = False

        return None


def transcribe_audio(audio_bytes):
    """
    Transcribe audio bytes to text.

    Accepts WebM/Opus audio from the browser.
    Returns dict with 'text' and 'language'.
    """

    model = _load_whisper()

    if model is None:

        raise RuntimeError(
            "Whisper model is not available. "
            "Install faster-whisper."
        )

    # Save to temporary file
    # (faster-whisper needs file path)

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False,
    ) as tmp:

        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:

        segments, info = model.transcribe(
            tmp_path,
            beam_size=5,
            language="en",
            vad_filter=True,
        )

        text = ""

        for segment in segments:
            text += segment.text

        return {
            "text": text.strip(),
            "language": info.language,
        }

    finally:

        os.unlink(tmp_path)


# ============================================================
# KOKORO TTS
# ============================================================

def _load_kokoro():
    """
    Load Kokoro TTS pipeline.
    """

    global _kokoro_pipeline
    global _kokoro_available

    if _kokoro_pipeline is not None:
        return _kokoro_pipeline

    try:

        from kokoro import KPipeline

        print(
            "[VOICE] Loading Kokoro TTS..."
        )

        # American English voice
        _kokoro_pipeline = KPipeline(
            lang_code="a",
        )

        _kokoro_available = True

        print(
            "[VOICE] Kokoro TTS loaded."
        )

        return _kokoro_pipeline

    except ImportError:

        print(
            "[VOICE] kokoro not installed. "
            "Run:\n"
            "  pip install kokoro soundfile"
        )

        _kokoro_available = False

        return None

    except Exception as e:

        print(
            f"[VOICE] Kokoro load error: {e}"
        )

        traceback.print_exc()

        _kokoro_available = False

        return None


def synthesize_speech(text):
    """
    Synthesize text to WAV audio bytes.

    Returns bytes of a WAV file.
    """

    pipeline = _load_kokoro()

    if pipeline is None:

        raise RuntimeError(
            "Kokoro TTS is not available. "
            "Install kokoro."
        )

    try:

        # Generate audio
        # voice = af_heart is a natural female voice
        # You can change to other voices

        voice = os.environ.get(
            "KOKORO_VOICE",
            "am_adam",
        )

        samples = None
        sample_rate = 24000

        for result in pipeline(
            text,
            voice=voice,
            speed=1.0,
        ):

            if samples is None:
                samples = result.audio
            else:
                import numpy as np
                samples = np.concatenate(
                    [samples, result.audio]
                )

        if samples is None:

            raise RuntimeError(
                "Kokoro produced no audio."
            )

        # Convert numpy float32 array to
        # WAV bytes

        buf = io.BytesIO()

        import soundfile as sf

        sf.write(
            buf,
            samples,
            sample_rate,
            format="WAV",
        )

        buf.seek(0)

        return buf.read()

    except Exception as e:

        print(
            f"[VOICE] TTS synthesis error: {e}"
        )

        traceback.print_exc()

        raise


# ============================================================
# STATUS
# ============================================================

def get_model_status():
    """
    Return current model availability.
    """

    return {
        "stt_ready": _whisper_available,
        "tts_ready": _kokoro_available,
        "stt_model": os.environ.get(
            "WHISPER_MODEL",
            "base",
        ),
        "tts_model": "kokoro",
    }


def load_all_models():
    """
    Pre-load both models.
    Returns status dict.
    """

    _load_whisper()
    _load_kokoro()

    return get_model_status()
