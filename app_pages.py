import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import json
import os
from memory import ConversationMemory
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import base64
from file_processor import extract_text_from_file  # 仅保留文件处理功能

class SensitiveWordFilter:
    """敏感词过滤类，负责加载、管理和过滤敏感词"""
    
    def __init__(self, file_path="sensitive_words.json"):
        self.file_path = file_path
        self.sensitive_words = self.load_sensitive_words()
        
    def load_sensitive_words(self):
        """从文件加载敏感词库"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            # 如果文件不存在，返回默认敏感词库
            return ["色情", "毒品", "傻逼"]
        except Exception as e:
            print(f"加载敏感词库失败: {e}")
            return []
            
    def save_sensitive_words(self):
        """保存敏感词库到文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.sensitive_words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存敏感词库失败: {e}")
            
    def add_sensitive_word(self, word):
        """添加敏感词"""
        if word and word not in self.sensitive_words:
            self.sensitive_words.append(word)
            self.save_sensitive_words()
            return True
        return False
        
    def remove_sensitive_word(self, word):
        """移除敏感词"""
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            self.save_sensitive_words()
            return True
        return False
        
    def filter_text(self, text):
        """过滤文本中的敏感词，返回过滤后的文本和是否包含敏感词的标志"""
        contains_sensitive = False
        filtered_text = text
        
        for word in self.sensitive_words:
            if word in filtered_text:
                contains_sensitive = True
                filtered_text = filtered_text.replace(word, '*' * len(word))
                
        return filtered_text, contains_sensitive


