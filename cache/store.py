"""
Deterministic cryptographic SHA-256 caching system for DubStream v2.0.
"""
import hashlib
import json
from pathlib import Path
from audio.buffer import AudioBuffer


class PipelineCache:
    """Manages utterance synthesis and metadata caching."""

    def __init__(self, cache_dir: Path | str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).resolve().parent / "storage"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_utterance_hash(
        source_audio_hash: str,
        speaker_id: str,
        source_text: str,
        translation_text: str,
        voice_model: str,
        prosody_params: dict = None,
    ) -> str:
        """Compute SHA-256 cache key for an utterance generation step."""
        raw_key = json.dumps({
            "audio_hash": source_audio_hash,
            "speaker_id": speaker_id,
            "source_text": source_text.strip(),
            "translation_text": translation_text.strip(),
            "voice_model": voice_model,
            "prosody": prosody_params or {},
        }, sort_keys=True)
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def get_cached_audio(self, cache_key: str) -> AudioBuffer | None:
        file_path = self.cache_dir / f"{cache_key}.wav"
        if file_path.exists():
            try:
                return AudioBuffer.from_wav_bytes(file_path.read_bytes())
            except Exception:
                return None
        return None

    def put_cached_audio(self, cache_key: str, audio_buf: AudioBuffer):
        file_path = self.cache_dir / f"{cache_key}.wav"
        try:
            file_path.write_bytes(audio_buf.to_wav_bytes())
        except Exception as e:
            print(f"[Cache Storage] Warning: Could not write cache file {file_path}: {e}")
