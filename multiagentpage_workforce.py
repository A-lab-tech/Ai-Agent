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

try:
    model = ModelFactory.create(
        # model_platform=ModelPlatformType.SILICONFLOW, 
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        # model_type='deepseek-ai/DeepSeek-V3',
        model_type="Qwen/Qwen2.5-72B-Instruct",
        # model_type="Qwen/QwQ-32B",
        url="https://api.siliconflow.cn/v1",
        api_key=SILICONFLOW_API_KEY,
        # model_platform=ModelPlatformType.GEMINI, 
        # model_type=ModelType.GEMINI_2_5_FLASH_PREVIEW, 
        model_config_dict={"temperature": 0.7, "stream": False, "max_tokens":4096} # stream=False 便于调试
    )
    print(f"成功创建模型实例：{model.model_type}")
except Exception as e:
    print(f"创建模型实例失败，请检查配置或API密钥：{e}")

# print(model.model_config_dict["temperature"])
# search_tool = SearchToolkit().search_baidu


weather_agent = ChatAgent(
    "你是一个助手，可以帮助完成对旅游目标天气的查询，如果有必要，可以使用必应搜索引擎进行查询，并给出对所穿衣物的建议",
    model=model,
    tools=[weather_tool, search_tool_bing]
    # tools=[search_tool,]
)

spots_agent = ChatAgent(
    "你是一个助手，可以帮助完成对旅游目标景点的查询和计划",
    model=model,
    tools=[search_tool_baidu, search_tool_bing]
)

accommodation_agent = ChatAgent(
    "你是一个助手，可以帮助完成对旅游目标食宿的查询和计划",
    model=model,
    tools=[search_tool_baidu, search_tool_bing]
)

transportation_agent = ChatAgent(
    "你是一个助手，可以帮助完成对旅游目标交通情况的查询和计划",
    model=model,
    tools=[search_tool_baidu, search_tool_bing]
)

result_agent = ChatAgent(
    "你是一个助手，可以帮助完成对旅游目标的综合整理，并计划得到每天的行程",
    model=model,
)
# Create a workforce instance
# workforce = Workforce("A Simple Workforce",)

workforce = Workforce(description="旅游攻略制作工作组，把任务分工解决。你应当跟随提问的语言",new_worker_agent_kwargs={'model':model},coordinator_agent_kwargs={'model':model, },task_agent_kwargs={'model':model},)


workforce.add_single_agent_worker(
    "一个天气查询助手",
    worker=weather_agent
).add_single_agent_worker(
    "一个景点查询助手",
    worker=spots_agent
).add_single_agent_worker(
    "一个食宿查询助手",
    worker=accommodation_agent
).add_single_agent_worker(
    "一个交通查询助手",
    worker=transportation_agent
).add_single_agent_worker(
    "一个结果整理助手",
    worker=result_agent
)


if __name__ == "__main__":
    # The id can be any string
    task = Task(
        content="计划一个12月下旬从上海去北京3天旅游的攻略，详细一些，考虑所有方面",
        id="0",
    )

    # Process the task with the workforce
    task = workforce.process_task(task)

    # See the result
    print(task.result)