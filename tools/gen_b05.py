#!/usr/bin/env python3
"""Sinh project Velxio cho B05: bộ tạo và kiểm tra bit chẵn lẻ 4 bit (74HC86, 74HC04).

  Bên phát : D3..D0, M (0 = even, 1 = odd)  ->  P = D0^D1^D2^D3^M   (u1: 3 XOR + 1 XOR chọn chế độ)
  Kênh     : E0..E4 lật từng bit để giả lập lỗi truyền                (u2, u3.1: 5 XOR)
  Bên thu  : X = R0^R1^R2^R3^RP (u3.2-4, u4.1: 4 XOR), ERR = X^M (u4.2), OK = NOT ERR (u5)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B05 - Parity 4 bit")
p.power(40, 900)
D = [p.switch(f"D{i}", 160, 80 + i * 110, "#ffcc00") for i in range(4)]
M = p.switch("M", 160, 540, "#ff66cc")
E = [p.switch(f"E{i}", 160, 650 + i * 100, "#ff5050") for i in range(5)]

def x(u, g, a, b):
    p.wire(a, (u, f"{g}A")); p.wire(b, (u, f"{g}B"))
    return (u, f"{g}Y")

# u1: bộ tạo
u1 = p.ic("86", "u1", 480, 140)
s01 = x(u1, 1, D[0], D[1])
s23 = x(u1, 2, D[2], D[3])
S = x(u1, 3, s01, s23)
P = x(u1, 4, S, M)
p.led(P, "led_p", 640, 60, "P (phát)", "yellow")

# u2 + u3.1: kênh truyền có thể lật bit
u2 = p.ic("86", "u2", 480, 420)
R = [x(u2, i + 1, D[i], E[i]) for i in range(4)]
u3 = p.ic("86", "u3", 840, 560)
RP = x(u3, 1, P, E[4])
for i, r in enumerate(R):
    p.led(r, f"led_r{i}", 640, 300 + i * 70, f"R{i}", "blue")
p.led(RP, "led_rp", 640, 580, "RP", "blue")

# bộ kiểm tra: 4 XOR
r01 = x(u3, 2, R[0], R[1])
r23 = x(u3, 3, R[2], R[3])
r03 = x(u3, 4, r01, r23)
u4 = p.ic("86", "u4", 1100, 560)
X = x(u4, 1, r03, RP)
ERR = x(u4, 2, X, M)
for g in (3, 4):
    p.to_gnd((u4, f"{g}A")); p.to_gnd((u4, f"{g}B"))
p.led(ERR, "led_err", 1300, 520, "LỖI", "red")

u5 = p.ic("04", "u5", 1100, 760)
p.wire(ERR, (u5, "1A"))
for g in range(2, 7):
    p.to_gnd((u5, f"{g}A"))
p.led((u5, "1Y"), "led_ok", 1300, 740, "OK", "green")

p.save(sys.argv[1])
