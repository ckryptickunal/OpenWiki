"""Local speech-to-text fallback for videos whose captions can't be fetched.

Used by `openwiki youtube --asr` when a video has no caption track, or when YouTube blocks or rate-limits the
captions endpoint for your IP. The audio stream is still downloadable in that case (it is served from a
different host), so OpenWiki downloads the smallest audio format with yt-dlp, transcribes it locally with
Whisper, writes the usual `[m:ss]` transcript, and deletes the audio.

Backends, first one installed wins (install with `pip install "openwiki-cli[asr]"`):
- `mlx-whisper`     Apple Silicon (fastest on M-series Macs)
- `faster-whisper`  CPU / CUDA on Linux, Windows, Intel Macs
- `whisper`         the reference openai-whisper package

`OPENWIKI_ASR_MODEL` picks the model (default: large-v3-turbo; good multilingual quality, e.g. Hindi).
`OPENWIKI_ASR_PROMPT` primes Whisper with domain vocabulary (comma-separated terms, any script), which reduces
mis-hearings of jargon and names.
"""

from __future__ import annotations

import importlib.util
import tempfile
from dataclasses import dataclass
from pathlib import Path

from openwiki.env import env_value

BACKENDS = ("mlx_whisper", "faster_whisper", "whisper")
DEFAULT_MODELS = {
    "mlx_whisper": "mlx-community/whisper-large-v3-turbo",
    "faster_whisper": "large-v3-turbo",
    "whisper": "turbo",
}
AUDIO_FORMAT = "ba[abr<=70]/worstaudio/ba"


class ASRUnavailable(RuntimeError):
    """No speech-to-text backend is installed."""


@dataclass
class Segment:
    start: float
    text: str


def available_backend() -> str | None:
    for name in BACKENDS:
        if importlib.util.find_spec(name) is not None:
            return name
    return None


def asr_language(languages: list[str] | None) -> str | None:
    """Whisper takes one language hint; use the first preferred caption language, or auto-detect."""
    for code in languages or []:
        code = code.strip().lower().split("-")[0]
        if code:
            return code
    return None


def download_audio(video_id: str, dest: Path) -> Path:
    import yt_dlp

    opts = {
        "format": AUDIO_FORMAT,
        "outtmpl": str(dest / f"{video_id}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    files = sorted(dest.glob(f"{video_id}.*"))
    if not files:
        raise RuntimeError("audio download produced no file")
    return files[0]


def transcribe_file(audio: Path, *, language: str | None = None, backend: str | None = None,
                    model: str | None = None) -> list[Segment]:
    backend = backend or available_backend()
    if backend is None:
        raise ASRUnavailable('no speech-to-text backend; pip install "openwiki-cli[asr]"')
    model = model or env_value("OPENWIKI_ASR_MODEL") or DEFAULT_MODELS[backend]
    prompt = env_value("OPENWIKI_ASR_PROMPT") or None
    if backend == "mlx_whisper":
        import mlx_whisper

        out = mlx_whisper.transcribe(str(audio), path_or_hf_repo=model, language=language,
                                     condition_on_previous_text=False, initial_prompt=prompt)
        return [Segment(s["start"], s["text"]) for s in out["segments"]]
    if backend == "faster_whisper":
        from faster_whisper import WhisperModel

        segments, _ = WhisperModel(model).transcribe(str(audio), language=language,
                                                     condition_on_previous_text=False, initial_prompt=prompt)
        return [Segment(s.start, s.text) for s in segments]
    import whisper

    out = whisper.load_model(model).transcribe(str(audio), language=language, condition_on_previous_text=False,
                                               initial_prompt=prompt)
    return [Segment(s["start"], s["text"]) for s in out["segments"]]


def transcribe_video(video_id: str, *, languages: list[str] | None = None):
    """Download audio, transcribe, clean up. Returns a youtube.FetchedTranscript."""
    from openwiki.textfmt import format_timed_transcript
    from openwiki.youtube import FetchedTranscript

    backend = available_backend()
    if backend is None:
        raise ASRUnavailable('no speech-to-text backend; pip install "openwiki-cli[asr]"')
    lang = asr_language(languages)
    with tempfile.TemporaryDirectory(prefix="openwiki-asr-") as tmp:
        audio = download_audio(video_id, Path(tmp))
        segments = transcribe_file(audio, language=lang, backend=backend)
    text = format_timed_transcript(segments)
    if not text.strip():
        raise RuntimeError("speech-to-text produced no text")
    return FetchedTranscript(
        text=text,
        language=f"speech-to-text, {backend}",
        language_code=lang or "und",
        is_generated=True,
        snippet_count=len(segments),
    )
