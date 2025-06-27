import tkinter as tk
from api_client import APIClient
from app_pages import HomePage, ChatPage, MultiAgentPage, CodeGenPage
from sensitive_word_filter import SensitiveWordFilter

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("（多模态）大语言模型应用开发")
        self.geometry("800x600")

        try:
            # 实例化API客户端
            self.api_client = APIClient()
        except ValueError:
            # 如果API密钥未找到，则退出应用
            self.destroy()
            return

        self.sensitive_filter = SensitiveWordFilter()  # 创建敏感词过滤器实例

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, ChatPage, MultiAgentPage, CodeGenPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.status_bar = tk.Label(self, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.show_home_page()

    def show_frame(self, page_name):
        """将指定名称的页面显示在最上层。"""
        frame = self.frames[page_name]
        frame.tkraise()

    def show_home_page(self):
        """显示主页。"""
        self.show_frame("HomePage")

    def show_chat_page(self):
        """显示普通对话页面。"""
        self.show_frame("ChatPage")

    def show_multi_agent_page(self):
        """显示Multi-Agent页面。"""
        self.show_frame("MultiAgentPage")

    def show_code_gen_page(self):
        """显示代码生成页面。"""
        self.show_frame("CodeGenPage")

    def set_status(self, message):
        """更新状态栏的文本。"""
        self.status_bar.config(text=message)
        self.update_idletasks()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()    
