<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C09 — LFSR 4 bit

## Thiết kế

Bốn D flip-flop Nhóm 2 cùng nhận clock; các bit dịch `D1=Q0`, `D2=Q1`, `D3=Q2`. Mặc định ALT=0 chọn phản hồi `Q3 ⊕ Q2`; ALT=1 chọn `Q3 ⊕ Q1`. XOR được dựng từ AND, OR, NOT: `X⊕Y = X·¬Y + ¬X·Y`. Không dùng cổng XOR chuyên dụng.

```text
                    ALT chọn Q2 hoặc Q1
                              ↓
Q3 ────────────────→ [XOR dựng từ AND/OR/NOT] ──┐
Q0..Q3 ────────────→ [phát hiện 0000] ──────────┤ OR → D0
LOAD ──────────────→ [nạp đồng bộ] ─────────────┘
CLK ───────────────→ chung bốn D-FF: Q0 → Q1 → Q2 → Q3
```

Với `Z=¬Q0·¬Q1·¬Q2·¬Q3`, `T=¬ALT·Q2+ALT·Q1`, `F=(Q3⊕T)+Z`: `D0=LOAD+¬LOAD·F`, `D1=¬LOAD·Q0`, `D2=¬LOAD·Q1`, `D3=¬LOAD·Q2`. LOAD=1 nạp seed Q0Q1Q2Q3=1000 tại cạnh lên; sau đó đưa LOAD về 0 để chạy. CLK, LOAD, ALT là ba công tắc từ trên xuống, ALT mặc định 0. Mỗi LED Q0–Q3 có điện trở 330 Ω, công tắc có pull-down 10 kΩ.

Thứ tự chuỗi trong tài liệu là **Q0Q1Q2Q3**, Q0 bên trái. Với quy ước chuỗi thời gian q0(t+4)=q0(t+1)⊕q0(t), ALT=0 có đa thức đặc trưng `x⁴+x+1`; nếu đảo quy ước thứ tự có thể ghi đa thức nghịch đảo `x⁴+x³+1`. ALT=1 tương ứng `x⁴+x²+1`. Công thức nêu trên là định nghĩa cụ thể của tap để tránh nhầm khi đổi thứ tự bit.

<div style="page-break-before: always"></div>

## Chu kỳ 15 trạng thái, ALT=0

| Bước | Q0Q1Q2Q3 | Bước | Q0Q1Q2Q3 |
|:-:|:---:|:-:|:---:|
| 0 | 1000 | 8 | 1010 |
| 1 | 0100 | 9 | 1101 |
| 2 | 0010 | 10 | 1110 |
| 3 | 1001 | 11 | 1111 |
| 4 | 1100 | 12 | 0111 |
| 5 | 0110 | 13 | 0011 |
| 6 | 1011 | 14 | 0001 |
| 7 | 0101 | 15 | 1000 (lặp) |

Chu kỳ có 15 trạng thái khác nhau, không chứa 0000. ALT=1 từ cùng seed có chu kỳ ngắn hơn: `1000 → 0100 → 1010 → 0101 → 0010 → 0001 → 1000` (6 trạng thái).

## Trạng thái 0 và khởi tạo

LFSR XOR thuần không có Z bị mắc tại 0000 vì phản hồi bằng 0. Ở mạch này, Z=1 chỉ khi 0000 và đưa D0 lên 1 nên cạnh kế tiếp đưa `0000 → 1000`, với cả hai lựa chọn tap; Z=0 ở tất cả 15 trạng thái khác nên không thay đổi chu kỳ tối đa. LOAD cũng nạp seed 1000 khi có cạnh clock. FF rời không có PRE/CLR: có thể dùng FF phần cứng có preset/reset phù hợp để khởi tạo bất đồng bộ, nhưng phần này không có trong project Velxio và không tương đương LOAD đồng bộ.

## Kiểm chứng và thực tế

Chạy `python tools/gen_c09.py C09-LFSR-4bit/C09-LFSR-4bit.vlx` từ thư mục repo. Script lưu rồi đọc bằng `vlx_extra.Circuit`, kiểm đủ 16 trạng thái × 2 ALT × 2 LOAD = 64 trường hợp cạnh lên, xác nhận thoát 0000, chu kỳ 15 không chứa 0 và chu kỳ tap phụ dài 6. Các trạng thái ban đầu được cấp cho bộ kiểm thử, không khẳng định trạng thái khởi động của FF trong Velxio hay phần cứng. Khi lắp thật cần khởi tạo, chống dội clock, đảm bảo setup/hold và xét trễ cổng phản hồi. Chưa chạy Velxio hoặc quay video.