class BasePage(tk.Frame):
    """所有页面的基类，包含共享的控件和元素。"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sensitive_filter = controller.sensitive_filter  # 获取敏感词过滤器实例

        # --- 顶部控制栏 ---
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, pady=5, padx=10)

        self.back_button = tk.Button(top_frame, text="返回主页", command=self.controller.show_home_page)
        self.back_button.pack(side=tk.LEFT)
        
        # 添加敏感词库按钮
        self.sensitive_btn = tk.Button(top_frame, text="敏感词库", command=self.open_sensitive_words_manager)
        self.sensitive_btn.pack(side=tk.LEFT, padx=5)

        temp_frame = tk.Frame(top_frame)
        tk.Label(temp_frame, text="输出确定性:").pack(side=tk.LEFT)
        self.temp_var = tk.StringVar(value="medium")
        temp_options = [("高", "low"), ("中", "medium"), ("低", "high")]
        for text, value in temp_options:
            tk.Radiobutton(temp_frame, text=text, variable=self.temp_var, value=value).pack(side=tk.LEFT)
        temp_frame.pack(side=tk.RIGHT)

    def get_temperature(self):
        """将GUI上的选项映射为具体的temperature数值。"""
        mapping = {"low": 0.2, "medium": 0.7, "high": 1.2}
        return mapping.get(self.temp_var.get(), 0.7)
        
    def open_sensitive_words_manager(self):
        """打开敏感词管理窗口"""
        SensitiveWordsManager(self, self.sensitive_filter)


class SensitiveWordsManager:
    """敏感词管理窗口类"""
    
    def __init__(self, parent, sensitive_filter):
        self.parent = parent
        self.sensitive_filter = sensitive_filter
        
        # 创建顶级窗口
        self.window = tk.Toplevel(parent)
        self.window.title("敏感词库管理")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # 创建框架
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 敏感词列表
        tk.Label(frame, text="当前敏感词库:").pack(anchor=tk.W)
        
        self.word_listbox = tk.Listbox(frame, width=40, height=10)
        self.word_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.word_listbox, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.word_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.word_listbox.yview)
        
        # 刷新敏感词列表
        self.refresh_word_list()
        
        # 添加敏感词
        add_frame = tk.Frame(frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(add_frame, text="添加敏感词:").pack(side=tk.LEFT)
        self.add_entry = tk.Entry(add_frame, width=20)
        self.add_entry.pack(side=tk.LEFT, padx=5)
        self.add_btn = tk.Button(add_frame, text="添加", command=self.add_word)
        self.add_btn.pack(side=tk.LEFT)
        
        # 删除敏感词
        delete_frame = tk.Frame(frame)
        delete_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(delete_frame, text="删除敏感词:").pack(side=tk.LEFT)
        self.delete_entry = tk.Entry(delete_frame, width=20)
        self.delete_entry.pack(side=tk.LEFT, padx=5)
        self.delete_btn = tk.Button(delete_frame, text="删除", command=self.delete_word)
        self.delete_btn.pack(side=tk.LEFT)
        
        # 批量导入/导出
        batch_frame = tk.Frame(frame)
        batch_frame.pack(fill=tk.X, pady=5)
        
        self.import_btn = tk.Button(batch_frame, text="导入敏感词库", command=self.import_words)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(batch_frame, text="导出敏感词库", command=self.export_words)
        self.export_btn.pack(side=tk.LEFT)
        
    def refresh_word_list(self):
        """刷新敏感词列表"""
        self.word_listbox.delete(0, tk.END)
        for word in self.sensitive_filter.sensitive_words:
            self.word_listbox.insert(tk.END, word)
            
    def add_word(self):
        """添加敏感词"""
        word = self.add_entry.get().strip()
        if not word:
            messagebox.showwarning("警告", "请输入敏感词!")
            return
            
        if self.sensitive_filter.add_sensitive_word(word):
            self.refresh_word_list()
            messagebox.showinfo("成功", f"已添加敏感词: {word}")
        else:
            messagebox.showwarning("警告", f"敏感词 '{word}' 已存在!")
            
        self.add_entry.delete(0, tk.END)
        
    def delete_word(self):
        """删除敏感词"""
        word = self.delete_entry.get().strip()
        if not word:
            messagebox.showwarning("警告", "请输入敏感词!")
            return
            
        if self.sensitive_filter.remove_sensitive_word(word):
            self.refresh_word_list()
            messagebox.showinfo("成功", f"已删除敏感词: {word}")
        else:
            messagebox.showwarning("警告", f"敏感词 '{word}' 不存在!")
            
        self.delete_entry.delete(0, tk.END)
        
    def import_words(self):
        """导入敏感词库"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    words = json.load(f)
                else:
                    words = [line.strip() for line in f if line.strip()]
                    
            # 添加到敏感词库
            added_count = 0
            for word in words:
                if self.sensitive_filter.add_sensitive_word(word):
                    added_count += 1
                    
            self.refresh_word_list()
            messagebox.showinfo("成功", f"已从文件导入 {added_count} 个敏感词")
        except Exception as e:
            messagebox.showerror("错误", f"导入敏感词库失败: {str(e)}")
            
    def export_words(self):
        """导出敏感词库"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(self.sensitive_filter.sensitive_words, f, ensure_ascii=False, indent=2)
                else:
                    f.write('\n'.join(self.sensitive_filter.sensitive_words))
                    
            messagebox.showinfo("成功", f"已导出 {len(self.sensitive_filter.sensitive_words)} 个敏感词到文件")
        except Exception as e:
            messagebox.showerror("错误", f"导出敏感词库失败: {str(e)}")


class HomePage(tk.Frame):
    """应用的主页面。"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="请选择一个功能", font=("微软雅黑", 16)).pack(pady=20)
        tk.Button(self, text="普通对话", command=self.controller.show_chat_page, width=20, height=2).pack(pady=10)
        tk.Button(self, text="Multi-Agent", command=self.controller.show_multi_agent_page, width=20, height=2).pack(
            pady=10)
        tk.Button(self, text="代码生成", command=self.controller.show_code_gen_page, width=20, height=2).pack(pady=10)


