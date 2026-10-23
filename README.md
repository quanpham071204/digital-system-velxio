# 30 Bài Thử Thách Digital System – Velxio

**Sinh viên:** Phạm Anh Quân – MSSV 2353011 · **Môn:** ĐATKLL – HCMUT
**Trình mô phỏng:** [Velxio](https://velxio.dev/editor/) (không lắp breadboard)

## Tiến độ

| Bài | Nội dung | Nhóm | Project | Báo cáo |
|---|---|---|---|---|
| [B01](B01-kiem-tra-IC/) | Kiểm tra IC 74HC00/02/04/08/32/86 | 1 | [.vlx](B01-kiem-tra-IC/B01-kiem-tra-IC.vlx) | [MD](B01-kiem-tra-IC/README.md) · [PDF](B01-kiem-tra-IC/B01-kiem-tra-IC.pdf) |
| [B02](B02-NAND-van-nang/) | NAND là cổng vạn năng | 1 | [.vlx](B02-NAND-van-nang/B02-NAND-van-nang.vlx) | [MD](B02-NAND-van-nang/README.md) · [PDF](B02-NAND-van-nang/B02-NAND-van-nang.pdf) |
| [B03](B03-NOR-van-nang/) | NOR là cổng vạn năng | 1 | [.vlx](B03-NOR-van-nang/B03-NOR-van-nang.vlx) | [MD](B03-NOR-van-nang/README.md) · [PDF](B03-NOR-van-nang/B03-NOR-van-nang.pdf) |
| B04 | Schmitt trigger: clock và chống dội | 1 | ⬜ | ⬜ |
| B05 | Tạo/kiểm tra bit chẵn lẻ 4 bit | 1 | ⬜ | ⬜ |
| B06 | Biểu quyết đa số 3 người | 2 | ⬜ | ⬜ |
| B07 | So sánh độ lớn 2 bit | 2 | ⬜ | ⬜ |
| B08 | D Flip-Flop: chốt dữ liệu, chia tần | 2 | ⬜ | ⬜ |
| B09 | JK Flip-Flop: 4 chế độ | 2 | ⬜ | ⬜ |
| B10 | T Flip-Flop, bộ đếm gợn 3 bit | 2 | ⬜ | ⬜ |
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
├── vlx.py             # thư viện dùng chung: nguồn, công tắc, LED, IC, cổng
├── gen_bxx.py         # sinh file .vlx (tái tạo mạch tự động)
├── build_pdf.sh       # README.md → PDF (pandoc + Chromium)
└── report.css         # định dạng PDF
```

## Cách dùng

**Mở project:** vào https://velxio.dev/editor/ → **File → Open project…** → chọn file `.vlx` → click công tắc trên canvas để đổi ngõ vào.

**Tạo lại project:**
```bash
python3 tools/gen_b01.py B01-kiem-tra-IC/B01-kiem-tra-IC.vlx
python3 tools/gen_b02.py B02-NAND-van-nang/B02-NAND-van-nang.vlx   # tương tự cho các bài khác
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
- id của LED phải viết thường (ngspice đổi tên nút sang chữ thường, LED có id chữ hoa không bao giờ sáng).
- Không dùng chung IC 74HC với Flip-Flop/cổng cơ bản trong cùng một mạch (quy định của đề).
