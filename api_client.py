import os
from dotenv import load_dotenv
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox


class APIClient:
    def __init__(self):
        """初始化OpenAI API客户端。"""
        load_dotenv()
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")

        if not api_key:
            messagebox.showerror("API密钥错误", "请在您的 .env 文件中设置 SILICONFLOW_API_KEY。")
            raise ValueError("未找到API密钥")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

    def get_response_stream(self, messages, temperature=0.7, stop_event=None):
        """
        从聊天API获取流式响应。
        通过yield逐块返回响应内容。
        新增：stop_event参数，用于从外部中断数据流。
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=temperature
            )
            for chunk in stream:
                # 在返回每一块数据前，检查停止信号是否被设置
                if stop_event and stop_event.is_set():
                    # 如果信号被设置，则跳出循环，停止发送数据
                    break

                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # 仅在未被用户主动停止时才显示API错误
            if not (stop_event and stop_event.is_set()):
                messagebox.showerror("API错误", f"调用API时发生错误: {str(e)}")
                yield f"\n[错误] {str(e)}"