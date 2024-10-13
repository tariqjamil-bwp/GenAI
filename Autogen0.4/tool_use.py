from autogen_agentchat.agents import ToolUseAssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, StopMessageTermination
from autogen_core.components.models import OpenAIChatCompletionClient
from autogen_core.components.tools import FunctionTool

async def get_weather(city: str) -> str:
    return f"The weather in {city} is 72 degrees and Sunny."


get_weather_tool = FunctionTool(get_weather, description="Get the weather for a city")

assistant = ToolUseAssistantAgent(
    "Weather_Assistant",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    registered_tools=[get_weather_tool],
)

team = RoundRobinGroupChat([assistant])
result = await team.run("What's the weather in New York?", termination_condition=StopMessageTermination())