class ChatPage(BasePage):
    """用于普通对话的页面，带有记忆功能。"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.stop_event = None
        self.memory = ConversationMemory()
        self.attachments = []  # 存储附件信息
        
        # 历史对话管理框架 - 单行布局
        history_frame = tk.Frame(self)
        history_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # 历史对话下拉框 (左侧)
        tk.Label(history_frame, text="历史对话:").pack(side=tk.LEFT)
        self.conversation_var = tk.StringVar()
        self.conversation_dropdown = ttk.Combobox(
            history_frame, 
            textvariable=self.conversation_var,
            state="readonly",
            width=30
        )
        self.conversation_dropdown.pack(side=tk.LEFT, padx=5)
        self.conversation_dropdown.bind("<<ComboboxSelected>>", self.load_selected_conversation)
        
        # 新对话按钮 (中间)
        self.new_conversation_btn = tk.Button(
            history_frame, 
            text="新对话", 
            command=self.start_new_conversation,
            bg="white",
            fg="black",
            width=8
        )
        self.new_conversation_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮 (中间)
        self.delete_btn = tk.Button(
            history_frame, 
            text="删除", 
            command=self.delete_conversation,
            width=8,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮 (右侧)
        self.export_btn = tk.Button(
            history_frame, 
            text="导出为MD", 
            command=self.export_conversation,
            width=8,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT)
        
        # 附件控制按钮 - 放在输入框上方（仅保留文件上传和清除）
        attachment_frame = tk.Frame(self)
        attachment_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.file_button = tk.Button(attachment_frame, text="添加文件", command=self.upload_file)
        self.file_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(attachment_frame, text="全部清除", command=self.clear_attachments)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 显示附件列表的区域
        self.attachments_listbox = tk.Listbox(self, height=2, width=70)
        self.attachments_listbox.pack(pady=2, padx=10, fill=tk.X)
        
        # 对话输入和输出区域
        self.label = tk.Label(self, text="请输入您的问题:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(self, width=70)
        self.entry.pack(pady=5, padx=10, fill=tk.X)
        self.entry.bind("<Return>", lambda event: self.start_response_thread())

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        self.submit_button = tk.Button(button_frame, text="提交", command=self.start_response_thread)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="终止输出", command=self.stop_response, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.output = scrolledtext.ScrolledText(self, width=80, height=20)
        self.output.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        
        # 初始化新对话
        self.start_new_conversation()

    def start_new_conversation(self):
        """开始全新的对话"""
        # 保存当前对话(如果有)
        if hasattr(self, 'current_conversation') and self.current_conversation:
            self.memory.save_conversation()
        
        # 创建新对话
        conv_id = self.memory.start_new_conversation()
        self.current_conversation = conv_id
        self.update_conversation_dropdown()
        self.conversation_var.set(conv_id)
        self.output.delete(1.0, tk.END)  # 清空输出区域，不显示创建提示
        self.entry.focus_set()
        
        # 清空附件
        self.clear_attachments()
        
        # 根据是否有历史对话更新按钮状态
        has_history = bool(self.memory.get_all_conversations())
        self.delete_btn.config(state=tk.NORMAL if has_history else tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL if has_history else tk.DISABLED)

    def update_conversation_dropdown(self):
        """更新对话下拉菜单"""
        conversations = self.memory.get_all_conversations()
        self.conversation_dropdown['values'] = conversations
        if conversations:
            self.delete_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)

    def load_selected_conversation(self, event=None):
        """加载选中的对话"""
        conv_id = self.conversation_var.get()
        if not conv_id:
            return
            
        # 保存当前对话状态
        if hasattr(self, 'current_conversation') and self.current_conversation:
            self.memory.save_conversation()
            
        self.current_conversation = conv_id
        self.output.delete(1.0, tk.END)
        messages = self.memory.get_conversation_history(conv_id)
        
        for msg in messages:
            role = "您" if msg['role'] == "user" else "AI"
            content = msg['content']
            self.output.insert(tk.END, f"{role}: {content}\n\n")
        
        self.output.see(tk.END)
        
        # 清空附件
        self.clear_attachments()

    def delete_conversation(self):
        """删除当前选中的对话"""
        conv_id = self.conversation_var.get()
        if not conv_id:
            return
            
        if messagebox.askyesno("确认删除", f"确定要删除对话 '{conv_id}' 吗？"):
            if self.memory.delete_conversation(conv_id):
                self.update_conversation_dropdown()
                if self.memory.get_all_conversations():
                    # 加载列表中的第一个对话
                    self.conversation_var.set(self.memory.get_all_conversations()[0])
                    self.load_selected_conversation()
                else:
                    # 如果没有对话了，创建新对话
                    self.start_new_conversation()

    def export_conversation(self):
        """导出对话为Markdown文件"""
        conv_id = self.conversation_var.get()
        if not conv_id:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md")],
            initialfile=f"{conv_id}.md"
        )
        
        if file_path:
            if self.memory.export_to_markdown(conv_id, file_path):
                messagebox.showinfo("导出成功", f"对话已成功导出到 {file_path}")
            else:
                messagebox.showerror("导出失败", "无法导出对话")

    def upload_file(self):
        """上传文件附件"""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # 提取文件内容
                content = extract_text_from_file(file_path)
                filename = os.path.basename(file_path)
                
                # 添加到附件列表
                attachment_info = {
                    "type": "file",
                    "filename": filename,
                    "path": file_path,
                    "content": content
                }
                self.attachments.append(attachment_info)
                self.attachments_listbox.insert(tk.END, f"文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法上传文件: {str(e)}")

    def clear_attachments(self):
        """清除所有附件"""
        if self.attachments or self.attachments_listbox.size() > 0:
            if messagebox.askyesno("确认清除", "确定要清除所有附件吗？"):
                self.attachments = []
                self.attachments_listbox.delete(0, tk.END)

    def start_response_thread(self):
        question = self.entry.get()
        if not question and not self.attachments:
            messagebox.showwarning("警告", "请输入问题或添加附件。")
            return

        # 过滤敏感词
        filtered_question, contains_sensitive = self.sensitive_filter.filter_text(question)
        
        if contains_sensitive:
            # 修改：显示过滤后的问题并终止对话
            self.output.insert(tk.END, f"\n\n您: {filtered_question}\nAI: 抱歉，因包含敏感词无法回答。\n")
            self.memory.add_message("user", filtered_question)
            self.memory.add_message("assistant", "抱歉，因包含敏感词无法回答。")
            self.memory.save_conversation()
            self.update_conversation_dropdown()
            self.entry.delete(0, tk.END)
            return

        # 构建包含附件内容的完整问题
        full_question = filtered_question
        
        if self.attachments:
            full_question += "\n\n参考以下附件内容:\n"
            
            for i, attachment in enumerate(self.attachments):
                # 对于文件，提取并添加内容
                full_question += f"\n附件 {i+1}: 文件 '{attachment['filename']}' 的内容:\n"
                # 限制内容长度，避免过长
                content = attachment['content']
                if len(content) > 2000:
                    content = content[:2000] + "..."
                full_question += f"{content}\n"

        self.output.insert(tk.END, f"\n\n您: {full_question}\nAI: ")
        self.memory.add_message("user", full_question)
        self.entry.delete(0, tk.END)

        self.submit_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.get_response, args=(full_question, self.stop_event))
        thread.start()

    def stop_response(self):
        if self.stop_event:
            self.stop_event.set()

    def get_response(self, question, stop_event):
        try:
            self.controller.set_status("正在获取回答...")
            temperature = self.get_temperature()
            
            # 获取对话历史作为上下文
            messages = [{"role": "user" if msg['role'] == "user" else "assistant", 
                         "content": msg['content']} 
                        for msg in self.memory.get_conversation_history()]
            
            response_content = ""
            for content_chunk in self.controller.api_client.get_response_stream(
                messages, temperature, stop_event
            ):
                # 修改：实时过滤AI响应，发现敏感词立即终止
                filtered_chunk, contains_sensitive = self.sensitive_filter.filter_text(content_chunk)
                response_content += filtered_chunk
                self.output.insert(tk.END, filtered_chunk)
                self.output.see(tk.END)
                
                if contains_sensitive:
                    # 修改：发现敏感词时终止输出并提示
                    self.output.insert(tk.END, "\n\n[系统提示] 部分内容包含敏感词，已终止输出。\n")
                    self.output.see(tk.END)
                    stop_event.set()  # 终止API调用
                    break  # 跳出循环
                    
            if not stop_event.is_set():
                self.memory.add_message("assistant", response_content)
                self.memory.save_conversation()
                self.update_conversation_dropdown()
                
        finally:
            status_text = "用户已终止" if stop_event.is_set() else "回答完成"
            self.controller.set_status(status_text)
            self.submit_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


class MultiAgentPage(BasePage):
    """用于Multi-Agent对话的页面。"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.stop_event = None
        self.attachments = []  # 存储附件信息

        # 附件控制按钮 - 放在输入框上方
        attachment_frame = tk.Frame(self)
        attachment_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.file_button = tk.Button(attachment_frame, text="添加文件", command=self.upload_file)
        self.file_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(attachment_frame, text="全部清除", command=self.clear_attachments)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 显示附件列表的区域
        self.attachments_listbox = tk.Listbox(self, height=2, width=70)
        self.attachments_listbox.pack(pady=2, padx=10, fill=tk.X)

        # 移动到附件模块下方
        self.label = tk.Label(self, text="请输入一个供AI辩论的话题:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(self, width=70)
        self.entry.pack(pady=5, padx=10, fill=tk.X)
        self.entry.bind("<Return>", lambda event: self.start_debate_thread())

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        self.submit_button = tk.Button(button_frame, text="开始辩论", command=self.start_debate_thread)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="终止辩论", command=self.stop_response, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.save_button = tk.Button(button_frame, text="保存辩论", command=self.save_debate, state=tk.NORMAL)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.output = scrolledtext.ScrolledText(self, width=80, height=20)
        self.output.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

    def start_debate_thread(self):
        topic = self.entry.get()
        if not topic and not self.attachments:
            messagebox.showwarning("警告", "请输入一个辩论话题或添加附件。")
            return

        # 过滤敏感词
        filtered_topic, contains_sensitive = self.sensitive_filter.filter_text(topic)
        
        if contains_sensitive:
            # 修改：显示过滤后的话题并终止辩论
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"辩论话题: {filtered_topic}\n\nAI: 抱歉，因话题包含敏感词无法开始辩论。\n")
            self.entry.delete(0, tk.END)
            self.submit_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            return
        
        # 构建包含附件内容的完整话题
        full_topic = filtered_topic
        
        if self.attachments:
            full_topic += "\n\n参考以下附件内容:\n"
            
            for i, attachment in enumerate(self.attachments):
                # 对于文件，提取并添加内容
                full_topic += f"\n附件 {i+1}: 文件 '{attachment['filename']}' 的内容:\n"
                # 限制内容长度，避免过长
                content = attachment['content']
                if len(content) > 2000:
                    content = content[:2000] + "..."
                full_topic += f"{content}\n"

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"辩论话题: {full_topic}\n\n")
        self.entry.delete(0, tk.END)

        self.submit_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)  # 辩论开始时禁用保存按钮

        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.run_debate, args=(full_topic, self.stop_event))
        thread.start()

    def stop_response(self):
        if self.stop_event:
            self.stop_event.set()
            self.save_button.config(state=tk.NORMAL)  # 终止后启用保存按钮

    def save_debate(self):
        """保存辩论内容为文件"""
        content = self.output.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("警告", "没有可保存的内容!")
            return

        # 创建文件保存对话框
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("文本文档", "*.txt"), ("所有文件", "*.*")],
            title="保存辩论内容"
        )
        
        if not file_path:  # 用户取消了保存
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("成功", f"辩论内容已保存到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错:\n{str(e)}")

    def upload_file(self):
        """上传文件附件"""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # 提取文件内容
                content = extract_text_from_file(file_path)
                filename = os.path.basename(file_path)
                
                # 添加到附件列表
                attachment_info = {
                    "type": "file",
                    "filename": filename,
                    "path": file_path,
                    "content": content
                }
                self.attachments.append(attachment_info)
                self.attachments_listbox.insert(tk.END, f"文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法上传文件: {str(e)}")

    def clear_attachments(self):
        """清除所有附件"""
        if self.attachments or self.attachments_listbox.size() > 0:
            if messagebox.askyesno("确认清除", "确定要清除所有附件吗？"):
                self.attachments = []
                self.attachments_listbox.delete(0, tk.END)

    def run_debate(self, topic, stop_event):
        try:
            self.controller.set_status("辩论进行中...")
            temperature = self.get_temperature()

            agent_a_persona = "你是辩手A，你对给定的话题持赞成态度，请有力地陈述你的观点。"
            agent_b_persona = "你是辩手B，你对给定的话题持反对态度，请针对辩手A的观点进行反驳。"

            messages = [{"role": "system", "content": agent_a_persona},
                        {"role": "user", "content": f"辩论话题是: '{topic}'。请开始你的开篇陈词。"}]

            for i in range(3):
                if stop_event.is_set(): break

                self.output.insert(tk.END, f"--- 第 {i + 1} 回合 ---\n辩手A: ")
                agent_a_response = ""
                for chunk in self.controller.api_client.get_response_stream(messages, temperature, stop_event):
                    # 修改：实时过滤辩手A的回应
                    filtered_chunk, contains_sensitive = self.sensitive_filter.filter_text(chunk)
                    agent_a_response += filtered_chunk
                    self.output.insert(tk.END, filtered_chunk)
                    self.output.see(tk.END)
                    
                    if contains_sensitive:
                        # 修改：发现敏感词时终止辩论
                        self.output.insert(tk.END, "\n\n[系统提示] 辩手A的发言包含敏感词，已终止辩论。\n")
                        self.output.see(tk.END)
                        stop_event.set()
                        break
                        
                if stop_event.is_set(): break

                messages = [{"role": "system", "content": agent_b_persona}, {"role": "user",
                                                                             "content": f"话题是'{topic}'。刚刚辩手A说：'{agent_a_response}'。请你对此进行反驳。"}]

                self.output.insert(tk.END, f"\n辩手B: ")
                agent_b_response = ""
                for chunk in self.controller.api_client.get_response_stream(messages, temperature, stop_event):
                    # 修改：实时过滤辩手B的回应
                    filtered_chunk, contains_sensitive = self.sensitive_filter.filter_text(chunk)
                    agent_b_response += filtered_chunk
                    self.output.insert(tk.END, filtered_chunk)
                    self.output.see(tk.END)
                    
                    if contains_sensitive:
                        # 修改：发现敏感词时终止辩论
                        self.output.insert(tk.END, "\n\n[系统提示] 辩手B的发言包含敏感词，已终止辩论。\n")
                        self.output.see(tk.END)
                        stop_event.set()
                        break
                        
                if stop_event.is_set(): break
                        
                self.output.insert(tk.END, "\n\n")

                messages = [{"role": "system", "content": agent_a_persona}, {"role": "user",
                                                                             "content": f"继续关于'{topic}'的辩论。你的论点是'{agent_a_response}'。辩手B反驳道：'{agent_b_response}'。请你回应。"}]
        finally:
            status_text = "用户已终止" if stop_event.is_set() else "辩论完成"
            self.controller.set_status(status_text)
            self.submit_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)  # 辩论结束后启用保存按钮


