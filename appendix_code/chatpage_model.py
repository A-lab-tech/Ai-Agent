import os
from dotenv import load_dotenv
from camel.types import RoleType, ModelType, ModelPlatformType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks import Task
from camel.toolkits import SearchToolkit
from tools_con import search_tool_baidu, python_executor, weather_tool, search_tool_bing



load_dotenv()

# 从环境变量中获取 SiliconFlow API 密钥
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SILICONFLOW_API_KEY:
    raise ValueError("SILICONFLOW_API_KEY 环境变量未设置。请在 .env 文件中或系统环境变量中设置。")
'''
try:
    qwenmodel = ModelFactory.create(
        # model_platform=ModelPlatformType.SILICONFLOW, 
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        # model_type='deepseek-ai/DeepSeek-V3',
        model_type="Qwen/Qwen2.5-72B-Instruct",
        # model_type="Qwen/QwQ-32B",
        url="https://api.siliconflow.cn/v1",
        api_key=SILICONFLOW_API_KEY,
        # model_platform=ModelPlatformType.GEMINI, 
        # model_type=ModelType.GEMINI_2_5_FLASH_PREVIEW, 
        model_config_dict={"temperature": 0.7, "stream": True, "max_tokens": 4096} # stream=False 便于调试
    )
    print(f"成功创建模型实例：{qwenmodel.model_type}")
except Exception as e:
    print(f"创建模型实例失败，请检查配置或API密钥：{e}")
'''
agents_web={}
agents={}
for tem in [0.2, 0.7, 1,2]:
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
            model_config_dict={"temperature": tem, "stream": False, "max_tokens": 4096} # stream=False 便于调试
        )
        print(f"成功创建模型实例：{deepseekmodel.model_type}")
    except Exception as e:
        print(f"创建模型实例失败，请检查配置或API密钥：{e}")
    
    chatagent = ChatAgent("You are a helpful assistant.",
                        model=deepseekmodel,
                        tools=[])

    chatagent_web = ChatAgent("You are a helpful assistant, and you can use tools to search the web and get weather information.",
                        model=deepseekmodel,
                        tools=[search_tool_bing, weather_tool,])
    agents_web[tem] = chatagent_web
    agents[tem] = chatagent

if __name__ == "__main__":
    # agent = agents[0.7]
    agent =  agents_web[0.7]
    question = """What is camel ai? """
    response = agent.step(question)
    print(response.msgs[0].content)
    