#!/usr/bin/env python3
"""Sinh project Velxio cho B08: khảo sát D Flip-Flop (Nhóm 2).

  (a) flip-flop-d: D = công tắc, CLK = công tắc gạt (clock tay); kèm một D latch
      kích mức (NOT, AND, NOR) dùng chung D và CLK (= EN) để so sánh.
  (b) Linh kiện D-FF của Velxio không có PRE/CLR, nên dựng D-FF kích cạnh lên
      theo cấu trúc 6 cổng NAND 3 ngõ vào của 74HC74 (mỗi NAND = AND-3 + NOT),
      có PRE_n, CLR_n tích cực mức thấp (công tắc mặc định = 1).
  (c) flip-flop-d với Qbar nối về D: chia tần 2, CLK = công tắc riêng.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B08 - Khao sat D Flip-Flop")
p.power(40, 1100)

# ── (a) chốt dữ liệu ────────────────────────────────────────────────────────
Da = p.switch("Da", 160, 60, "#ffcc00")
CLKa = p.switch("CLKa", 160, 190, "#66ccff")
Qa, Qba = p.ff("d", "ff_a", 480, 100, CLKa, D=Da)
p.led(Qa, "led_qa", 640, 60, "(a) Q", "red")
p.led(Qba, "led_qba", 640, 150, "(a) Q̄", "white")
# Để so sánh: D latch kích mức (EN = CLKa) dựng từ NOT, AND, NOR
nD = p.gate("not", "lat_nd", 900, 40, Da)
S = p.gate("and", "lat_s", 1000, 20, Da, CLKa)        # S = D·EN
R = p.gate("and", "lat_r", 1000, 120, nD, CLKa)       # R = D'·EN
p.comp("logic-gate-nor", "lat_q", 1160, 120)          # Q  = NOR(R, Q̄)
p.comp("logic-gate-nor", "lat_qb", 1160, 20)          # Q̄  = NOR(S, Q)
p.wire(R, ("lat_q", "A")); p.wire(("lat_qb", "Y"), ("lat_q", "B"))
p.wire(S, ("lat_qb", "A")); p.wire(("lat_q", "Y"), ("lat_qb", "B"))
p.led(("lat_q", "Y"), "led_latch", 1320, 100, "(a) Q latch", "orange")

# ── (b) D-FF 6 NAND có PRE/CLR bất đồng bộ ───────────────────────────────────
Db = p.switch("Db", 160, 340, "#ffcc00")
CLKb = p.switch("CLKb", 160, 460, "#66ccff")
PREn = p.switch("PREn", 160, 580, "#ff66cc", value=1)
CLRn = p.switch("CLRn", 160, 700, "#ff5050", value=1)

def nand3(cid, x, y):
    """NAND 3 ngõ vào = AND-3 + NOT; trả về (id AND-3, chân ra NOT)."""
    p.comp("logic-gate-and-3", f"{cid}_and", x, y)
    y_ = p.gate("not", f"{cid}_not", x + 120, y + 6, (f"{cid}_and", "Y"))
    return f"{cid}_and", y_

n1a, n1 = nand3("n1", 440, 330)
n2a, n2 = nand3("n2", 440, 430)
n3a, n3 = nand3("n3", 440, 530)
n4a, n4 = nand3("n4", 440, 630)
qa_, Qb = nand3("nq", 760, 400)
qba_, Qbb = nand3("nqb", 760, 540)
def ins(g, a, b, c):
    p.wire(a, (g, "A")); p.wire(b, (g, "B")); p.wire(c, (g, "C"))
ins(n1a, PREn, n4, n2)          # n1 = NAND(PRE_n, n4, n2)
ins(n2a, n1, CLRn, CLKb)        # n2 = NAND(n1, CLR_n, CLK)
ins(n3a, n2, CLKb, n4)          # n3 = NAND(n2, CLK, n4)
ins(n4a, n3, Db, CLRn)          # n4 = NAND(n3, D, CLR_n)
ins(qa_, PREn, n2, Qbb)         # Q  = NAND(PRE_n, n2, Q̄)
ins(qba_, Qb, n3, CLRn)         # Q̄  = NAND(Q, n3, CLR_n)
p.led(Qb, "led_qb", 1000, 380, "(b) Q", "red")
p.led(Qbb, "led_qbb", 1000, 520, "(b) Q̄", "white")

# ── (c) chia tần 2 ───────────────────────────────────────────────────────────
CLKc = p.switch("CLKc", 160, 860, "#66ccff")
p.comp("flip-flop-d", "ff_c", 480, 860)
p.wire(CLKc, ("ff_c", "CLK"))
p.wire(("ff_c", "Qbar"), ("ff_c", "D"))
p.led(CLKc, "led_clkc", 640, 800, "(c) CLK", "blue")
p.led(("ff_c", "Q"), "led_qc", 640, 900, "(c) Q = CLK/2", "green")

p.save(sys.argv[1])