class CodeGenPage(BasePage):
    """专门用于生成代码的页面，集成了Prompt Engineering选项。"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.stop_event = None
        self.attachments = []  # 存储附件信息

        pe_frame = tk.LabelFrame(self, text="Prompt Engineering 选项", padx=10, pady=10)
        pe_frame.pack(pady=10, padx=10, fill=tk.X)
        tk.Label(pe_frame, text="编程语言:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.lang_var = tk.StringVar(value="Python")
        ttk.Combobox(pe_frame, textvariable=self.lang_var, values=["Python", "JavaScript", "Java", "C++", "SQL"]).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2)
        tk.Label(pe_frame, text="指定依赖库:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.libs_var = tk.StringVar()
        tk.Entry(pe_frame, textvariable=self.libs_var, width=20).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.add_comments_var = tk.BooleanVar(value=True)
        tk.Checkbutton(pe_frame, text="添加代码注释", variable=self.add_comments_var).grid(row=1, column=0, sticky=tk.W,
                                                                                           padx=5)
        self.add_docstrings_var = tk.BooleanVar()
        tk.Checkbutton(pe_frame, text="包含文档字符串(docstring)", variable=self.add_docstrings_var).grid(row=1,
                                                                                                          column=1,
                                                                                                          columnspan=2,
                                                                                                          sticky=tk.W,
                                                                                                          padx=5)
        self.explain_first_var = tk.BooleanVar()
        tk.Checkbutton(pe_frame, text="先解释思路再写代码", variable=self.explain_first_var).grid(row=1, column=2,
                                                                                                  columnspan=2,
                                                                                                  sticky=tk.W, padx=5)

        # 附件控制按钮 - 放在输入框上方
        attachment_frame = tk.Frame(self)
        attachment_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.file_button = tk.Button(attachment_frame, text="添加文件", command=self.upload_file)
        self.file_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(attachment_frame, text="全部清除", command=self.clear_attachments)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 显示附件列表的区域
        self.attachments_listbox = tk.Listbox(self, height=2, width=70)
        self.attachments_listbox.pack(pady=2, padx=10, fill=tk.X)

        # 移动到附件模块下方
        self.label = tk.Label(self, text="请输入您的代码生成需求:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(self, width=70)
        self.entry.pack(pady=5, padx=10, fill=tk.X)
        self.entry.bind("<Return>", lambda event: self.start_response_thread())

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        self.submit_button = tk.Button(button_frame, text="生成代码", command=self.start_response_thread)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="终止输出", command=self.stop_response, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.save_button = tk.Button(button_frame, text="保存代码", command=self.save_code, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.output = scrolledtext.ScrolledText(self, width=80, height=15, font=("Courier New", 10))
        self.output.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

    def start_response_thread(self):
        request = self.entry.get()
        if not request and not self.attachments:
            messagebox.showwarning("警告", "请输入代码生成需求或添加附件。")
            return

        # 过滤敏感词
        filtered_request, contains_sensitive = self.sensitive_filter.filter_text(request)
        
        if contains_sensitive:
            # 修改：显示过滤后的需求并终止生成
            self.output.insert(tk.END, f"\n\n> 用户需求: {filtered_request}\n\nAI: 抱歉，因需求包含敏感词无法生成代码。\n")
            self.entry.delete(0, tk.END)
            self.submit_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            return
        
        # 构建包含附件内容的完整请求
        full_request = filtered_request
        
        if self.attachments:
            full_request += "\n\n参考以下附件内容:\n"
            
            for i, attachment in enumerate(self.attachments):
                # 对于文件，提取并添加内容
                full_request += f"\n附件 {i+1}: 文件 '{attachment['filename']}' 的内容:\n"
                # 限制内容长度，避免过长
                content = attachment['content']
                if len(content) > 2000:
                    content = content[:2000] + "..."
                full_request += f"{content}\n"

        self.output.insert(tk.END, f"\n\n> 用户需求: {full_request}\n\n")
        self.entry.delete(0, tk.END)

        self.submit_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)  # 生成过程中禁用保存按钮

        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.get_response, args=(full_request, self.stop_event))
        thread.start()

    def stop_response(self):
        if self.stop_event:
            self.stop_event.set()

    def get_response(self, request, stop_event):
        try:
            self.controller.set_status("正在构建Prompt并生成代码...")
            language = self.lang_var.get()
            libraries = self.libs_var.get()
            system_prompt = f"你是一位精通 {language} 的资深软件开发专家。"
            
            # 构建包含附件信息的完整请求
            full_request_parts = [f"请为我生成一段 {language} 代码，我的需求是：'{request}'。", "\n请严格遵守以下要求："]
            if libraries: full_request_parts.append(f"- 必须使用以下库或框架：{libraries}。")
            if self.add_comments_var.get(): full_request_parts.append("- 在代码的关键部分添加清晰的中文注释。")
            if self.add_docstrings_var.get(): full_request_parts.append(
                f"- 为所有函数或类编写详细的文档字符串 (docstrings)。")
            full_request_parts.append(f"- 所有的代码都必须包裹在 ```{language.lower()} ... ``` 格式的代码块中。")
            if self.explain_first_var.get(): full_request_parts.append(
                "\n在生成代码之前，请先用中文分步骤详细地解释你的实现思路，然后再给出完整的代码。")
            
            # 添加附件信息
            if self.attachments:
                full_request_parts.append(f"\n\n参考以下附件内容:")
                
                for i, attachment in enumerate(self.attachments):
                    full_request_parts.append(f"\n附件 {i+1}: 文件 '{attachment['filename']}' 的内容:")
                    # 限制内容长度，避免过长
                    content = attachment['content']
                    if len(content) > 2000:
                        content = content[:2000] + "..."
                    full_request_parts.append(content)
                
            final_request = "\n".join(full_request_parts)

            self.controller.set_status("正在生成代码...")
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": final_request}]
            temperature = self.get_temperature()

            for content_chunk in self.controller.api_client.get_response_stream(messages, temperature, stop_event):
                # 修改：实时过滤代码生成内容
                filtered_chunk, contains_sensitive = self.sensitive_filter.filter_text(content_chunk)
                self.output.insert(tk.END, filtered_chunk)
                self.output.see(tk.END)
                
                if contains_sensitive:
                    # 修改：发现敏感词时终止生成
                    self.output.insert(tk.END, "\n\n[系统提示] 生成的代码包含敏感词，已终止输出。\n")
                    self.output.see(tk.END)
                    stop_event.set()
                    break
                    
        finally:
            status_text = "用户已终止" if stop_event.is_set() else "代码生成完成"
            self.controller.set_status(status_text)
            self.submit_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)

    def save_code(self):
    # 获取当前选择的语言
        language = self.lang_var.get()
        
        # 定义语言对应的文件扩展名映射
        ext_map = {
            "Python": ".py",
            "JavaScript": ".js",
            "Java": ".java",
            "C++": ".cpp",
            "SQL": ".sql"
        }
        
        # 获取默认文件扩展名
        default_ext = ext_map.get(language, ".txt")
        
        # 获取代码内容
        code_content = self.output.get("1.0", tk.END)
        
        # 提取代码块（如果存在）
        import re
        # 修改：增强正则表达式，更灵活地匹配语言标识和代码块
        code_block_pattern = re.compile(r'```\s*([a-z\+]*)\s*\n([\s\S]*?)```', re.IGNORECASE | re.MULTILINE)
        matches = code_block_pattern.findall(code_content)
        
        # 如果找到代码块，使用第一个代码块的内容
        if matches:
            # 尝试找到与所选语言匹配的代码块
            language_matches = [m for m in matches if self._is_language_match(m[0], language)]
            if language_matches:
                code_content = language_matches[0][1]  # 提取代码部分
            else:
                # 如果没有找到匹配的语言，使用第一个代码块
                code_content = matches[0][1]
        else:
            # 如果没有找到代码块，使用完整内容
            pass
        
        # 打开文件对话框
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[(f"{language} files", f"*{default_ext}"), ("All files", "*.*")],
            initialfile="file"
        )
        
        # 如果用户选择了文件路径，则保存文件
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(code_content)
                messagebox.showinfo("成功", f"代码已成功保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")

    def _is_language_match(self, code_block_lang, selected_lang):
        """检查代码块语言标识是否与所选语言匹配"""
        # 语言映射表，处理不同表示方式
        lang_map = {
            "Python": ["python", "py"],
            "JavaScript": ["javascript", "js"],
            "Java": ["java"],
            "C++": ["c++", "cpp", "cxx"],
            "SQL": ["sql"]
        }
        
        # 获取所选语言的所有可能标识
        valid_ids = lang_map.get(selected_lang, [])
        # 如果代码块语言标识在有效标识列表中，或者没有语言标识但用户选择了该语言
        return code_block_lang.lower() in valid_ids or (not code_block_lang and selected_lang == "C++")

    def upload_file(self):
        """上传文件附件"""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # 提取文件内容
                content = extract_text_from_file(file_path)
                filename = os.path.basename(file_path)
                
                # 添加到附件列表
                attachment_info = {
                    "type": "file",
                    "filename": filename,
                    "path": file_path,
                    "content": content
                }
                self.attachments.append(attachment_info)
                self.attachments_listbox.insert(tk.END, f"文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法上传文件: {str(e)}")

    def clear_attachments(self):
        """清除所有附件"""
        if self.attachments or self.attachments_listbox.size() > 0:
            if messagebox.askyesno("确认清除", "确定要清除所有附件吗？"):
                self.attachments = []
                self.attachments_listbox.delete(0, tk.END)    
