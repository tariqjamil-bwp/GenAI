############################## LITERATURE REVIEW ###############################################
from autogen_agentchat.agents import CodingAssistantAgent, ToolUseAssistantAgent, BaseChatAgent
from autogen_agentchat.teams import RoundRobinGroupChat, StopMessageTermination
from autogen_core.components.models import OpenAIChatCompletionClient
from autogen_core.components.tools import FunctionTool
import asyncio
from model import create_clients
client = create_clients(0)
#################################################################################################
def google_search(query: str, num_results: int = 2, max_chars: int = 500) -> list:  # type: ignore[type-arg]
    import requests
    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        raise ValueError("Serper API key not found in environment variables")
    # Serper API endpoint for search
    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    # Set up request parameters
    payload = {
        "q": query,
        "num": num_results
    }
    # Make request to Serper API
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error in API request: {response.status_code}")

    # Parse the results from the response
    search_results = response.json().get("organic", [])

    # Limit the length of the results based on max_chars
    truncated_results = []
    total_chars = 0
    for result in search_results:
        snippet = result.get("snippet", "")
        if total_chars + len(snippet) <= max_chars:
            truncated_results.append(result)
            total_chars += len(snippet)
        else:
            break
    print(truncated_results)
    return truncated_results

    def get_page_content(url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            content = ""
            for word in words:
                if len(content) + len(word) + 1 > max_chars:
                    break
                content += " " + word
            return content.strip()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    enriched_results = []
    for item in results:
        body = get_page_content(item["link"])
        enriched_results.append(
            {"title": item["title"], "link": item["link"], "snippet": item["snippet"], "body": body}
        )
        time.sleep(1)  # Be respectful to the servers

    return enriched_results

#################################################################################################
def arxiv_search(query: str, max_results: int = 2) -> list:  # type: ignore[type-arg]
    """
    Search Arxiv for papers and return the results including abstracts.
    """
    import arxiv

    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)

    results = []
    for paper in client.results(search):
        results.append(
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "abstract": paper.summary,
                "pdf_url": paper.pdf_url,
            }
        )

    # # Write results to a file
    # with open('arxiv_search_results.json', 'w') as f:
    #     json.dump(results, f, indent=2)

    return results

#################################################################################################
google_search_tool = FunctionTool(
    google_search, description="Search Google for information, returns results with a snippet and body content"
)
arxiv_search_tool = FunctionTool(
    arxiv_search, description="Search Arxiv for papers related to a given topic, including abstracts"
)

google_search_agent = ToolUseAssistantAgent(
    name="Google_Search_Agent",
    registered_tools=[google_search_tool],
    model_client=client[0],
    description="An agent that can search Google for information, returns results with a snippet and body content",
    system_message="You are a helpful AI assistant. Solve tasks using your tools.",
)

arxiv_search_agent = ToolUseAssistantAgent(
    name="Arxiv_Search_Agent",
    registered_tools=[arxiv_search_tool],
    model_client=client[1],
    description="An agent that can search Arxiv for papers related to a given topic, including abstracts",
    system_message="You are a helpful AI assistant. Solve tasks using your tools. Specifically, you can take into consideration the user's request and craft a search query that is most likely to return relevant academi papers.",
)

#################################################################################################
report_agent = CodingAssistantAgent(
    name="Report_Agent",
    model_client=client[2],
    description="Generate a report based on a given topic",
    system_message="You are a helpful assistant. "
    "Your task is to synthesize data extracted into a high quality literature review including CORRECT references. "
    "You FIRST discuss individually each paper, with <title> <author> <published_date> <abstract> <body> <paper_url>. "
    "You MUST write a final report that is formatted as a literature review with CORRECT references.  "
    "Your response should end with the word 'TERMINATE'",
)

#################################################################################################
import asyncio, os
async def literature_research(topic):
    team = RoundRobinGroupChat(participants=[google_search_agent, arxiv_search_agent, report_agent])
    result = await team.run(
        task=f"Write a detailed literature review on {topic}.",
        termination_condition=StopMessageTermination(),
    )
    return result

#################################################################################################
import re
import markdown2  # Ensure this is installed
from IPython.display import display, HTML
import re

def convert_to_markdown(response):
    # Extract relevant parts of the response
    messages = response.messages

    # Initialize a Markdown string
    markdown = ""

    # Loop through each message to build the Markdown content
    for message in messages:
        source = message.source
        content = message.content

        if isinstance(content, str):
            # Extract content only from the Report_Agent source
            if source == 'Report_Agent':
                # Clean up content to remove unwanted characters
                content = re.sub(r'<.*?>', '', content)  # Remove XML tags

                # Replace URLs with Markdown format for links and ensure each starts on a new line
                content = re.sub(r'(https?://[^\s]+)', r'[\1](\1)\n', content)

                # Adding formatting for the Report_Agent output
                markdown += f"# {source} Output\n\n{content.strip()}\n\n"
                break  # Exit the loop after extracting Report_Agent content

    return markdown
#################################################################################################
def convert_to_html(markdown_content):
    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content)

    # Add custom styles for font size, text wrapping, and link styling
    styled_html = f"""
    <style>
        .markdown-body {{
            font-size: 16px;
            width: 110ch;
            line-height: 1.6;
            margin: 12px 0;
        }}
        a {{
            color: blue;          /* Set link color to blue */
            text-decoration: underline;  /* Underline links */
        }}
    </style>
    <div class="markdown-body">
        {html_content}
    </div>
    """
    return styled_html

def save_and_open_html(html_output, filename="output.html"):
    # Save HTML to a file
    with open(filename, "w") as file:
        file.write(html_output)
    
    # Automatically open the file in the default web browser
    webbrowser.open(f"file://{os.path.realpath(filename)}")

#################################################################################################
if __name__ == "__main__":
    # Properly run the async function using asyncio's event loop
    topic = "Top 5 papers on LLM Agents in Education in 2024"

    os.system("clear")
    result = asyncio.run(literature_research(topic))
    print(result)

    #for m in result.messages:
    #    print(m.source)
    #    print(m.content)

    # Assuming 'result' is your response object containing messages
    markdown_result = convert_to_markdown(result)
    print(markdown_result)
    # Convert the Markdown to HTML
    html_output = convert_to_html(markdown_result)
    # Display the styled HTML output in Jupyter Notebook
    display(HTML(html_output))
    import webbrowser
    # Save and open the HTML output
    save_and_open_html(html_output)
