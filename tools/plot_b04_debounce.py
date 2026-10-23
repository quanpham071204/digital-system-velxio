#!/usr/bin/env python3
"""Mô phỏng lý thuyết mạch chống dội B04b (Velxio không tạo dội phím).

Nút nhấn có dội -> nút X (pull-up R1) -> R2 -> tụ C -> 74HC14 (ngưỡng theo mô
hình Velxio: V_T+ = 0,6·VCC, V_T- = 0,4·VCC). Vẽ X, V_C và ngõ ra 1Y.
Cách dùng: python3 tools/plot_b04_debounce.py B04-Schmitt-trigger/img/B04b_ly_thuyet.png
"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

VCC, R1, R2, C = 5.0, 10e3, 22e3, 1e-6
VTP, VTM = 0.6 * VCC, 0.4 * VCC
PRESS = [20.0, 20.8, 21.5, 23.0, 23.8, 26.0, 26.5]      # ms, các lần tiếp điểm đổi trạng thái
RELEASE = [120.0, 120.7, 122.0, 122.6, 124.5]
DT, T_END = 1e-5, 0.22

def contact(t_ms):
    return sum(t_ms >= e for e in PRESS + RELEASE) % 2   # 1 = tiếp điểm đóng

ts, xs, vcs, ys, edges = [], [], [], [], []
v, out, t = VCC, 0, 0.0
while t < T_END:
    tm = t * 1e3
    closed = contact(tm)
    # đóng: tụ xả qua R2 về 0; hở: tụ nạp qua R1 + R2 lên VCC
    v += ((0 - v) / (R2 * C) if closed else (VCC - v) / ((R1 + R2) * C)) * DT
    x = 0.0 if closed else VCC - (VCC - v) * R1 / (R1 + R2)
    new = 1 if (out == 0 and v < VTM) else 0 if (out == 1 and v > VTP) else out
    if new != out:
        edges.append((round(tm, 1), new))
    out = new
    ts.append(tm); xs.append(x); vcs.append(v); ys.append(out * VCC)
    t += DT

fig, axs = plt.subplots(3, 1, figsize=(9, 5.5), sharex=True)
axs[0].plot(ts, xs, drawstyle='steps-post', color='tab:red')
axs[0].set_ylabel('X (nút nhấn,\ncó dội)', rotation=0, ha='right')
axs[1].plot(ts, vcs, color='tab:blue')
axs[1].axhline(VTP, ls='--', c='gray'); axs[1].axhline(VTM, ls=':', c='gray')
axs[1].text(T_END * 1e3, VTP + 0.15, 'V_T+ = 3,0 V', ha='right', fontsize=8)
axs[1].text(T_END * 1e3, VTM - 0.7, 'V_T− = 2,0 V', ha='right', fontsize=8)
axs[1].set_ylabel('V_C\n(sau RC)', rotation=0, ha='right')
axs[2].plot(ts, ys, drawstyle='steps-post', color='tab:green')
axs[2].set_ylabel('1Y\n(74HC14)', rotation=0, ha='right')
for a in axs:
    a.set_ylim(-0.5, 5.8); a.grid(alpha=.3)
axs[2].set_xlabel('t (ms)')
fig.suptitle('B04b – Chống dội (lý thuyết): R1 = 10 kΩ, R2 = 22 kΩ, C = 1 µF')
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=130)
print('Cạnh ngõ ra (ms, mức):', edges)
