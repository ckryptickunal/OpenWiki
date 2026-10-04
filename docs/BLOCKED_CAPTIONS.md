# When YouTube blocks captions: proxies, Tor rotation, and local speech-to-text

A field report from a real run, plus the options OpenWiki gives you. Written while building
[ProAstro](case-studies/proastro.md), which pulls ~10,000 Hindi and English videos and shorts from four channels.

## What happens

`youtube-transcript-api` reads captions from YouTube's `timedtext` endpoint. From a laptop connection in India,
fetching shorts back to back with no pause, the IP was blocked after **46 transcripts** (`ip_blocked`,
`RequestBlocked`). Things we tried at that moment:

| Attempt | Result |
|---|---|
| Retry later, same IP | Still blocked 12 minutes later (and on later checks) |
| `yt-dlp --write-auto-subs` (same `timedtext` host) | `HTTP 429 Too Many Requests` |
| `yt-dlp --impersonate chrome` (curl-cffi) for subtitles | Still 429; impersonation doesn't help, the block is per IP |
| `yt-dlp` **audio** download (`googlevideo.com`) | **Works**, ~3 s per short, not blocked |
| `YOUTUBE_PROXY=socks5://127.0.0.1:9050` (shared local Tor) | 1 of 3 videos succeeded; depends on the exit node |

So the captions endpoint and the media endpoint are throttled separately. When captions are blocked you can
still get the audio, and a local model can turn it into a transcript.

## Option 1: wait, and pace yourself

`ip_blocked` and `rate_limited` are never permanent skips; rerun later. Use `--limit` and smaller batches.
Free, but slow when you have thousands of videos.

## Option 2: proxy, with Tor circuit rotation

```bash
pip install "openwiki-cli[tor]"
tor --SocksPort 9060 --ControlPort 9061 --CookieAuthentication 0 &
export YOUTUBE_PROXY=socks5://127.0.0.1:9060
export YOUTUBE_TOR_CONTROL_PORT=9061     # new: on a block, ask Tor for a new circuit and retry at once
openwiki youtube --urls-file urls.txt --folder Talks
```

With `YOUTUBE_TOR_CONTROL_PORT` set, a blocked or rate-limited caption request sends `SIGNAL NEWNYM` to Tor and
retries straight away on a fresh exit, instead of sleeping. Many Tor exits are themselves blocked by YouTube,
so expect a mix of successes and failures; it is a useful accelerator, not a guarantee. Only use the
control port without a password on `127.0.0.1`.

## Option 3: `--asr`, local speech-to-text (new)

```bash
pip install "openwiki-cli[asr]"     # mlx-whisper on Apple Silicon, faster-whisper elsewhere
openwiki youtube --channel @SomeChannel --lang hi,en --asr
```

When a video has no captions, or its captions are blocked or rate limited, OpenWiki downloads the smallest
audio stream with yt-dlp, transcribes it with Whisper, writes the normal `[m:ss]` transcript, and deletes
the audio. The header says `Transcript Language: speech-to-text, <backend> (<lang>)` so you can always tell
ASR text from YouTube captions.

- The first `--lang` code is passed to Whisper as the language hint (`hi` above); without `--lang`, Whisper
  auto-detects.
- `OPENWIKI_ASR_PROMPT` primes Whisper with your domain's vocabulary (it becomes Whisper's `initial_prompt`).
  On noisy shorts with background music it fixed some terms but not all; clean audio matters more.
- Model: `OPENWIKI_ASR_MODEL` (default `large-v3-turbo`, ~1.6 GB download on first use). It handles Hindi and
  Hinglish about as well as YouTube's own auto-captions: astrology terms such as "कुंडली" sometimes come out
  misheard, so downstream LLM steps should expect phonetic errors.
- Speed measured on an Apple M5 with `mlx-whisper`: a 1-minute short takes 3-8 s to transcribe once the model
  is loaded. End to end, with audio downloads overlapping, that came to roughly 10-15 shorts per minute.
- Videos with no captions at all now get transcribed too, which matters for regional-language channels where
  many uploads have no caption track.

## Which to use

| Situation | Use |
|---|---|
| A few hundred English videos | Plain captions, pace with `--limit` |
| Blocked IP, need captions specifically | Tor + `YOUTUBE_TOR_CONTROL_PORT`, or a residential proxy in `YOUTUBE_PROXY` |
| Thousands of videos, non-English, or many videos without captions | `--asr` (combine with a proxy so caption hits stay cheap) |
| Server / CI | A paid residential proxy; cloud IPs are blocked far more aggressively |

## Note on yt-dlp

Recent yt-dlp warns `No supported JavaScript runtime could be found` unless `deno` is installed. Audio
downloads for public videos still worked in our run, but installing `deno` avoids missing formats later.
