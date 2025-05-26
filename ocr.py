from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from pdf2image import convert_from_path
from pytesseract import image_to_string
from deep_translator import GoogleTranslator
from reportlab.lib.utils import simpleSplit


# 翻訳（ピリオド区切りで分割翻訳）
def translate_by_line(text):
    count = 0
    translated_lines = []
    lines = []
    # 改行をすべてスペースに置換
    text = text.replace("\n", " ")
    for line in text.split("."):
        line = line.strip()
        if not line:
            continue
        try:
            print("count", count, line)
            lines.append(line)
            translated = GoogleTranslator(source="en", target="ja").translate(line)
            translated_lines.append(translated)
            count += 1
        except Exception as e:
            print(f"⚠️ 翻訳失敗: {e}")
            translated_lines.append(line)

    print(lines)
    return translated_lines


# PDF準備
c = Canvas("output.pdf", pagesize=A4)
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

# OCR対象PDF
images = convert_from_path(
    "/Users/naganodaiki/Desktop/中央大学理工英語/2024.pdf", dpi=300
)

# OCR対象ページ（2～5）
full_text = ""
for i, image in enumerate(images):
    if 1 < i <= 5:
        full_text += image_to_string(image, lang="eng")

# 翻訳
translated_lines = translate_by_line(full_text)

# ページ設定
width, height = A4
margin_left = 60
margin_top = height - 60
line_height = 16
max_width = width - 2 * margin_left
font_name = "HeiseiKakuGo-W5"
font_size = 9

# 出力処理（自動折返し対応）
lines_on_page = 0
text_obj = c.beginText(margin_left, margin_top)
text_obj.setFont(font_name, font_size)

for line in translated_lines:
    wrapped_lines = simpleSplit(line, font_name, font_size, max_width)
    for wrap in wrapped_lines:
        text_obj.textLine(wrap)
        lines_on_page += 1
        if lines_on_page >= int((height - 100) / line_height):
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(margin_left, margin_top)
            text_obj.setFont(font_name, font_size)
            lines_on_page = 0

# 最後のページを描画
c.drawText(text_obj)
c.save()
print("✅ 出力完了（文字切れ対策済）: output.pdf")
