"""Banda sonora sintetizada, 48 kHz estéreo, 15.0 s a 100 BPM.

No usa material de terceros: todo se genera con numpy para que el proyecto sea
reproducible y libre de licencias de audio.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from timeline import ACCENTS, BEAT, BELL, CUTS, KICKS, RISER, TOTAL

SR = 48000
N = int(SR * TOTAL)


def t_axis(duration: float) -> np.ndarray:
    return np.arange(int(SR * duration)) / SR


def kick(duration: float = 0.42, amp: float = 0.62) -> np.ndarray:
    t = t_axis(duration)
    f = 118 * np.exp(-t * 26) + 43
    phase = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 9.5)
    body = np.sin(phase) * env
    click = np.random.default_rng(3).normal(0, 1, t.size) * np.exp(-t * 240) * 0.16
    return (body + click) * amp


def sub_boom(duration: float = 1.5, amp: float = 0.72) -> np.ndarray:
    t = t_axis(duration)
    f = 62 * np.exp(-t * 3.2) + 28
    phase = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 2.6)
    return np.sin(phase) * env * amp


def tick(amp: float = 0.10) -> np.ndarray:
    t = t_axis(0.05)
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 1, t.size)
    # Paso alto simple: diferencia de la señal
    hp = np.diff(np.concatenate([[0.0], noise]))
    return hp * np.exp(-t * 120) * amp


def bell_note(freq: float = 880.0, duration: float = 1.8, amp: float = 0.20) -> np.ndarray:
    t = t_axis(duration)
    mod = np.sin(2 * np.pi * freq * 2.01 * t) * 2.2 * np.exp(-t * 5)
    carrier = np.sin(2 * np.pi * freq * t + mod)
    partial = np.sin(2 * np.pi * freq * 2.98 * t) * 0.35 * np.exp(-t * 7)
    return (carrier + partial) * np.exp(-t * 2.4) * amp


def pad(duration: float, freqs: tuple[float, ...] = (110.0, 164.81, 220.0), amp: float = 0.10) -> np.ndarray:
    t = t_axis(duration)
    out = np.zeros_like(t)
    for i, f in enumerate(freqs):
        detune = 1 + (i - 1) * 0.0009
        lfo = 1 + 0.12 * np.sin(2 * np.pi * (0.11 + i * 0.03) * t + i)
        out += np.sin(2 * np.pi * f * detune * t) * lfo / (i + 1.4)
    env = np.minimum(1, t / 1.1) * np.minimum(1, np.clip((duration - t) / 1.6, 0, 1))
    return out * env * amp


def riser(duration: float, amp: float = 0.30) -> np.ndarray:
    t = t_axis(duration)
    rng = np.random.default_rng(23)
    noise = rng.normal(0, 1, t.size)
    # Filtro paso alto de un polo con corte creciente
    cutoff = 300 + 5200 * (t / duration) ** 2
    alpha = np.clip(1 - np.exp(-2 * np.pi * cutoff / SR), 0.001, 0.9)
    out = np.zeros_like(noise)
    prev = 0.0
    for i in range(noise.size):
        prev = prev + alpha[i] * (noise[i] - prev)
        out[i] = noise[i] - prev
    env = (t / duration) ** 2.4
    return out * env * amp


def place(track: np.ndarray, sound: np.ndarray, at: float, gain: float = 1.0) -> None:
    start = int(at * SR)
    end = min(track.size, start + sound.size)
    if start >= track.size:
        return
    track[start:end] += sound[: end - start] * gain


def build(path: str | Path) -> dict:
    left = np.zeros(N, dtype=np.float32)
    right = np.zeros(N, dtype=np.float32)

    kick_hit = kick()
    for i, beat in enumerate(KICKS):
        g = 0.95 if beat in ACCENTS else 0.55
        place(left, kick_hit, beat, g)
        place(right, kick_hit, beat, g)

    for cut in CUTS:
        t = tick(0.12 if cut in (7.2, 9.6, 11.4) else 0.075)
        place(left, t, cut, 0.9)
        place(right, t, cut, 0.55)

    # Hats suaves en contratiempo (cada negra + 0.3 s), muy bajo
    hat = tick(0.035)
    for beat in KICKS[:-1]:
        place(left, hat, beat + BEAT / 2, 0.5)
        place(right, hat, beat + BEAT / 2, 0.7)

    p = pad(TOTAL)
    left += p
    right += p * 0.96

    r = riser(RISER[1] - RISER[0])
    place(left, r, RISER[0], 0.9)
    place(right, r, RISER[0], 1.0)

    place(left, sub_boom(), 11.4, 1.0)
    place(right, sub_boom(), 11.4, 1.0)
    place(left, bell_note(), BELL, 0.9)
    place(right, bell_note(), BELL + 0.012, 0.9)

    # Ducking del pad en cada kick (sidechain suave)
    duck = np.ones(N, dtype=np.float32)
    for beat in KICKS:
        start = int(beat * SR)
        length = int(0.28 * SR)
        end = min(N, start + length)
        if start >= N:
            continue
        curve = np.linspace(1.0, 0.42, end - start) ** 0.6
        duck[start:end] = np.minimum(duck[start:end], curve)
    left *= np.where(duck < 0.999, duck, 1.0)
    right *= np.where(duck < 0.999, duck, 1.0)

    # Fade de salida
    fade = int(0.45 * SR)
    left[-fade:] *= np.linspace(1, 0, fade) ** 1.6
    right[-fade:] *= np.linspace(1, 0, fade) ** 1.6

    stereo = np.stack([left, right], axis=1)
    stereo *= 1.0 / max(1e-6, np.max(np.abs(stereo)))
    stereo = np.tanh(stereo * 1.25) / np.tanh(1.25)
    stereo *= 0.85  # ~ -1.4 dBFS
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes(pcm.tobytes())

    return {"path": str(path), "seconds": pcm.shape[0] / SR, "peak": float(np.max(np.abs(stereo)))}


if __name__ == "__main__":
    info = build(Path(__file__).resolve().parent.parent / "render" / "soundtrack.wav")
    print(info)
