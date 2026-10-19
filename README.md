# 30 Bài Thử Thách Digital System – Velxio

**Sinh viên:** Phạm Anh Quân – MSSV 2353011 · **Môn:** ĐATKLL – HCMUT
**Trình mô phỏng:** [Velxio](https://velxio.dev/editor/) (không lắp breadboard)

## Tiến độ

| Bài | Nội dung | Nhóm | Project | Báo cáo |
|---|---|---|---|---|
| [B01](B01-kiem-tra-IC/) | Kiểm tra IC 74HC00/02/04/08/32/86 | 1 | [.vlx](B01-kiem-tra-IC/B01-kiem-tra-IC.vlx) | [MD](B01-kiem-tra-IC/README.md) · [PDF](B01-kiem-tra-IC/B01-kiem-tra-IC.pdf) |
| B02 | NAND là cổng vạn năng | 1 | ⬜ | ⬜ |
| B03 – B05 | NOR vạn năng, Schmitt, parity | 1 | ⬜ | ⬜ |
| B06 – B10 | Biểu quyết, so sánh, D/JK/T FF, ripple counter | 2 | ⬜ | ⬜ |
| C01 – C10 | Kết hợp | 1 / 2 | ⬜ | ⬜ |
| A01 – A10 | Ứng dụng (chọn 2–3 bài) | 2 | ⬜ | ⬜ |

## Cấu trúc

```
Bxx-ten-bai/
├── README.md          # báo cáo: lý thuyết, thiết kế, kết quả, khác biệt mô phỏng/thực tế
├── Bxx-ten-bai.pdf    # báo cáo xuất PDF để nộp
├── Bxx-ten-bai.vlx    # project Velxio
└── img/               # ảnh chụp canvas, giản đồ thời gian
tools/
├── gen_bxx.py         # sinh file .vlx (tái tạo mạch tự động)
├── build_pdf.sh       # README.md → PDF (pandoc + Chromium)
└── report.css         # định dạng PDF
```

## Cách dùng

**Mở project:** vào https://velxio.dev/editor/ → **File → Open project…** → chọn file `.vlx` → click công tắc trên canvas để đổi ngõ vào.

**Tạo lại project:**
```bash
python3 tools/gen_b01.py B01-kiem-tra-IC/B01-kiem-tra-IC.vlx
```

**Xuất PDF:**
```bash
tools/build_pdf.sh B01-kiem-tra-IC
```

## Nộp bài

Theo đề, mỗi bài nộp **báo cáo** (đủ các mục trong "Tiêu chí hoàn thành") **và project mô phỏng** (link chia sẻ hoặc file xuất từ Velxio) để giảng viên chạy lại. Mỗi bài trong repo đã có sẵn `.pdf` và `.vlx`.

## Lưu ý về Velxio

- Không nối dây vào chân `VCC` của IC 74HC: Velxio tự cấp 5 V, nối thêm nguồn sẽ gây lỗi SPICE `singular matrix`.
- 74HC02 trong Velxio dùng sơ đồ chân giống 74HC00 (khác IC thật).
- Signal Generator không làm clock cho Flip-Flop được (SPICE không phát hiện cạnh). Dùng công tắc hoặc nút nhấn làm clock tay.
- Flip-Flop của Velxio không có chân PRE/CLR.
- Không dùng chung IC 74HC với Flip-Flop/cổng cơ bản trong cùng một mạch (quy định của đề).
