#!/usr/bin/env python3
"""Render a small original sound and observe playback with the macOS audio consumer."""

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time
import wave


ROOT = Path(__file__).resolve().parent


def pin(path):
    data = path.read_bytes()
    return {"path": path.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def render(score, destination):
    rate = score["sample_rate"]
    duration = max(event["offset_ms"] + event["length_ms"] for event in score["events"]) + score["tail_ms"]
    samples = [0.0] * (rate * duration // 1000)
    for event in score["events"]:
        start = rate * event["offset_ms"] // 1000
        frames = rate * event["length_ms"] // 1000
        for index in range(frames):
            seconds = index / rate
            envelope = min(1, index / (rate * 0.01), (frames - index - 1) / (rate * 0.06))
            tone = math.sin(2 * math.pi * event["frequency_hz"] * seconds)
            samples[start + index] += tone * envelope * event["gain"]
    if max(abs(sample) for sample in samples) >= 1:
        raise ValueError("Score clips during export")
    pcm = array("h", (round(sample * 32767) for sample in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(destination), "wb") as stream:
        stream.setparams((1, 2, rate, len(samples), "NONE", "PCM"))
        stream.writeframes(pcm.tobytes())


def play(file):
    started = time.monotonic()
    run = subprocess.run(["/usr/bin/afplay", "-v", "0", str(file)], capture_output=True,
                         text=True, check=False, timeout=20)
    return {"exit_code": run.returncode, "elapsed_seconds": round(time.monotonic() - started, 3),
            "stderr": run.stderr.strip()}


def check(output):
    import platform

    output.mkdir(parents=True, exist_ok=False)
    master_file = ROOT / "master.json"
    score = json.loads(master_file.read_text(encoding="utf-8"))
    audio_file = output / "cue.wav"
    render(score, audio_file)
    with wave.open(str(audio_file), "rb") as stream:
        assert stream.getparams()[:3] == (1, 2, score["sample_rate"]), "Expected mono 16-bit PCM"
        frames = stream.getnframes()
        duration = frames / stream.getframerate()
        samples = array("h", stream.readframes(frames))
    if sys.byteorder != "little":
        samples.byteswap()
    expected_peak = max(abs(sample) for sample in samples)
    assert 1000 < expected_peak < 30000 and statistics.pstdev(samples) > 500, "Signal absent or clipped"
    assert len(set(samples[-1000:])) == 1 and samples[-1] == 0, "Expected silent tail"
    assert audio_file.stat().st_size < 100 * 1024, "Audio exceeds byte budget"
    playback = play(audio_file)
    assert playback["exit_code"] == 0 and playback["elapsed_seconds"] >= duration * 0.8, playback
    invalid = output / "truncated.wav"
    invalid.write_bytes(audio_file.read_bytes()[:15])
    bad_playback = play(invalid)
    assert bad_playback["exit_code"] != 0, "Truncated export was not rejected by the player"
    receipt = {"method": "playback", "environment": f"macOS {platform.mac_ver()[0]} {platform.machine()} / afplay",
               "scope": "Native player at zero volume. No audible assessment or mobile-device claim.",
               "authoring": [pin(master_file), pin(ROOT / "RIGHTS.md"), pin(Path(__file__))],
               "artifact": pin(audio_file), "duration_seconds": duration, "frames": frames, "peak": expected_peak,
               "positive": playback, "negative": {"artifact": pin(invalid), "playback": bad_playback}}
    (output / "audio-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New destination for exports and native playback receipts")
    print(json.dumps(check(parser.parse_args().output), indent=2))
