from autogen_agentchat.agents import CodingAssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, StopMessageTermination
from autogen_core.components.models import OpenAIChatCompletionClient
import os
client = OpenAIChatCompletionClient(model="llama3-70b-8192", api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

planner_agent = CodingAssistantAgent(
    "planner_agent",
    model_client=client,
    description="A helpful assistant that can plan trips.",
    system_message="You are a helpful assistant that can suggest a travel plan for a user based on their request.",
)

local_agent = CodingAssistantAgent(
    "local_agent",
    model_client=client,
    description="A local assistant that can suggest local activities or places to visit.",
    system_message="You are a helpful assistant that can suggest authentic and interesting local activities or places to visit for a user and can utilize any context information provided.",
)

language_agent = CodingAssistantAgent(
    "language_agent",
    model_client=client,
    description="A helpful assistant that can provide language tips for a given destination.",
    system_message="You are a helpful assistant that can review travel plans, providing feedback on important/critical tips about how best to address language or communication challenges for the given destination. If the plan already includes language tips, you can mention that the plan is satisfactory, with rationale.",
)

travel_summary_agent = CodingAssistantAgent(
    "travel_summary_agent",
    model_client=client,
    description="A helpful assistant that can summarize the travel plan.",
    system_message="You are a helpful assistant that can take in all of the suggestions and advice from the other agents and provide a detailed tfinal travel plan. You must ensure th b at the final plan is integrated and complete. YOUR FINAL RESPONSE MUST BE THE COMPLETE PLAN. When the plan is complete and all perspectives are integrated, you can respond with TERMINATE.",
)

# travel.py
import asyncio
async def plan_trip():
    group_chat = RoundRobinGroupChat([planner_agent, local_agent, language_agent, travel_summary_agent])
    result = await group_chat.run(task="Plan a 3 day trip to Nepal.", 
                                  termination_condition=StopMessageTermination())
    return result

if __name__ == "__main__":
    # Properly run the async function using asyncio's event loop
    response = asyncio.run(plan_trip())

    os.system("clear")
    # Extracting and printing only the relevant messages (content of the trip plan)
    for message in response.messages:
        if message.source == 'planner_agent':
            print("Planner's Itinerary:\n", message.content)
        elif message.source == 'local_agent':
            print("\nLocal Expert's Suggestions:\n", message.content)
        elif message.source == 'language_agent':
            print("\nLanguage and Communication Tips:\n", message.content)
        elif message.source == 'travel_summary_agent':
            print("\nTravel Summary:\n", message.content)
        else:
            print(message.content)

