<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C07 — Bộ đếm đồng bộ lên/xuống

## Thiết kế

Ba T flip-flop Nhóm 2 dùng chung clock, đếm modulo 8 tại cạnh lên. U=1 đếm lên, U=0 đếm xuống. Công tắc CLK ở trên, U ở dưới và mặc định U=1. LED từ trên xuống Q0, Q1, Q2, OVER.

```text
 U, Q0, Q1, Q2 ──→ [AND / OR / NOT] ──→ T0, T1, T2
                                          ↓   ↓   ↓
CLK ────────────────────────────────────→ ba T-FF
                                          ↓   ↓   ↓
                                         Q0  Q1  Q2
 U, Q0, Q1, Q2 ──→ [logic trạng thái biên] ──→ OVER
```

Các phương trình thực hiện trong mạch:

- `T0 = 1`
- `T1 = U·Q0 + ¬U·¬Q0`
- `T2 = U·Q0·Q1 + ¬U·¬Q0·¬Q1`
- `OVER = U·Q2·Q1·Q0 + ¬U·¬Q2·¬Q1·¬Q0`

OVER là **cờ tổ hợp trạng thái biên**, sáng khi U=1 và Q=111 hoặc U=0 và Q=000: tức trước cạnh lên kế tiếp sẽ quay vòng nếu U giữ nguyên. Nó không phải cờ đã chốt hay xung sau khi quay vòng, và có thể đổi ngay khi U đổi. Mạch dùng 3 T-FF, 4 NOT, 12 AND và 3 OR; công tắc có điện trở kéo xuống 10 kΩ, mỗi LED có điện trở 330 Ω.

<div style="page-break-before: always"></div>

## Bảng trạng thái tại cạnh lên

| Q2Q1Q0 hiện tại | Sau cạnh, U=1 | Sau cạnh, U=0 | OVER khi U=1 | OVER khi U=0 |
|:---:|:---:|:---:|:-:|:-:|
| 000 | 001 | 111 | 0 | 1 |
| 001 | 010 | 000 | 0 | 0 |
| 010 | 011 | 001 | 0 | 0 |
| 011 | 100 | 010 | 0 | 0 |
| 100 | 101 | 011 | 0 | 0 |
| 101 | 110 | 100 | 0 | 0 |
| 110 | 111 | 101 | 0 | 0 |
| 111 | 000 | 110 | 1 | 0 |

Nếu không có cạnh lên, trạng thái FF giữ nguyên kể cả khi U thay đổi. Cờ OVER tổ hợp có thể thay đổi theo U ngay lúc đó.

## Kiểm chứng và thực tế

Từ thư mục repo chạy `python tools/gen_c07.py C07-dem-len-xuong/C07-dem-len-xuong.vlx`. Script lưu rồi dùng `vlx_extra.Circuit` đọc file, cấp 8 trạng thái và 2 chiều, kiểm các chuyển CLK 0→1, 1→1 và 1→0: 48 trường hợp; đồng thời kiểm cờ OVER, ba chân clock chung và đổi U không có cạnh rồi đếm tiếp theo chiều mới. Chuỗi từ 000: lên 0→1→2→3→4→5→6→7→0; xuống 0→7→6→5→4→3→2→1→0.

Mô hình kiểm tra cấp trạng thái, không chứng minh khởi động phần cứng. Chuỗi kiểm tra bắt đầu từ trạng thái 0 được cấp cho bộ kiểm chứng; trạng thái khi nạp Velxio cần quan sát. Mạch thật cần khởi tạo phù hợp, chống dội clock và đáp ứng setup/hold cho U. Do trễ cổng và lệch thời điểm Q trên phần cứng, OVER tổ hợp có thể glitch; cần chốt/đồng bộ nếu mạch sau yêu cầu tín hiệu ổn định. Chưa chạy Velxio hoặc quay video.
