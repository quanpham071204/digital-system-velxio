<style>h2,h3 { break-after: avoid; } th,td { font-size:9pt; padding:1px 5px; }</style>

# C02 — Bộ cộng trừ 2 bit

## Mục tiêu và thiết kế

Mạch Nhóm 1 dùng 74HC86, 74HC08, 74HC32 thực hiện `A1A0 + B1B0` khi M=0 và `A1A0 − B1B0` khi M=1. Bốn LED lần lượt là S0, S1, Cout và Overflow. Mỗi công tắc có điện trở kéo xuống 10 kΩ; mỗi LED có điện trở 330 Ω. Các đầu vào cổng dư nối GND.

```text
 B0 ── XOR M ──┐         B1 ── XOR M ──┐
 A0 ─────────── FA0 ─C1─> A1 ─────────── FA1 ── Cout
 M ────────────┘  │                     │
                 S0                    S1
                          C1 ── XOR ── Cout → Overflow
```

Với i=0,1: `Bi' = Bi ⊕ M`, `C0 = M`, `Pi = Ai ⊕ Bi'`, `Si = Pi ⊕ Ci`, `Ci+1 = (Ai·Bi') + (Pi·Ci)`. `Overflow = C1 ⊕ Cout`. Khi M=1, phép tính là `A + ~B + 1` trong hai bit.

Hai IC 74HC86 thực hiện đảo có điều kiện, propagate, tổng và Overflow; một 74HC08 tạo carry và một 74HC32 ghép carry. Công tắc từ trên xuống A0, B0, A1, B1, M. Mở `C02-cong-tru-2bit.vlx` trong Velxio.

<div style="page-break-before: always"></div>

## Bảng chân trị

Số bit A và B được ghi theo thứ tự A1A0 và B1B0. Overflow tính theo số có dấu bù 2, phạm vi −2 đến +1.

| A1A0 | B1B0 | M | S1S0 | Cout | Overflow |
|:---:|:---:|:-:|:---:|:-:|:-:|
| 00 | 00 | 0 | 00 | 0 | 0 |
| 00 | 00 | 1 | 00 | 1 | 0 |
| 00 | 01 | 0 | 01 | 0 | 0 |
| 00 | 01 | 1 | 11 | 0 | 0 |
| 00 | 10 | 0 | 10 | 0 | 0 |
| 00 | 10 | 1 | 10 | 0 | 1 |
| 00 | 11 | 0 | 11 | 0 | 0 |
| 00 | 11 | 1 | 01 | 0 | 0 |
| 01 | 00 | 0 | 01 | 0 | 0 |
| 01 | 00 | 1 | 01 | 1 | 0 |
| 01 | 01 | 0 | 10 | 0 | 1 |
| 01 | 01 | 1 | 00 | 1 | 0 |
| 01 | 10 | 0 | 11 | 0 | 0 |
| 01 | 10 | 1 | 11 | 0 | 1 |
| 01 | 11 | 0 | 00 | 1 | 0 |
| 01 | 11 | 1 | 10 | 0 | 1 |
| 10 | 00 | 0 | 10 | 0 | 0 |
| 10 | 00 | 1 | 10 | 1 | 0 |
| 10 | 01 | 0 | 11 | 0 | 0 |
| 10 | 01 | 1 | 01 | 1 | 1 |
| 10 | 10 | 0 | 00 | 1 | 1 |
| 10 | 10 | 1 | 00 | 1 | 0 |
| 10 | 11 | 0 | 01 | 1 | 1 |
| 10 | 11 | 1 | 11 | 0 | 0 |
| 11 | 00 | 0 | 11 | 0 | 0 |
| 11 | 00 | 1 | 11 | 1 | 0 |
| 11 | 01 | 0 | 00 | 1 | 0 |
| 11 | 01 | 1 | 10 | 1 | 0 |
| 11 | 10 | 0 | 01 | 1 | 1 |
| 11 | 10 | 1 | 01 | 1 | 0 |
| 11 | 11 | 0 | 10 | 1 | 0 |
| 11 | 11 | 1 | 00 | 1 | 0 |

## Carry và tràn có dấu

Cout là carry ra của phép cộng bên trong. Với phép trừ không dấu, Cout=1 nghĩa là không mượn, Cout=0 nghĩa là có mượn. Overflow báo kết quả có dấu vượt khoảng −2…+1; hai cờ không tương đương. Ví dụ `11 + 01 = 00`, Cout=1 nhưng Overflow=0 khi hiểu −1 + 1 = 0; `01 + 01 = 10`, Cout=0 nhưng Overflow=1 khi hiểu 1 + 1 = 2.

Phép trừ có dấu có đúng **4 trong 16** trường hợp tràn: `00−10` (0−(−2)=2), `01−10` (1−(−2)=3), `01−11` (1−(−1)=2), `10−01` (−2−1=−3). Đây là kết quả đếm đầy đủ theo miền hai bit; con số bốn là đúng.

## Kiểm chứng và thực tế

Từ thư mục repo chạy `python tools/gen_c02.py C02-cong-tru-2bit/C02-cong-tru-2bit.vlx`. Script lưu rồi đọc lại JSON từ file `.vlx`, truy ngược dây từ điện trở LED qua các cổng, đối chiếu cả 32 tổ hợp với phép tính số nguyên và điều kiện tràn có dấu. Kiểm chứng logic không thay thế mô phỏng Velxio hoặc đo mạch thật.

Velxio cấp VCC nội bộ cho IC theo quy ước project; phần cứng thật cần nối VCC/GND đúng chân, tụ decoupling gần mỗi IC, mức xác định cho các đầu vào không dùng và kiểm tra dòng LED theo datasheet. Chưa khẳng định đã chạy mô phỏng hoặc đo phần cứng.

## PDF và video

Báo cáo: [C02-cong-tru-2bit.pdf](C02-cong-tru-2bit.pdf). Chưa có video demo: cửa sổ Velxio đang thu nhỏ, công cụ UI không quan sát được và không cung cấp thao tác di chuyển con trỏ mượt theo đường vòng. Không tạo video thay thế bằng ảnh tĩnh hoặc khẳng định LED đã được quan sát.


