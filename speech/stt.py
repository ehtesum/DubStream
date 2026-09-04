"""
Speech-to-Text (STT) abstraction for DubStream v2.0.

Outputs structured SpeechSegment objects containing optional word-level WordTiming alignment.
Includes fallback mechanisms when word-level timestamps are unavailable.
"""
from dataclasses import dataclass, field
import numpy as np

from audio.buffer import AudioBuffer


@dataclass
class WordTiming:
    word: str
    start: float
    end: float
    confidence: float = 1.0


@dataclass
class SpeechSegment:
    speaker_id: str
    start: float
    end: float
    text: str
    words: list[WordTiming] = field(default_factory=list)


class Transcriber:
    """STT engine wrapping Whisper with optional word-level timestamp extraction."""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._whisper_model = None

    @property
    def whisper_model(self):
        if self._whisper_model is None:
            import whisper
            self._whisper_model = whisper.load_model(self.model_name)
        return self._whisper_model

    def transcribe_buffer(
        self, audio_buf: AudioBuffer, speaker_id: str = "SPEAKER_00", language: str = None
    ) -> list[SpeechSegment]:
        """
        Transcribe AudioBuffer into list of SpeechSegment objects.
        Attempts word-level timestamp extraction (word_timestamps=True);
        falls back gracefully to segment-level timestamps if unsupported.
        """
        mono_16k = audio_buf.to_mono().resample(16000)
        samples = mono_16k.samples

        if len(samples) == 0:
            return []

        try:
            # Primary attempt: word_timestamps=True
            result = self.whisper_model.transcribe(
                samples,
                language=language if language and language != "auto" else None,
                fp16=False,
                word_timestamps=True,
            )
        except Exception:
            # Fallback: standard segment transcription without word timestamps
            result = self.whisper_model.transcribe(
                samples,
                language=language if language and language != "auto" else None,
                fp16=False,
            )

        raw_segments = result.get("segments", [])
        output_segments = []

        for seg in raw_segments:
            text = seg.get("text", "").strip()
            if not text:
                continue

            seg_start = float(seg.get("start", 0.0))
            seg_end = float(seg.get("end", audio_buf.duration))

            words_list = []
            if "words" in seg:
                for w in seg["words"]:
                    w_text = w.get("word", "").strip()
                    if w_text:
                        words_list.append(WordTiming(
                            word=w_text,
                            start=float(w.get("start", seg_start)),
                            end=float(w.get("end", seg_end)),
                            confidence=float(w.get("probability", 1.0)),
                        ))

            output_segments.append(SpeechSegment(
                speaker_id=speaker_id,
                start=seg_start,
                end=seg_end,
                text=text,
                words=words_list,
            ))

        return output_segments
