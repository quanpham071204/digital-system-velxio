"""Thư viện nhỏ dùng chung cho các script gen_bxx.py: dựng project Velxio (.vlx).

Quy ước giống B01:
  - Nguồn 5 V là Signal Generator ở chế độ DC (chân SIG = +5 V, GND = mass).
  - Công tắc gạt: chân 3 nối +5 V, chân 2 là ngõ ra, pull-down 10 kΩ xuống GND.
  - LED: ngõ ra -> R 330 Ω -> LED -> GND.
"""
import datetime
import json

C_PWR, C_GND, C_SIG = '#ff3030', '#000000', '#00aaff'
SW_COLORS = ['#ffcc00', '#33cc66', '#ff66cc', '#66ccff', '#ff9933', '#cc99ff', '#ffffff']


class Project:
    def __init__(self, name):
        self.name = name
        self.comps, self.wires = [], []
        self._n = 0
        self.sw_count = 0

    # ── primitive ───────────────────────────────────────────────────────────
    def comp(self, kind, cid, x, y, props=None):
        self.comps.append({"id": cid, "metadataId": kind, "x": x, "y": y,
                           "properties": props or {}})
        return cid

    def wire(self, a, b, color=C_SIG):
        self._n += 1
        self.wires.append({"id": f"w{self._n}",
                           "start": {"componentId": a[0], "pinName": a[1], "x": 0, "y": 0},
                           "end": {"componentId": b[0], "pinName": b[1], "x": 0, "y": 0},
                           "waypoints": [], "color": color})

    # ── building blocks ─────────────────────────────────────────────────────
    def power(self, x, y, cid="src"):
        self.comp("signal-generator", cid, x, y,
                  {"waveform": "dc", "offset": 5, "amplitude": 0, "frequency": 1})
        self.vcc, self.gnd = (cid, "SIG"), (cid, "GND")

    def to_gnd(self, pin):
        self.wire(pin, self.gnd, C_GND)

    def to_vcc(self, pin):
        self.wire(self.vcc, pin, C_PWR)

    def switch(self, name, x, y, color=None):
        """Công tắc gạt + pull-down 10 kΩ. Trả về chân ngõ ra (id, '2')."""
        color = color or SW_COLORS[self.sw_count % len(SW_COLORS)]
        self.sw_count += 1
        s, r = f"sw{name}", f"rpd{name}"
        self.comp("slide-switch", s, x, y, {"value": 0})
        self.comp("resistor", r, x + 90, y + 40, {"value": "10000"})
        self.to_vcc((s, "3"))
        self.wire((s, "2"), (r, "1"), color)
        self.to_gnd((r, "2"))
        return (s, "2")

    def led(self, src, cid, x, y, label, color="red", r="330"):
        """Ngõ ra src -> R -> LED -> GND.

        id của LED phải viết thường: ngspice đổi tên nút sang chữ thường nên
        LED có id chứa chữ hoa (vd. "ledNOT") không bao giờ sáng trong Velxio."""
        cid = cid.lower()
        rid = f"r_{cid}"
        self.comp("resistor", rid, x, y + 15, {"value": r})
        self.comp("led", cid, x + 110, y, {"color": color, "label": label})
        self.wire(src, (rid, "1"))
        self.wire((rid, "2"), (cid, "A"))
        self.to_gnd((cid, "C"))

    def ic(self, kind, cid, x, y):
        """IC 74HC: chỉ nối GND; VCC được Velxio cấp ngầm (xem B01 mục 5)."""
        self.comp(f"ic-74hc{kind}", cid, x, y)
        self.to_gnd((cid, "GND"))
        return cid

    def gate(self, kind, cid, x, y, a, b=None):
        """Cổng rời Nhóm 2 (logic-gate-and/or/not/nor ...). Trả về (cid, 'Y')."""
        self.comp(f"logic-gate-{kind}", cid, x, y)
        self.wire(a, (cid, "A"))
        if b is not None:
            self.wire(b, (cid, "B"))
        return (cid, "Y")

    # ── output ──────────────────────────────────────────────────────────────
    def save(self, path):
        payload = {"format": "velxio-project", "version": 1,
                   "exportedAt": datetime.datetime.now(datetime.UTC).isoformat(),
                   "name": self.name, "boards": [], "fileGroups": {},
                   "components": self.comps, "wires": self.wires,
                   "activeBoardId": None}
        with open(path, "w") as f:
            json.dump(payload, f, indent=1, ensure_ascii=False)
        print(f"{path}: {len(self.comps)} components, {len(self.wires)} wires")
