import arxiv
from datetime import datetime
from langchain_community.retrievers import ArxivRetriever
from langchain_community.document_loaders import ArxivLoader

class ArxivScraper:
    '''
    This class takes a dict of urls and creates a report returns it and saves it to a file.

    Input:
        - urls: dictionary of query and the corresponding urls
        {
            "query1": [url1, url2, url3],
            "query2": [url4, url5, url6],
            "query3": [url7, url8, url9]
            ...
        }

    Output:
        - report: string of the report
    '''

    def __init__(self, urls, load_max_docs=1, scrape_method='abstract', report_name="scrape_results.txt"):
        self.urls = urls
        self.load_max_docs = load_max_docs
        self.scrape_method = scrape_method
        self.report_name = report_name

    def _scrape_abstract(self, link):
        query = link.split("/")[-1]
        retriever = ArxivRetriever(load_max_docs=self.load_max_docs, doc_content_chars_max=None)
        docs = retriever.invoke(query)

        # Include the published date and author to provide additional context, 
        # aligning with APA-style formatting in the report.
        context = f"Published: {docs[0].metadata['Published']}; Author: {docs[0].metadata['Authors']}; Content: {docs[0].page_content}"
        image = []
        
        return context, image, docs[0].metadata["Title"]

    def _scrape_full_text(self, link):
        # Load full paper content
        query = link.split("/")[-1]
        loader = ArxivLoader(query=query, load_max_docs=1)
        docs = loader.load()

        context = f"Published: {docs[0].metadata['Published']}; Author: {docs[0].metadata['Authors']}; Content: {docs[0].page_content}"
        image = []

        return context, image, docs[0].metadata["Title"]
    
    def _set_scrape_method(self):
        if self.scrape_method == 'abstract':
            scrape_method = self._scrape_abstract
        elif self.scrape_method == 'full_text':
            scrape_method = self._scrape_full_text
        else:
            raise ValueError(f"Invalid scrape method: {self.scrape_method}")
        
        return scrape_method
        
    def create_report(self, search_results):
        scrape_method = self._set_scrape_method()
        all_reports = []  # Store all individual reports
        
        # Calculate total papers across all queries
        total_papers = sum(len(urls) for urls in search_results.values())
        
        # Clear the file at the beginning
        with open(self.report_name, "w", encoding='utf-8') as f:
            f.write(f"ArXiv Research Report\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Queries: {len(search_results)}\n")
            f.write(f"Total Papers: {total_papers}\n")
            f.write(f"{'='*60}\n\n")
        
        paper_counter = 1
        successful_extractions = 0
        failed_extractions = 0
        
        # Process each query and its papers
        for query, urls in search_results.items():
            try:
                # Add query section header
                query_header = f"QUERY: {query}\n"
                query_header += f"Papers found: {len(urls)}\n"
                query_header += f"{'='*60}\n\n"
                
                with open(self.report_name, "a", encoding='utf-8') as f:
                    f.write(query_header)
                
                print(f"\n📋 Processing query: {query}")
                print(f"   Found {len(urls)} papers")
                
                # Process each paper for this query
                for url in urls:
                    try:
                        context, image, title = scrape_method(url)
                        
                        # Create individual report
                        report = f"Paper {paper_counter}\n"
                        report += f"Query: {query}\n"
                        report += f"Title: {title}\n\n"
                        report += f"Context: {context}\n\n"
                        report += f"Image: {image}\n\n"
                        report += f"Link: {url}\n\n"
                        report += f"{'---'*20}\n\n"
                        
                        # Append to file
                        with open(self.report_name, "a", encoding='utf-8') as f:
                            f.write(report)
                        
                        # Store for return value
                        all_reports.append(report)
                        successful_extractions += 1
                        
                        print(f"   ✓ Paper {paper_counter}: {title[:50]}...")
                        
                    except Exception as e:
                        error_report = f"Paper {paper_counter} - ERROR\n"
                        error_report += f"Query: {query}\n"
                        error_report += f"Link: {url}\n"
                        error_report += f"Error: {str(e)}\n\n"
                        error_report += f"{'---'*20}\n\n"
                        
                        # Append error to file
                        with open(self.report_name, "a", encoding='utf-8') as f:
                            f.write(error_report)
                        
                        failed_extractions += 1
                        print(f"   ✗ Error processing paper {paper_counter}: {e}")
                    
                    paper_counter += 1
                
                # Add spacing between queries
                with open(self.report_name, "a", encoding='utf-8') as f:
                    f.write(f"\n{'='*60}\n\n")
                    
            except Exception as e:
                print(f"✗ Error processing query '{query}': {e}")
                continue
        
        # Add summary at the end
        summary = f"\nSUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total queries processed: {len(search_results)}\n"
        summary += f"Total papers processed: {total_papers}\n"
        summary += f"Successful extractions: {successful_extractions}\n"
        summary += f"Failed extractions: {failed_extractions}\n"
        summary += f"Success rate: {(successful_extractions/total_papers*100):.1f}%\n" if total_papers > 0 else "Success rate: 0%\n"
        
        # Add query breakdown
        summary += f"\nQuery Breakdown:\n"
        for query, urls in search_results.items():
            summary += f"  • {query}: {len(urls)} papers\n"
        
        with open(self.report_name, "a", encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n📊 Report completed!")
        print(f"   Total papers: {total_papers}")
        print(f"   Successful: {successful_extractions}")
        print(f"   Failed: {failed_extractions}")
        print(f"   Success rate: {(successful_extractions/total_papers*100):.1f}%" if total_papers > 0 else "   Success rate: 0%")
        
        # Return combined report
        combined_report = "".join(all_reports)
        return combined_report
    

    def run(self):
        report = self.create_report(self.urls)
        return report


# Example Usage
if __name__ == "__main__":
    urls = {
    'Low Rank Adaptation of Large Language Models': ['http://arxiv.org/pdf/2405.10616v2', 'http://arxiv.org/pdf/2502.13568v1', 'http://arxiv.org/pdf/2312.03732v1', 'http://arxiv.org/pdf/2504.05343v2', 'http://arxiv.org/pdf/2402.10462v1'], 
    }

    scraper = ArxivScraper(urls, scrape_method='full_text', report_name="scrape_results.txt")
    scraper.run()

