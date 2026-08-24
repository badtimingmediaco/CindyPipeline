#!/usr/bin/env python3
"""Download the Whisper model at SETUP time, not mid-build.

faster-whisper does not bundle its weights - it fetches them from Hugging Face the first
time you transcribe. Left alone, that means an editor's first real build stalls partway
through Stage 1 on a several-hundred-megabyte download, and on a blocked or throttled
network it fails there, after the build has already started. Doing it here moves the wait
to a moment where waiting is expected, and turns a mid-build failure into a setup warning.

  python warm_models.py                 # default model
  python warm_models.py --model medium  # more accurate, ~1.5GB
  python warm_models.py --check         # report only, download nothing

THE MODEL IS PART OF THE SPEC, not a free choice: four editors on four different models
produce four different transcripts, and every sticker's text and timing is anchored to
that transcript. Change it here and in reference/05-pipeline.md together, or not at all.
"""
import argparse
import os
import sys
import time

# English-only, ~500MB. Her audio is clean studio VO, where small.en's word timestamps
# are reliable, and it is a far kinder download for four editors than medium's ~1.5GB.
# Bump to "medium" if transcript accuracy ever proves to be the limiting factor.
DEFAULT_MODEL = "small.en"


def cache_dir():
    return (os.environ.get("HF_HOME")
            or os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))


def cached_models():
    hub = os.path.join(cache_dir(), "hub")
    try:
        return sorted(d.replace("models--Systran--faster-whisper-", "")
                      for d in os.listdir(hub) if "faster-whisper" in d)
    except OSError:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    have = cached_models()
    print(f"  cache: {cache_dir()}")
    print(f"  models already present: {', '.join(have) if have else '(none)'}")

    if a.model in have:
        print(f"  [ok] {a.model} is cached - no download needed")
        return 0
    if a.check:
        print(f"  [warn] {a.model} is NOT cached; the first build would download it")
        return 1

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  [FAIL] faster-whisper is not installed - pip install faster-whisper")
        return 2

    print(f"  downloading {a.model} ... (a few hundred MB, one time)")
    print("  This can take several minutes with no visible output. That is normal.")
    print("  RUN THIS FROM A TERMINAL, not from inside an agent tool call - the download")
    print("  outlives most tool timeouts, and a timeout there looks like a network failure.")
    print("  Interrupted downloads resume, so re-running after a drop is safe.")
    t = time.time()
    try:
        WhisperModel(a.model, device="cpu", compute_type="int8")
    except Exception as e:
        print(f"  [FAIL] could not download: {type(e).__name__}: {e}")
        print("  If this is a connection error, check whether huggingface.co is reachable")
        print("  and whether a VPN or proxy is interfering. Setup is otherwise fine; the")
        print("  model can be fetched later by re-running this script.")
        return 3
    print(f"  [ok] {a.model} ready ({time.time() - t:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
