import os
from dotenv import load_dotenv
from camel.types import RoleType, ModelType, ModelPlatformType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks import Task
from camel.toolkits import SearchToolkit, CodeExecutionToolkit, WeatherToolkit, MathToolkit

search_tool_baidu = SearchToolkit().search_baidu
search_tool_bing = SearchToolkit().search_bing
python_executor = CodeExecutionToolkit().execute_code
weather_tool = WeatherToolkit().get_weather_data
add_tool = MathToolkit().add
sub_tool = MathToolkit().sub
mul_tool = MathToolkit().multiply
div_tool = MathToolkit().divide
