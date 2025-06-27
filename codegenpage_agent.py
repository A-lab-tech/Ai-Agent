import os
from dotenv import load_dotenv
from camel.types import RoleType, ModelType, ModelPlatformType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks import Task
from camel.toolkits import CodeExecutionToolkit
# from tools_con import search_tool_baidu, python_executor, weather_tool, search_tool_bing


load_dotenv()

# 从环境变量中获取 SiliconFlow API 密钥
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SILICONFLOW_API_KEY:
    raise ValueError("SILICONFLOW_API_KEY 环境变量未设置。请在 .env 文件中或系统环境变量中设置。")

try:
    deepseekmodel = ModelFactory.create(
        # model_platform=ModelPlatformType.SILICONFLOW, 
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type='deepseek-ai/DeepSeek-V3',
        # model_type="Qwen/Qwen2.5-72B-Instruct",
        # model_type="Qwen/QwQ-32B",
        url="https://api.siliconflow.cn/v1",
        api_key=SILICONFLOW_API_KEY,
        # model_platform=ModelPlatformType.GEMINI, 
        # model_type=ModelType.GEMINI_2_5_FLASH_PREVIEW, 
        model_config_dict={"temperature": 0.2, "stream": False, "max_tokens": 4096} # stream=False 便于调试
    )
    print(f"成功创建模型实例：{deepseekmodel.model_type}")
except Exception as e:
    print(f"创建模型实例失败，请检查配置或API密钥：{e}")


def agent_generator(language):
    sys_prompt=f"""你是一个严谨的研究员，擅长完成{language}代码书写。
        你的任务是**清晰地理解用户的需求，并根据需求完成代码，调用工具检查代码的完整性**。
        
        你拥有以下强大的工具：
        1.  **code_executor(code: str, code_type={language})**: 当用户需要执行数学计算、数据处理、代码生成或任何需要编程逻辑的任务时使用此工具。例如，当用户要求“计算 123 乘以 456”。
        **你的工作流程：**
        - **第一步：理解请求** - 仔细分析用户的输入。
        - **第二步：选择工具** - 判断哪个工具能解决当前问题。
            - 如果是需要计算或执行代码，**请立即调用 `code_executor` 工具**。
        - **第三步：执行与回复** - 工具执行后，你会收到工具的输出。结合工具输出，给出正确的代码。
        - **重要提示：** 在你决定使用工具时，请直接输出工具调用指令，不要有额外的自然语言说明，除非你确定不需要工具而直接回复。
        """
    

    code_executor=CodeExecutionToolkit().execute_code

    codeagent = ChatAgent(sys_prompt,
                        model=deepseekmodel,
                            tools=[code_executor],)
    return codeagent

if __name__ == "__main__":
    codeagent = agent_generator(language="python", )
    question = "请生成一个Python代码，用BFS完成八皇后的求解。"
    response = codeagent.step(question)
    print(response.msgs[0].content)
