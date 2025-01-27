
from .models import *
def intcomma(number):
    """
    Функция для форматирования целых чисел с добавлением запятых как разделителя разрядов.
    
    Args:
        number (int): Целое число для форматирования.
    
    Returns:
        str: Отформатированная строка с добавлением запятых как разделителя разрядов.
    """
    parts = []
    for i, digit in enumerate(reversed(str(number))):
        if i > 0 and i % 3 == 0:
            parts.append(' ')
        parts.append(digit)
    return ''.join(reversed(parts))

import fitz  # PyMuPDF
from PIL import Image
import io

def extract_pdf_thumbnail(file_path, output_path):
    try:
        doc = fitz.open(file_path)
        page = doc[0]  # Первая страница
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")

        # Открываем изображение и меняем размер
        image = Image.open(io.BytesIO(img_data))
        image = image.resize((140, 181))  # Размер 140x181
        image.save(output_path)
        return output_path
    except Exception as e:
        print(f"Ошибка извлечения изображения из PDF: {e}")
        return None

from docx import Document
from PIL import Image, ImageDraw

def extract_docx_thumbnail(file_path, output_path):
    try:
        doc = Document(file_path)
        text = '\n'.join([p.text for p in doc.paragraphs[:10]])  # Извлекаем первые 10 строк

        # Создаем изображение и меняем размер
        img = Image.new("RGB", (140, 181), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Добавляем текст
        draw.text((10, 10), text, fill=(0, 0, 0))

        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Ошибка извлечения изображения из Word: {e}")
        return None
