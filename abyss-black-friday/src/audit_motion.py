"""Auditoría 1: fidelidad cinemática referencia vs render + duración ajustable."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from analyze_reference import extract, analyze

REF = ROOT.parent / "dropbox" / "type_01_pindown.io_1795195281.mp4"

def curve(video: Path, fps: float, tag: str, scale="180:-1") -> dict:
    fdir = ROOT / "research" / f"audit_frames_{tag}"
    frames = extract(video, fdir, fps=int(fps), scale=scale)
    return analyze(frames, ROOT / "research" / f"audit_motion_{tag}.json", fps)

def cuts_within(cuts, expected, tol=0.12):
    out = []
    for e in expected:
        hit = min((abs(c - e) for c in cuts), default=99)
        out.append((e, hit <= tol))
    return out

if __name__ == "__main__":
    ref = curve(REF, 30, "ref")
    print(f"REFERENCIA type_01: {ref['duration']}s cortes={ref['cuts']} flow_mean={ref['flow_mean_global']} peak={ref['flow_peak']}")
    pieces = {
        "reel18": (ROOT / "out" / "masters" / "reel_black_friday_abyss_master.mp4", 30, [3.0, 7.2, 13.2], [3.0, 13.2]),
        "reel15": (ROOT / "out" / "masters" / "reel_black_friday_abyss_15s_master.mp4", 30, [2.5, 6.0, 11.0], [2.5, 11.0]),
    }
    report = {"reference": {"cuts": ref["cuts"], "flow_mean": ref["flow_mean_global"], "flow_peak": ref["flow_peak"]}}
    for tag, (path, fps, exp_cuts, exp_whips) in pieces.items():
        d = curve(path, fps, tag)
        # cortes duros detectados + whips (picos de flujo con blur): unimos ambos como "eventos de transición"
        events = sorted(set([round(c, 2) for c in d["cuts"]] + [round(w["t"], 2) for w in d["whips"]]))
        ok_cuts = cuts_within(events, exp_cuts + exp_whips, tol=0.25)
        # push-in: energía de flujo sostenida dentro de cada plano (gramática de la referencia)
        per = [r for r in d["per_frame"] if "flow_mean" in r]
        fm = np.array([r["flow_mean"] for r in per])
        report[tag] = {
            "duration": d["duration"],
            "events_detected": events,
            "expected": exp_cuts + exp_whips,
            "events_match": all(ok for _, ok in ok_cuts),
            "flow_mean": d["flow_mean_global"],
            "flow_peak": d["flow_peak"],
            "pushin_sostenido": bool(fm.mean() > 0.15),
        }
        print(f"{tag}: {d['duration']}s eventos={events} esperados={exp_cuts + exp_whips} match={all(ok for _, ok in ok_cuts)} flow_mean={d['flow_mean_global']} push-in={fm.mean() > 0.15}")
    # ratio de energía: la referencia tiene push-in continuo; el render debe tener flow_mean>0 y picos en whips
    (ROOT / "research" / "audit_motion_report.json").write_text(json.dumps(report, indent=2))
    print("report:", ROOT / "research" / "audit_motion_report.json")
