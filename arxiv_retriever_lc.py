import os
import arxiv
from langchain_community.retrievers import ArxivRetriever


class ArxivScraper:
    '''
    This class is used to scrape a paper from Arxiv.
    '''

    def __init__(self, link, session=None):
        self.link = link
        self.session = session

    def scrape(self):
        query = self.link.split("/")[-1]
        retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=None)
        docs = retriever.invoke(query)

        # Include the published date and author to provide additional context, 
        # aligning with APA-style formatting in the report.
        context = f"Published: {docs[0].metadata['Published']}; Author: {docs[0].metadata['Authors']}; Content: {docs[0].page_content}"
        image = []

        return context, image, docs[0].metadata["Title"]


class ArxivSearch:
    '''
    This class is used to search for papers on Arxiv.
    '''

    def __init__(self, query, max_results=5):
        self.query = query
        self.max_results = max_results

    def retrieve(self):
        search_results = dict()

        client = arxiv.Client()

        search = arxiv.Search(
            query=self.query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
    
        for result in client.results(search):
            print(f"Title: {result.title}")
            print(f"PDF Link: {result.pdf_url}\n")
            search_results[result.title] = result.pdf_url

        return search_results

class ArxivAgent:
    '''
    This class is used to create an agent that can search for papers on Arxiv and scrape them.
    '''

    def __init__(self, query, max_results=5):
        self.query = query
        self.max_results = max_results

    def run(self):
        search_results = ArxivSearch(self.query, self.max_results).retrieve()
        for title, link in search_results.items():
            context, image, title = ArxivScraper(link).scrape()
            
            # Create a report
            report = f"Title: {title}\n\n"
            report += f"Context: {context}\n\n"
            report += f"Image: {image}\n"
        
        # Save the report to a file
        with open("report.txt", "w") as f:
            f.write(report)

        return report

if __name__ == "__main__":
    agent = ArxivAgent(query="Low Rank Adaptation of Large Language Models", max_results=1)
    agent.run()
