import json
import os

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