import arxiv

class ArxivRetriever:
    '''
    This class takes a list of queries and return a dictionary of query and the corresponding urls.

    Input: 
        - queries: list of queries
        - ppq: papers per query

    Output:
        - retrieved_urls: dictionary of query and the corresponding urls
        {
            "query1": [url1, url2, url3],
            "query2": [url4, url5, url6],
            "query3": [url7, url8, url9]
            ...
        }

    '''

    def __init__(self, queries, ppq=1):
        self.queries = queries
        self.ppq = ppq # Papers per Query

    # Takes a Query and Returns a List of URLs
    def _retrieve_arxiv_urls(self, query):
        search_results = list()

        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=self.ppq, # Number of Papers to Retrieve per Query
            sort_by=arxiv.SortCriterion.Relevance
        )

        for result in client.results(search):
            print(result.title, result.pdf_url)
            search_results.append(result.pdf_url)

        return search_results

    # Takes a list of search queries and returns a dictionary of query and the corresponding urls.
    def search_arxiv(self):
        retrieved_urls = dict()
        all_seen_urls = set()  # Track all URLs we've seen
        
        for query in self.queries:
            urls = self._retrieve_arxiv_urls(query)
            
            # Filter out URLs that already exist in other results
            unique_urls = []
            for url in urls:
                if url not in all_seen_urls:
                    unique_urls.append(url)
                    all_seen_urls.add(url)
            
            retrieved_urls[query] = unique_urls
        
        return retrieved_urls

    def run(self):
        search_results = self.search_arxiv()
        return search_results


# Example Usage
if __name__ == "__main__":
    queries = ["Low Rank Adaptation of Large Language Models", "Generative Pre-trained Transformer 3", "Quantum Computers"]
    retriever = ArxivRetriever(queries, ppq=5)
    retrieved_urls = retriever.run()
    print(retrieved_urls)
