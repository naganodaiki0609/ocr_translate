from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from pdf2image import convert_from_path
from pytesseract import image_to_string
from deep_translator import GoogleTranslator
from reportlab.lib.utils import simpleSplit
import re
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
from deep_translator import DeeplTranslator


# 段落ごとに翻訳し、翻訳結果を句点（。）で分割して文単位に整形
def translate_by_paragraph(text):
    paragraphs = re.split(r"\n\s*\n", text)
    translated_paragraphs = []
    api_key = os.getenv("DEEPL_API_KEY")

    if not api_key:
        # 環境変数が設定されていない場合は、エラーメッセージを表示して処理を中断する
        raise ValueError("環境変数 'DEEPL_API_KEY' が設定されていません。")

    # translator = GoogleTranslator(source="en", target="ja")
    translator = DeeplTranslator(
        api_key=api_key, source="en", target="ja", use_free_api=True
    )
    for i, para in enumerate(paragraphs):
        para = para.strip().replace("\n", " ")
        if not para:
            continue
        try:
            print(f"[{para}]")  # デバッグ表示
            print("--- APIに送信する英文 ---")
            print(para)
            print("-------------------------")
            translated = translator.translate(para)
            if translated:  # 翻訳結果がNoneや空でないことを確認
                translated_paragraphs.append(translated)

            print(f"--- APIからの翻訳結果 ---\n{translated}\n-------------------------")
            # sentences = [s.strip() for s in translated.split("。") if s.strip()]
            # translated_sentences.extend([s + "。" for s in sentences])
        except Exception as e:
            print(f"⚠️ 翻訳失敗: {e}")
            translated_paragraphs.append(para)

    return translated_paragraphs


def clean_ocr_text(text):
    lines = text.splitlines()
    cleaned_lines = []

    previous_line_was_empty = False  # 前の行が空行だったかを記録

    for line in lines:
        stripped_line = line.strip()

        # もし空行（空白のみの行も含む）なら
        if not stripped_line:
            # 連続する空行は一つにまとめる
            if not previous_line_was_empty:
                cleaned_lines.append("")  # 最初の空行だけ追加
            previous_line_was_empty = True
            continue

        # 空行でなかった場合
        previous_line_was_empty = False

        # 以下は元のクリーニングロジック
        # 文字化け・ゴミ判定（英字が含まれていない行）
        # この行は、英語PDFの場合、タイトルやセクション名など、数字や記号のみの行を除去してしまう可能性があるので注意
        # 必要に応じて調整してください。今回は一旦コメントアウトのままで良いでしょう
        # if re.match(r"^[^a-zA-Z]*$", stripped_line):
        #     continue

        # 選択肢 (7) A. B. C. D. のようなもの
        if re.match(r"^\(?\d+\)?\s*[A-D]\.", stripped_line):
            continue

        # 無意味な記号列
        if re.search(r"[=◆→★■※●○□◎✕✖]", stripped_line):
            continue

        # 複数のスペースを1つにまとめる
        cleaned_lines.append(re.sub(r"\s+", " ", stripped_line))

    # 最後に、テキストの冒頭や末尾に不要な空行が続く場合は除去することも検討
    # 例えば、最初の行が空行で始まる場合は削除
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    # 最後の行が空行で終わる場合も削除
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop(-1)

    return "\n".join(cleaned_lines)


# PDFの出力設定
def output_translated_pdf(translated_lines, output_path="output.pdf"):
    c = Canvas(output_path, pagesize=A4)
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    width, height = A4
    margin_left = 60
    margin_top = height - 60
    line_height = 16
    max_width = width - 2 * margin_left
    font_name = "HeiseiKakuGo-W5"
    font_size = 9

    lines_on_page = 0
    text_obj = c.beginText(margin_left, margin_top)
    text_obj.setFont(font_name, font_size)

    for line in translated_lines:
        wrapped_lines = wrap_text_japanese(line, font_name, font_size, max_width)

        for wrap in wrapped_lines:
            text_obj.textLine(wrap)
            lines_on_page += 1
            if lines_on_page >= int((height - 100) / line_height):
                c.drawText(text_obj)
                c.showPage()
                text_obj = c.beginText(margin_left, margin_top)
                text_obj.setFont(font_name, font_size)
                lines_on_page = 0

    c.drawText(text_obj)
    c.save()
    print(f"✅ PDF出力完了: {output_path}")


# OCR対象PDFの読み取り（2～5ページを抽出）
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    full_text = ""
    for i, image in enumerate(images):
        if 1 < i:
            full_text += image_to_string(image, lang="eng")
    return full_text


def wrap_text_japanese(text, font_name, font_size, max_width):
    lines = []
    buffer = ""
    for char in text:
        buffer += char
        if stringWidth(buffer, font_name, font_size) > max_width:
            lines.append(buffer)
            buffer = ""
    if buffer:
        lines.append(buffer)
    return lines


# 実行部分（パスは環境に合わせて修正）
pdf_path = (
    "/Users/naganodaiki/Desktop/英語過去問題/東京理科大学総域理工英語/2024_den.pdf"
)
raw_text = extract_text_from_pdf(pdf_path)
clean_text = clean_ocr_text(raw_text)
translated_lines = translate_by_paragraph(clean_text)
print("日本語", translated_lines)
output_translated_pdf(translated_lines)
