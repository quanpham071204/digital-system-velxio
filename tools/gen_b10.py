#!/usr/bin/env python3
"""Sinh project Velxio cho B10: T Flip-Flop và bộ đếm gợn 3 bit (Nhóm 2).

  (a) Ba T-FF dùng chung T và CLK: flip-flop-t có sẵn; JK với J = K = T;
      D với D = T ⊕ Q = T·Q̄ + T̄·Q (XOR dựng từ NOT, AND, OR).
  (b) Bộ đếm gợn 3 bit từ 3 flip-flop-t (T = 1). FF kích cạnh lên nên tầng sau
      lấy clock từ Q̄ tầng trước để đếm lên; công tắc DN chọn Q (đếm xuống):
      CLK(i+1) = DN̄·Q̄i + DN·Qi.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B10 - T Flip-Flop va bo dem gon 3 bit")
p.power(40, 1000)

# ── (a) ba phiên bản T Flip-Flop ─────────────────────────────────────────────
T = p.switch("T", 160, 60, "#ffcc00")
CLKa = p.switch("CLKa", 160, 200, "#66ccff")
Qt, _ = p.ff("t", "ff_t", 480, 40, CLKa, T=T)
Qjk, _ = p.ff("jk", "ff_jk", 480, 150, CLKa, J=T, K=T)
p.comp("flip-flop-d", "ff_d", 860, 270)
p.wire(CLKa, ("ff_d", "CLK"))
nT = p.gate("not", "x_nt", 440, 280, T)
x1 = p.gate("and", "x_a1", 560, 250, T, ("ff_d", "Qbar"))   # T·Q̄
x2 = p.gate("and", "x_a2", 560, 330, nT, ("ff_d", "Q"))     # T̄·Q
xo = p.gate("or", "x_or", 700, 290, x1, x2)                 # T ⊕ Q
p.wire(xo, ("ff_d", "D"))
p.led(Qt, "led_t", 1040, 20, "(a) Q T-FF có sẵn", "red")
p.led(Qjk, "led_jk", 1040, 130, "(a) Q JK (J=K=T)", "orange")
p.led(("ff_d", "Q"), "led_dx", 1040, 260, "(a) Q D + XOR", "yellow")

# ── (b) bộ đếm gợn 3 bit ────────────────────────────────────────────────────
CLKr = p.switch("CLKr", 160, 520, "#66ccff")
DN = p.switch("DN", 160, 680, "#ff66cc")
nDN = p.gate("not", "m_ndn", 420, 760, DN)
clk = CLKr
for i in range(3):
    x = 480 + i * 330
    p.comp("flip-flop-t", f"ff{i}", x, 520)
    p.to_vcc((f"ff{i}", "T"))
    p.wire(clk, (f"ff{i}", "CLK"))
    q, qb = (f"ff{i}", "Q"), (f"ff{i}", "Qbar")
    p.led(q, f"led_q{i}", x + 100, 440, f"Q{i}", "green")
    if i < 2:   # bộ chọn nguồn clock cho tầng sau
        up = p.gate("and", f"m_up{i}", x + 110, 600, qb, nDN)
        dn = p.gate("and", f"m_dn{i}", x + 110, 690, q, DN)
        clk = p.gate("or", f"m_or{i}", x + 220, 640, up, dn)
p.led(CLKr, "led_clkr", 300, 440, "CLK", "blue")
p.save(sys.argv[1])
