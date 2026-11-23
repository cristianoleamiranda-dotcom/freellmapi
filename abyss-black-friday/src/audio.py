"""Cama sonora mínima y oscura para el reel (120 BPM, rejilla de cortes).

Kick en negras, hat contratiado, drone sub muy bajo, riser antes de cada
whip e impacto en los cortes. Sin melodía: no compite con el audio que el
estudio elija en Instagram.
"""

from __future__ import annotations

import numpy as np

SR = 48000


def _env(n, a=0.002, d=0.18, curve=3.0):
    t = np.arange(n) / SR
    atk = np.clip(t / a, 0, 1)
    dec = np.clip(1 - (t - a) / d, 0, 1) ** curve
    return atk * dec


def kick(dur=0.30, f0=120.0, f1=44.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 26)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * _env(n, 0.001, dur * 0.9, 2.2)
    click = np.random.default_rng(3).normal(0, 1, n) * _env(n, 0.0005, 0.012, 2.0) * 0.35
    return body + click


def hat(dur=0.06, bright=0.6):
    n = int(dur * SR)
    rng = np.random.default_rng(11)
    x = rng.normal(0, 1, n)
    # high-pass barato: diferencia
    x = np.diff(np.concatenate([[0], x]))
    return x * _env(n, 0.0005, dur, 2.5) * bright


def sub(dur, f=55.0, level=0.16):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t)) * level


def riser(dur=0.5):
    n = int(dur * SR)
    rng = np.random.default_rng(21)
    x = rng.normal(0, 1, n)
    k = 9
    y = np.convolve(x, np.ones(k) / k, mode="same")
    t = np.arange(n) / n
    return y * (t ** 2.4) * 0.5


def impact(dur=0.5):
    n = int(dur * SR)
    rng = np.random.default_rng(31)
    x = rng.normal(0, 1, n)
    k = 60
    y = np.convolve(x, np.ones(k) / k, mode="same")
    return y * _env(n, 0.001, dur, 2.6) * 0.9 + kick(dur, 90, 38) * 0.8


def add(buf, sig, at):
    i0 = int(at * SR)
    i1 = min(len(buf), i0 + len(sig))
    if i0 < len(buf):
        buf[i0:i1] += sig[: i1 - i0]


def build(duration: float, beats: list[float], whips: list[float], bpm: float = 120.0) -> np.ndarray:
    n = int(duration * SR)
    buf = np.zeros(n)
    spb = 60.0 / bpm
    add(buf, sub(duration, 55.0, 0.14), 0.0)
    t = 0.0
    i = 0
    while t < duration - 0.25:
        add(buf, kick(0.30) * 0.85, t)
        if t + spb / 2 < duration - 0.2:
            add(buf, hat(0.06, 0.35), t + spb / 2)
        t += spb
        i += 1
    for w in whips:
        add(buf, riser(0.5), max(0.0, w - 0.5))
        add(buf, impact(0.55), w)
    for c in beats:
        add(buf, hat(0.09, 0.5), c)
    # fade in/out
    fi = int(0.08 * SR)
    fo = int(0.6 * SR)
    buf[:fi] *= np.linspace(0, 1, fi)
    buf[-fo:] *= np.linspace(1, 0, fo)
    peak = np.abs(buf).max() or 1.0
    buf = buf / peak * 0.82
    return buf


def write_wav(path, buf: np.ndarray) -> None:
    import wave
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    stereo = np.stack([pcm, pcm], axis=-1).ravel()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())
