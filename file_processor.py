import base64
from pathlib import Path

def encode_image_to_base64(image_path):
    """将图片文件编码为 base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_file(file_path):
    """从文本文件中提取内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()