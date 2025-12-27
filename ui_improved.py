# ui_final3.py

import os, io, threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

# ─── 백그라운드로 무거운 모듈 미리 로드 ─────────────────
def _preload():
    import PyPDF2, fitz
    from PIL import Image, ImageTk

threading.Thread(target=_preload, daemon=True).start()

# ─── 전역 변수 및 유틸 ─────────────────────────────────────
odd_pdf_path = None
even_pdf_path = None

def filename_only(p):
    return os.path.basename(p) if p else "선택되지 않음"

def try_preview():
    if odd_pdf_path and even_pdf_path:
        preview_merged()

# ─── 파일 클릭/드롭 콜백 ────────────────────────────────────
def click_odd(event):
    global odd_pdf_path
    p = filedialog.askopenfilename(title="홀수 PDF 선택", filetypes=[("PDF","*.pdf")])
    if p:
        odd_pdf_path = p
        lbl_odd.configure(text=f"홀수 파일: {filename_only(p)}")
        try_preview()

def click_even(event):
    global even_pdf_path
    p = filedialog.askopenfilename(title="짝수 PDF 선택", filetypes=[("PDF","*.pdf")])
    if p:
        even_pdf_path = p
        lbl_even.configure(text=f"짝수 파일: {filename_only(p)}")
        try_preview()

def drop_odd(event):
    global odd_pdf_path
    p = event.data.strip("{}")
    odd_pdf_path = p
    lbl_odd.configure(text=f"홀수 파일: {filename_only(p)}")
    try_preview()

def drop_even(event):
    global even_pdf_path
    p = event.data.strip("{}")
    even_pdf_path = p
    lbl_even.configure(text=f"짝수 파일: {filename_only(p)}")
    try_preview()

# ─── 홀/짝 교체 기능 ─────────────────────────────────────
def swap_files():
    global odd_pdf_path, even_pdf_path
    odd_pdf_path, even_pdf_path = even_pdf_path, odd_pdf_path
    lbl_odd.configure(text=f"홀수 파일: {filename_only(odd_pdf_path)}")
    lbl_even.configure(text=f"짝수 파일: {filename_only(even_pdf_path)}")
    try_preview()

# ─── 미리보기: 스크롤 프레임에 썸네일로 나열 ──────────────
#    창 높이에 맞춰 스케일을 계산합니다.
_preview_after_id = None
def preview_merged(scale_override=None):
    import PyPDF2, fitz
    from PIL import Image, ImageTk

    # 기존 썸네일 초기화
    for w in scroll_frame.winfo_children():
        w.destroy()

    # 병합
    r1 = PyPDF2.PdfReader(open(odd_pdf_path, "rb"))
    r2 = PyPDF2.PdfReader(open(even_pdf_path, "rb"))
    if len(r1.pages) != len(r2.pages):
        messagebox.showerror("Error", "페이지 수가 일치하지 않습니다.")
        return

    writer = PyPDF2.PdfWriter()
    n = len(r1.pages)
    for i in range(n):
        writer.add_page(r1.pages[i])
        writer.add_page(r2.pages[n - i - 1])
    buf = io.BytesIO(); writer.write(buf); buf.seek(0)

    doc = fitz.open(stream=buf.read(), filetype="pdf")

    # 스케일 계산: 스크롤 프레임 높이에 맞춰
    frame_h = scroll_frame.winfo_height()
    # PDF 페이지 실제 높이 (포인트 단위)
    page_rect = doc.load_page(0).mediabox  # mediabox.height
    pdf_pt_h = page_rect.height
    # 원하는 픽셀 높이: frame_h * 0.9 여유 줌
    desired_px_h = frame_h * 0.9
    scale = desired_px_h / pdf_pt_h

    # 썸네일 생성
    for idx in range(doc.page_count):
        page = doc.load_page(idx)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        photo = ImageTk.PhotoImage(img)

        lbl = ctk.CTkLabel(scroll_frame,
                           text=f"Page {idx+1}",
                           image=photo,
                           compound="top")
        lbl.image = photo
        lbl.grid(row=0, column=idx, padx=5, pady=5)

# ─── 창 크기 변경 시 미리보기 재실행 (디바운스) ─────────────
def on_resize(event):
    global _preview_after_id
    if odd_pdf_path and even_pdf_path:
        if _preview_after_id:
            scroll_frame.after_cancel(_preview_after_id)
        _preview_after_id = scroll_frame.after(300, preview_merged)

# ─── 병합 후 저장 ─────────────────────────────────────────
def merge_and_save():
    import PyPDF2
    if not odd_pdf_path or not even_pdf_path:
        messagebox.showerror("Error", "두 파일을 모두 선택하세요.")
        return

    outp = filedialog.asksaveasfilename(
        title="병합된 PDF 저장",
        defaultextension=".pdf",
        filetypes=[("PDF","*.pdf")])
    if not outp:
        return

    r1 = PyPDF2.PdfReader(open(odd_pdf_path, "rb"))
    r2 = PyPDF2.PdfReader(open(even_pdf_path, "rb"))
    writer = PyPDF2.PdfWriter()
    for i in range(len(r1.pages)):
        writer.add_page(r1.pages[i])
        writer.add_page(r2.pages[len(r1.pages)-i-1])
    with open(outp, "wb") as f:
        writer.write(f)

    messagebox.showinfo("완료", f"저장됨:\n{outp}")

# ─── UI 세팅 ─────────────────────────────────────────────
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = TkinterDnD.Tk()
app.title("MEOW PDF MERGER")
app.geometry("900x600")
app.resizable(True, True)

# 왼쪽 컨트롤
left = ctk.CTkFrame(app)
left.pack(side="left", fill="y", padx=20, pady=20)

ctk.CTkLabel(left, text="PDF MERGER", font=("Helvetica", 20)).pack(pady=(0,20))

# 홀수용 drop zone & click binding
lbl_odd = ctk.CTkLabel(left,
    text="홀수 페이지 PDF를\n드래그하거나 클릭",
    width=200, height=80, fg_color=("#f0f0f0","gray25"))
lbl_odd.pack(pady=10)
lbl_odd.drop_target_register(DND_FILES)
lbl_odd.dnd_bind("<<Drop>>", drop_odd)
lbl_odd.bind("<Button-1>", click_odd)

# 짝수용 drop zone & click binding
lbl_even = ctk.CTkLabel(left,
    text="짝수 페이지 PDF를\n드래그하거나 클릭",
    width=200, height=80, fg_color=("#f0f0f0","gray25"))
lbl_even.pack(pady=10)
lbl_even.drop_target_register(DND_FILES)
lbl_even.dnd_bind("<<Drop>>", drop_even)
lbl_even.bind("<Button-1>", click_even)

# 교체 & 저장 버튼
btn_opts = dict(width=200, corner_radius=8, fg_color="#1E90FF")
ctk.CTkButton(left, text="홀짝 파일 바꾸기", command=swap_files, **btn_opts).pack(pady=10)
ctk.CTkButton(left, text="병합 후 저장",   command=merge_and_save, **btn_opts).pack(pady=20)

# 오른쪽: 썸네일 미리보기 (가로 스크롤, 크기 자동 조정)
scroll_frame = ctk.CTkScrollableFrame(app, orientation="horizontal")
scroll_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
scroll_frame.bind("<Configure>", on_resize)

app.mainloop()
