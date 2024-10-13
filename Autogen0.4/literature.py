from autogen_agentchat.agents import CodingAssistantAgent, ToolUseAssistantAgent, BaseChatAgent
from autogen_agentchat.teams import RoundRobinGroupChat, StopMessageTermination
from autogen_core.components.models import OpenAIChatCompletionClient
from autogen_core.components.tools import FunctionTool

import os
client = OpenAIChatCompletionClient(model="llama3-70b-8192", 
                                    api_key=os.environ.get("GROQ_API_KEY"), 
                                    base_url="https://api.groq.com/openai/v1",
                                    max_tokens=8000)


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

google_search_tool = FunctionTool(
    google_search, description="Search Google for information, returns results with a snippet and body content"
)
arxiv_search_tool = FunctionTool(
    arxiv_search, description="Search Arxiv for papers related to a given topic, including abstracts"
)

google_search_agent = ToolUseAssistantAgent(
    name="Google_Search_Agent",
    registered_tools=[google_search_tool],
    model_client=client,
    description="An agent that can search Google for information, returns results with a snippet and body content",
    system_message="You are a helpful AI assistant. Solve tasks using your tools.",
)

arxiv_search_agent = ToolUseAssistantAgent(
    name="Arxiv_Search_Agent",
    registered_tools=[arxiv_search_tool],
    model_client=client,
    description="An agent that can search Arxiv for papers related to a given topic, including abstracts",
    system_message="You are a helpful AI assistant. Solve tasks using your tools. Specifically, you can take into consideration the user's request and craft a search query that is most likely to return relevant academi papers.",
)


report_agent = CodingAssistantAgent(
    name="Report_Agent",
    model_client=client,
    description="Generate a report based on a given topic",
    system_message="You are a helpful assistant. Your task is to synthesize data extracted into a high quality literature review including CORRECT references. You MUST write a final report that is formatted as a literature review with CORRECT references.  Your response should end with the word 'TERMINATE'",
)



import asyncio
async def literature_research():
    team = RoundRobinGroupChat(participants=[google_search_agent, arxiv_search_agent, report_agent])
    result = await team.run(
        task="Write a literature review on no code tools for building multi agent ai systems",
        termination_condition=StopMessageTermination(),
    )
    return result

# Function to extract and print research papers information
def extract_research_info(results):
    """
    Extracts titles, links, snippets, and dates from a list of research papers.

    Parameters:
    results (list): A list of dictionaries containing research paper data.

    Returns:
    None
    """
    for index, result in enumerate(results):
        # Extract basic details
        title = result.get('title', 'No Title Available')
        link = result.get('link', 'No Link Available')
        snippet = result.get('snippet', 'No Snippet Available')
        date = result.get('date', 'No Date Available')

        # Print basic details
        print(f"Paper {index + 1}:")
        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Snippet: {snippet}")
        print(f"Date: {date}\n")
        
        # Check for sitelinks and print them
        if 'sitelinks' in result:
            print("Sitelinks:")
            for sitelink in result['sitelinks']:
                sitelink_title = sitelink.get('title', 'No Title Available')
                sitelink_url = sitelink.get('link', 'No Link Available')
                print(f"- {sitelink_title}: {sitelink_url}")
            print()


if __name__ == "__main__":
    # Properly run the async function using asyncio's event loop
    os.system("clear")
    result = asyncio.run(literature_research())
    print(result)
    # Get the formatted summary
    #os.system("clear")
    
    #formatted_summary = extract_research_info(list(result))
    #print(formatted_summary)

