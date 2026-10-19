#!/usr/bin/env python3
"""Sinh project Velxio cho B01: 6 IC 74HC, 2 công tắc A/B dùng chung, 1 LED cho mỗi ngõ ra."""
import json, datetime, sys

C_PWR, C_GND, C_SIG = '#ff3030', '#000000', '#00aaff'
C_A, C_B = '#ffcc00', '#33cc66'
comps, wires = [], []

def comp(t, i, x, y, props=None):
    comps.append({"id": i, "metadataId": t, "x": x, "y": y, "properties": props or {}})

def w(i, a, b, color=C_SIG):
    wires.append({"id": i,
                  "start": {"componentId": a[0], "pinName": a[1], "x": 0, "y": 0},
                  "end": {"componentId": b[0], "pinName": b[1], "x": 0, "y": 0},
                  "waypoints": [], "color": color})

# 5 V rail (DC signal generator, GND = SPICE node 0)
comp("signal-generator", "src", 40, 420, {"waveform": "dc", "offset": 5, "amplitude": 0, "frequency": 1})

# Input switches A, B with 10k pull-down
for name, y, col in (("A", 160, C_A), ("B", 320, C_B)):
    s, r = f"sw{name}", f"rpd{name}"
    comp("slide-switch", s, 170, y, {"value": 0})
    comp("resistor", r, 260, y + 40, {"value": "10000"})
    w(f"{s}_pwr", ("src", "SIG"), (s, "3"), C_PWR)
    w(f"{s}_pd", (s, "2"), (r, "1"), col)
    w(f"{r}_gnd", (r, "2"), ("src", "GND"), C_GND)

ics = [("00", "NAND", 4), ("02", "NOR", 4), ("04", "NOT", 6),
       ("08", "AND", 4), ("32", "OR", 4), ("86", "XOR", 4)]
colors = ["red", "green", "blue", "yellow", "orange", "white"]

for idx, (num, fn, n) in enumerate(ics):
    r_, c_ = divmod(idx, 3)
    x, y = 480 + c_ * 430, 100 + r_ * 430
    ic = f"ic{num}"
    comp(f"ic-74hc{num}", ic, x, y)
    # VCC pin is auto-tied to Velxio's internal 5 V rail (vcc_rail); wiring the
    # generator to it puts two V-sources in parallel -> "singular matrix".
    w(f"{ic}_gnd", (ic, "GND"), ("src", "GND"), C_GND)
    for g in range(1, n + 1):
        w(f"{ic}_{g}A", ("swA", "2"), (ic, f"{g}A"), C_A)
        if n == 4:
            w(f"{ic}_{g}B", ("swB", "2"), (ic, f"{g}B"), C_B)
        rl, led = f"r{num}_{g}", f"led{num}_{g}"
        ly = y - 20 + (g - 1) * 55
        comp("resistor", rl, x + 140, ly, {"value": "330"})
        comp("led", led, x + 250, ly - 15,
             {"color": colors[idx], "label": f"{num}·{g}Y {fn}"})
        w(f"{rl}_in", (ic, f"{g}Y"), (rl, "1"), C_SIG)
        w(f"{rl}_led", (rl, "2"), (led, "A"), C_SIG)
        w(f"{led}_gnd", (led, "C"), ("src", "GND"), C_GND)

payload = {"format": "velxio-project", "version": 1,
           "exportedAt": datetime.datetime.now(datetime.UTC).isoformat(),
           "name": "B01 - Kiem tra IC 74HC",
           "boards": [], "fileGroups": {}, "components": comps, "wires": wires,
           "activeBoardId": None}
out = sys.argv[1]
json.dump(payload, open(out, "w"), indent=1)
print(len(comps), "components,", len(wires), "wires")
