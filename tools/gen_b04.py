#!/usr/bin/env python3
"""Sinh 3 project Velxio cho B04 (74HC14 Schmitt trigger).

  B04a-dao-dong-RC.vlx  : bộ dao động RC thiết kế cho mạch thật (1 Hz và 1 kHz).
                          Velxio KHÔNG giải được (xem báo cáo mục 4.2).
  B04a-clock.vlx        : thay thế trong mô phỏng: Signal Generator vuông 1 kHz
                          -> 74HC14 sửa dạng xung, xem bằng Oscilloscope.
  B04b-chong-doi.vlx    : nút nhấn + pull-up + RC + 74HC14 (chống dội).
Cách dùng: python3 tools/gen_b04.py B04-Schmitt-trigger
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

out = sys.argv[1]

# ── (a) Bộ dao động RC: R hồi tiếp 1Y -> 1A, C từ 1A xuống GND ──────────────
p = Project("B04a - Dao dong RC 74HC14 (mach that)")
p.power(40, 420)
u = p.ic("14", "u1", 420, 220)
def osc(g, r_fixed, pot_total, cap, ycomp, label, color):
    a, y = (u, f"{g}A"), (u, f"{g}Y")
    rf, pot, c = f"rf{g}", f"pot{g}", f"c{g}"
    p.comp("resistor", rf, 600, ycomp, {"value": r_fixed})
    p.comp("potentiometer", pot, 760, ycomp - 30, {"value": 512, "total": pot_total})
    p.comp("capacitor", c, 300, ycomp + 60, {"value": cap})
    # R cố định nối tiếp biến trở; biến trở mắc kiểu rheostat (chân GND nối
    # chung con trượt SIG) nên điện trở thay đổi 0 … pot_total.
    p.wire(y, (rf, "1"))
    p.wire((rf, "2"), (pot, "VCC"))
    p.wire((pot, "SIG"), (pot, "GND"))
    p.wire((pot, "SIG"), a)
    p.wire(a, (c, "1"))
    p.to_gnd((c, "2"))
    p.led(y, f"led{g}", 900, ycomp + 40, label, color)
osc(1, "100000", "50000", "10u", 80, "1 Hz", "red")
osc(2, "10000", "5000", "100n", 340, "1 kHz", "green")
for g in (3, 4, 5, 6):
    p.to_gnd((u, f"{g}A"))
p.save(f"{out}/B04a-dao-dong-RC.vlx")

# ── (a) Thay thế trong mô phỏng: khối tạo xung + 74HC14 ────────────────────
p = Project("B04a - Clock 1 kHz qua 74HC14")
p.power(40, 420)
p.comp("signal-generator", "gen", 40, 160,
       {"waveform": "square", "frequency": 1000, "amplitude": 2.5, "offset": 2.5})
p.to_gnd(("gen", "GND"))
u = p.ic("14", "u1", 420, 200)
p.wire(("gen", "SIG"), (u, "1A"))
p.wire((u, "1Y"), (u, "2A"))          # 2 tầng đảo -> CLK cùng pha với nguồn
p.led((u, "1Y"), "led_clkn", 620, 120, "CLK đảo (1Y)", "yellow")
p.led((u, "2Y"), "led_clk", 620, 260, "CLK (2Y)", "green")
for g in (3, 4, 5, 6):
    p.to_gnd((u, f"{g}A"))
p.save(f"{out}/B04a-clock.vlx")

# ── (b) Chống dội nút nhấn ──────────────────────────────────────────────────
p = Project("B04b - Chong doi nut nhan RC + 74HC14")
p.power(40, 420)
p.comp("pushbutton", "btn", 200, 300, {"color": "red", "pressed": False})
p.comp("resistor", "rpu", 200, 160, {"value": "10000"})     # pull-up
p.comp("resistor", "rrc", 400, 240, {"value": "22000"})     # R của khâu RC
p.comp("capacitor", "crc", 520, 360, {"value": "1u"})       # C của khâu RC
u = p.ic("14", "u1", 640, 220)
X, C = ("btn", "1.l"), ("crc", "1")
p.to_vcc(("rpu", "1"))
p.wire(("rpu", "2"), X)
p.to_gnd(("btn", "2.l"))
p.wire(X, ("rrc", "1"))
p.wire(("rrc", "2"), C)
p.to_gnd(("crc", "2"))
p.wire(C, (u, "1A"))                  # qua RC + Schmitt: đã chống dội
p.wire(X, (u, "2A"))                  # trực tiếp: để so sánh
p.led((u, "1Y"), "led_db", 840, 160, "Có chống dội", "green")
p.led((u, "2Y"), "led_raw", 840, 300, "Không chống dội", "red")
for g in (3, 4, 5, 6):
    p.to_gnd((u, f"{g}A"))
p.save(f"{out}/B04b-chong-doi.vlx")
