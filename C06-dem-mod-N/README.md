<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C06 — Bộ đếm đồng bộ mod-N

## Thiết kế

Mạch mặc định N=6, sử dụng ba D flip-flop và cổng AND, OR, NOT rời Nhóm 2; ba FF cùng nhận cạnh lên CLK. Tại mỗi cạnh, trạng thái `q < N−1` chuyển sang `q+1`, còn `q ≥ N−1` chuyển về 000. Do đó hai trạng thái không dùng 110 và 111 tự phục hồi về 000 ở cạnh lên tiếp theo. Đây là hồi phục đồng bộ, không phải reset bất đồng bộ.

```text
          ┌──────────────────────────────┐
          │ logic trạng thái kế tiếp D  │
          │  AND / OR / NOT             │
          └─ D0 ─── D1 ─── D2 ─────────┘
              ↓       ↓       ↓
CLK ───────→ FF0 ──→ FF1 ──→ FF2   (clock chung)
              Q0      Q1      Q2 ──→ LED
              └──── hồi tiếp Q ──────┘
```

Mũi tên giữa các khối FF trong hình chỉ vị trí, **không phải** clock nối tầng: mỗi FF nối trực tiếp CLK. Công tắc CLK có pull-down 10 kΩ; mỗi LED Q0, Q1, Q2 có điện trở 330 Ω. Các FF không có ngõ reset trong mạch.

Với `mᵢ` là minterm Q2Q1Q0 tương ứng số i, đúng cấu trúc cổng trong file là:

- `D0 = m0 + m2 + m4`
- `D1 = m1 + m2`
- `D2 = m3 + m4`

Mỗi minterm gồm ba biến Q hoặc phần bù: ví dụ `m2=¬Q2·Q1·¬Q0`. Mạch dùng 3 NOT chung, 14 AND và 4 OR, tổng 21 cổng; cách tổng các minterm giúp thể hiện rõ chuyển trạng thái, chưa khẳng định tối thiểu cổng.

<div style="page-break-before: always"></div>

## Bảng trạng thái N=6

| Hiện tại Q2Q1Q0 | D2D1D0 = trạng thái sau cạnh lên | Ý nghĩa |
|:---:|:---:|---|
| 000 | 001 | 0 → 1 |
| 001 | 010 | 1 → 2 |
| 010 | 011 | 2 → 3 |
| 011 | 100 | 3 → 4 |
| 100 | 101 | 4 → 5 |
| 101 | 000 | 5 → 0 |
| 110 | 000 | tự phục hồi |
| 111 | 000 | tự phục hồi |

## Kiểm chứng

Từ thư mục repo, chạy `python tools/gen_c06.py C06-dem-mod-N/C06-dem-mod-N.vlx`. Để tạo mạch khác, dùng tùy chọn `--N 5`, `--N 6` hoặc `--N 7` cùng đường dẫn đích riêng. Script lưu, đọc lại file bằng `vlx_extra.Circuit`, cấp đủ 8 trạng thái và kiểm 0→1, 1→1, 1→0 ở clock: 24 trường hợp cho mỗi N. Chuỗi N=6 là 0→1→2→3→4→5→0; đã kiểm riêng N=5 và N=7 bằng file tạm. Kiểm tra cấp trạng thái vào mô hình không xác nhận trạng thái khởi động phần cứng.

## Mô phỏng và thực tế

Một cách khác là giải mã trạng thái N rồi đưa tín hiệu về CLR bất đồng bộ. Do hồi tiếp clear, xung clear có thể bị rút ngắn; trễ các bit và cổng có thể gây glitch hoặc vi phạm yêu cầu xung reset. Thiết kế C06 quyết định trạng thái kế tiếp đồng bộ và không dùng đường CLR đó; vẫn cần tính setup/hold, clock skew, trễ clock-to-Q và chống dội công tắc khi làm mạch thật. Đây là phân tích, không phải kết quả đo. Chuỗi kiểm tra bắt đầu từ trạng thái 0 được cấp cho bộ kiểm chứng; trạng thái khi nạp Velxio cần quan sát. Mạch thực cần cơ chế khởi tạo phù hợp. Chưa chạy Velxio hoặc quay video.
