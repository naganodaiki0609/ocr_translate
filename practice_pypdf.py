from pdf2image import convert_from_path
import pytesseract
from googletrans import Translator
from pypdf import PdfWriter
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.cidfonts import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from deep_translator import GoogleTranslator


def paginate_lines(lines, lines_per_page):
    """指定行数ごとに分割"""
    for i in range(0, len(lines), lines_per_page):
        yield lines[i : i + lines_per_page]


c = Canvas("./output.pdf", pagesize=A4)
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

images = convert_from_path(
    "/Users/naganodaiki/Desktop/中央大学理工英語/2024.pdf", dpi=300
)
writer = PdfWriter()

full_text = ""
for i, image in enumerate(images):
    if i == 1 or i > 6:
        continue
    full_text += pytesseract.image_to_string(image, lang="eng+jpn") + "\n"

# 2. 翻訳（全文を一括で）
# translator = Translator()
translated_text = GoogleTranslator(source="en", target="ja").translate(full_text)

# 3. 改行単位で処理
lines = translated_text.splitlines()
lines_per_page = 40  # 1ページに収める最大行数
line_height = 18  # 行間
margin_top = 800  # 開始Y位置
margin_left = 40  # 開始X位置

# 4. ページ単位で描画
for chunk in paginate_lines(lines, lines_per_page):
    text_object = c.beginText()
    text_object.setFont("HeiseiKakuGo-W5", 14)
    text_object.setTextOrigin(margin_left, margin_top)
    text_object.setLeading(line_height)

    for line in chunk:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()

# for i, text in enumerate(images):
#     if i == 1 or i > 6:
#         continue
#     else:
#         text = pytesseract.image_to_string(text, lang="eng+jpn")
#         translator = Translator()
#         translated = translator.translate(text, src="en", dest="ja").text
#         translated = text
#         text_object = c.beginText()
#         text_object.setFont("HeiseiKakuGo-W5", 10)
#         text_object.setTextOrigin(40, 800)
#         for line in translated.splitlines():
#             text_object.textLine(line)
#         c.drawText(text_object)
#         c.showPage()

#         # writer.add_page(text)
#         # writer.add_page(translated)
#         print(f"原文の{i+1}ページ:{text}")
#         print(f"翻訳の{i+1}ページ:{translated}")

c.save()
