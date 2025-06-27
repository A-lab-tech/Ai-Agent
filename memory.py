import json
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self, storage_dir="conversations"):
        self.storage_dir = storage_dir
        self.current_conversation = None
        self.conversations = {}
        os.makedirs(storage_dir, exist_ok=True)
        self.load_conversations()

    def load_conversations(self):
        """加载所有保存的对话"""
        self.conversations = {}
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations[filename[:-5]] = data

    def start_new_conversation(self):
        """开始新的对话"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_conversation = {
            'id': f"对话_{timestamp}",
            'created_at': timestamp,
            'messages': []
        }
        return self.current_conversation['id']

    def add_message(self, role, content):
        """添加消息到当前对话"""
        if self.current_conversation is None:
            self.start_new_conversation()
        
        self.current_conversation['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def get_conversation_history(self, conversation_id=None):
        """获取对话历史"""
        if conversation_id is None:
            if self.current_conversation:
                return self.current_conversation['messages']
            return []
        else:
            return self.conversations.get(conversation_id, {}).get('messages', [])

    def save_conversation(self):
        """保存当前对话到文件"""
        if self.current_conversation:
            filepath = os.path.join(self.storage_dir, f"{self.current_conversation['id']}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_conversation, f, ensure_ascii=False, indent=2)
            self.conversations[self.current_conversation['id']] = self.current_conversation

    def delete_conversation(self, conversation_id):
        """删除指定对话"""
        if conversation_id in self.conversations:
            filepath = os.path.join(self.storage_dir, f"{conversation_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.conversations[conversation_id]
            return True
        return False

    def export_to_markdown(self, conversation_id, filename):
        """导出对话到Markdown文件"""
        if conversation_id not in self.conversations:
            return False
        
        messages = self.conversations[conversation_id]['messages']
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 对话记录: {conversation_id}\n\n")
            f.write(f"**创建时间**: {self.conversations[conversation_id]['created_at']}\n\n")
            for msg in messages:
                f.write(f"## {msg['role']} ({msg['timestamp']})\n\n")
                f.write(f"{msg['content']}\n\n")
        return True

    def get_all_conversations(self):
        """获取所有对话列表"""
        return sorted(self.conversations.keys(), reverse=True)