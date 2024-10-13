import asyncio
import logging
from autogen_agentchat import EVENT_LOGGER_NAME
from autogen_agentchat.agents import CodeExecutorAgent, CodingAssistantAgent
from autogen_agentchat.logging import ConsoleLogHandler
from autogen_agentchat.teams import RoundRobinGroupChat, StopMessageTermination
from autogen_ext.code_executor.docker_executor import DockerCommandLineCodeExecutor
from autogen_core.components.models import OpenAIChatCompletionClient
import os

logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(ConsoleLogHandler())
logger.setLevel(logging.INFO)

#client = OpenAIChatCompletionClient(model="gpt-4", api_key="YOUR_API_KEY")
client = OpenAIChatCompletionClient(model="llama3-70b-8192", api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

async def main() -> None:
    async with DockerCommandLineCodeExecutor(work_dir="coding") as code_executor:
        code_executor_agent = CodeExecutorAgent("code_executor", code_executor=code_executor)
        coding_assistant_agent = CodingAssistantAgent(
            "coding_assistant", 
            model_client=client,
        )
        group_chat = RoundRobinGroupChat([coding_assistant_agent, code_executor_agent])
        result = await group_chat.run(
            task="Create a plot of NVDIA and TSLA stock returns YTD from 2024-01-01 and save it to 'nvidia_tesla_2024_ytd.png'.",
            termination_condition=StopMessageTermination(),
        )

asyncio.run(main())