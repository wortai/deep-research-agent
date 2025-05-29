from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="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")

# Step 2. Defining the list of URLs to extract content from
urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://en.wikipedia.org/wiki/Quantum_computing",
    "https://en.wikipedia.org/wiki/Climate_change"
] # You can provide up to 20 URLs simultaneously

# Step 3. Executing the extract request
response = tavily_client.extract(urls=urls, include_images=True)

# Step 4. Printing the extracted raw content
for result in response["results"]:
    print(f"URL: {result['url']}")
    print(f"Raw Content: {result['raw_content']}")
    print(f"Images: {result['images']}\n")
