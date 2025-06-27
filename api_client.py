import os
from dotenv import load_dotenv
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox

class APIClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")

        if not api_key:
            messagebox.showerror("API密钥错误", "请在您的 .env 文件中设置 SILICONFLOW_API_KEY。")
            raise ValueError("未找到API密钥")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

    def get_response_stream(self, messages, temperature=0.7, stop_event=None):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=temperature
            )
            for chunk in stream:
                if stop_event and stop_event.is_set():
                    break

                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            if not (stop_event and stop_event.is_set()):
                messagebox.showerror("API错误", f"调用API时发生错误: {str(e)}")
                yield f"\n[错误] {str(e)}"
