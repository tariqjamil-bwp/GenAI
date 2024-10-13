import os
import time
from openai import RateLimitError
from autogen_core.components.models import OpenAIChatCompletionClient  # Assuming this is where the client class is from

# Define the models in priority order
models = [
    "llama-3.1-70b-versatile",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]

# Function to create clients for all models
def create_clientsX():
    clients = []  # List to store successful clients

    for model in models:
        try:
            client = OpenAIChatCompletionClient(
                model=model,
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                max_tokens=4096,  # Adjust max_tokens as needed
            )
            print(f"Successfully initialized client with model: {model}")
            clients.append(client)  # Add successful client to list

        except RateLimitError:
            print(f"Rate limit exceeded for model: {model}. Skipping to the next one...")
            time.sleep(1)  # Optional: Wait before trying the next model

    if not clients:
        raise Exception("No clients could be initialized. All models exceeded rate limits.")

    return clients  # Return the list of clients

##################################################################################################################################################
def create_clients(model_index=1):
    
    # Prepare the list of models starting from the next one
    available_models = models[model_index:] + models[:model_index]

    clients = []  # List to store successful clients
    print(available_models)
    for model in available_models:
        print(model)
        try:
            client = OpenAIChatCompletionClient(
                model=model,
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                max_tokens=8000,
            )
            print(f"Successfully initialized client with model: {model}")
            clients.append(client)  # Add successful client to the list

        except RateLimitError:
            print(f"Rate limit exceeded for model: {model}. Skipping to the next one...")
            time.sleep(1)  # Optional: Wait before trying the next model

    if not clients:
        raise Exception("No clients could be initialized. All models exceeded rate limits.")

    return clients  # Return the list of clients

# Create the clients
#clients_list = create_clients()
