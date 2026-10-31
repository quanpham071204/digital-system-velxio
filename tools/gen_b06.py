#!/usr/bin/env python3
"""Sinh project Velxio cho B06: mạch biểu quyết đa số 3 người (Nhóm 2: cổng AND, OR rời).

  Thông qua: Y = AB + BC + AC  (3 AND + 2 OR = 5 cổng 2 ngõ vào)
  Nhất trí : U = ABC = (AB)·C  (thêm 1 AND, dùng lại AB)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B06 - Bieu quyet da so 3 nguoi")
p.power(40, 520)
A = p.switch("A", 160, 100, "#ffcc00")
B = p.switch("B", 160, 250, "#33cc66")
C = p.switch("C", 160, 400, "#66ccff")

ab = p.gate("and", "g_ab", 480, 80, A, B)
bc = p.gate("and", "g_bc", 480, 200, B, C)
ac = p.gate("and", "g_ac", 480, 320, A, C)
o1 = p.gate("or", "g_or1", 640, 130, ab, bc)
y = p.gate("or", "g_or2", 800, 220, o1, ac)
u = p.gate("and", "g_abc", 640, 440, ab, C)

p.led(y, "led_tq", 960, 200, "Thông qua", "green")
p.led(u, "led_nt", 960, 420, "Nhất trí", "blue")
p.save(sys.argv[1])
