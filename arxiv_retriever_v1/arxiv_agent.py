
'''
This script presents Arxiv Scraper based on User Query.

    - INPUT: User Query (Example: "Low Rank Adaptation of Large Language Models")

    - Step 1: Create different prompts from base user query -> Expecting healthier results.
    - Step 2: Search Arxiv for the prompts -> Get URLs
    - Step 3: Scrape the paper -> Get Abstract, Full Text, Summarized Text [3 Modes to test out]
    - Step 4: Combine the results -> Get a report

    - OUTPUT: Save the report to a file
'''
import arxiv
from datetime import datetime
from queries import QueryVariationGenerator
from langchain_community.retrievers import ArxivRetriever
from langchain_community.document_loaders import ArxivLoader

class ArxivAgent:
    def __init__(self, query, max_results=5, ppq=1):
        self.query = query
        self.max_results = max_results
        self.ppq = ppq # Papers per Query

    # Step 0: Create different prompts from base user query (Use Langchain with Gemini API)
    def create_prompts(self):
        query_generator = QueryVariationGenerator(api_key="AIzaSyAguOE8t4H1YON7WjH0HXj6Q-DRKRj49Pk")
        
        # Query Variation Generator
        prompts = query_generator.generate_query_variations(self.query, num_variations=int(self.max_results/2))
        
        # Query Variation Generator with Context
        prompts_with_context = query_generator.generate_with_context(
            base_query=self.query,
            context="Generative PreTrained Transformers",
            num_variations=(self.max_results - len(prompts))
        )

        return prompts + prompts_with_context

    # Step 1: Search Arxiv for the prompts -> Get URLs
    def _retrieve_arxiv_urls(self, query):
        search_results = list()

        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=self.ppq, # Number of Papers to Retrieve per Query
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        for result in client.results(search):
            print(result.title, result.pdf_url)
            search_results.append(result.pdf_url)

        return search_results
    
    # Step 2: Search Arxiv for the prompts -> Get URLs
    def search_arxiv(self, search_queries):
        search_results = set() # Return Variable

        for query in search_queries:
            search_results.update(self._retrieve_arxiv_urls(query))
        
        return list(search_results)

    # Step 3: Scrape the paper -> Get Abstract, Full Text, Summarized Text [3 Modes to test out]

    # 3a: Abstract Only
    def _scrape_abstract(self, link):
        query = link.split("/")[-1]
        retriever = ArxivRetriever(load_max_docs=1, doc_content_chars_max=None)
        docs = retriever.invoke(query)

        # Include the published date and author to provide additional context, 
        # aligning with APA-style formatting in the report.
        context = f"Published: {docs[0].metadata['Published']}; Author: {docs[0].metadata['Authors']}; Content: {docs[0].page_content}"
        image = []
        
        return context, image, docs[0].metadata["Title"]

    # 3b: Full Text
    def _scrape_full_text(self, link):
        # Load full paper content
        query = link.split("/")[-1]
        loader = ArxivLoader(query=query, load_max_docs=1)
        docs = loader.load()

        context = f"Published: {docs[0].metadata['Published']}; Author: {docs[0].metadata['Authors']}; Content: {docs[0].page_content}"
        image = []

        return context, image, docs[0].metadata["Title"]

    # 3c: Summarized Text
    def _scrape_summarized_text(self, link):
        pass

    # 3d: Creating Report by Scraping Papers based on the scrape_method | Default: Abstract Only
    def create_report(self, search_results, report_name="report.txt", scrape_method=_scrape_abstract):
        all_reports = []  # Store all individual reports
        
        # Clear the file at the beginning (optional - remove if you want to keep existing content)
        with open(report_name, "w") as f:
            f.write(f"ArXiv Research Report\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Papers: {len(search_results)}\n")
            f.write(f"{'='*60}\n\n")
        
        # Process each paper
        for i, link in enumerate(search_results, 1):
            try:
                context, image, title = scrape_method(link)
                
                # Create individual report
                report = f"Paper {i}\n"
                report += f"Title: {title}\n\n"
                report += f"Context: {context}\n\n"
                report += f"Image: {image}\n\n"
                report += f"Link: {link}\n\n"
                report += f"{'---'*20}\n\n"
                
                # Append to file (use 'a' mode to add to existing content)
                with open(report_name, "a", encoding='utf-8') as f:
                    f.write(report)
                
                # Store for return value
                all_reports.append(report)
                
                print(f"✓ Processed paper {i}: {title[:50]}...")
                
            except Exception as e:
                error_report = f"Paper {i} - ERROR\n"
                error_report += f"Link: {link}\n"
                error_report += f"Error: {str(e)}\n\n"
                error_report += f"{'---'*20}\n\n"
                
                # Append error to file
                with open("report.txt", "a", encoding='utf-8') as f:
                    f.write(error_report)
                
                print(f"✗ Error processing paper {i}: {e}")
        
        # Add summary at the end
        summary = f"\nSUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total papers processed: {len(search_results)}\n"
        summary += f"Successful extractions: {len(all_reports)}\n"
        summary += f"Failed extractions: {len(search_results) - len(all_reports)}\n"
        
        with open("report.txt", "a", encoding='utf-8') as f:
            f.write(summary)
        
        # Return combined report
        combined_report = "".join(all_reports)
        return combined_report
    
    def run(self):
        search_queries = self.create_prompts()
        search_results = self.search_arxiv(search_queries)
        # self.create_report(search_results, report_name="abstract_only_report.txt", scrape_method=self._scrape_abstract)
        self.create_report(search_results, report_name="full_text_report.txt", scrape_method=self._scrape_full_text)

if __name__ == "__main__":
    retriever = ArxivAgent(query="Low Rank Adaptation of Large Language Models", max_results=5, ppq=5)
    retriever.run()
