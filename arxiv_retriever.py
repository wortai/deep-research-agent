'''
This script uses the Arxiv API to retrieve papers from Arxiv and extract the text from the PDF files.
It uses the PyPDF2 library to extract the text from the PDF files.

To run this script, you need to have the Arxiv API key.
You can get one from the Arxiv website.
'''

import os
import arxiv
from PyPDF2 import PdfReader
import shutil

class ArxivRetriever:
    def __init__(self, query, max_results=5):
        self.pdf_directory = 'papers'
        self.output_file = 'combined_papers.txt'
        self.query = query
        self.max_results = max_results

    # Delete Extracted File if already exists
    def delete_extraction_txt(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            print(f"Deleted existing file: {self.output_file}")

    # Delete PDF Directory
    def delete_extraction_pdfs(self):
        if os.path.exists(self.pdf_directory):
            for filename in os.listdir(self.pdf_directory):
                file = os.path.join(self.pdf_directory, filename)
                try:
                    if os.path.isfile(file) or os.path.islink(file):
                        os.remove(file)
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")

    def retrieve(self):
        client = arxiv.Client()

        search = arxiv.Search(
            query=self.query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
    
        for result in client.results(search):
            print(f"Title: {result.title}")
            # print(f"Authors: {[author.name for author in result.authors]}")
            # print(f"Abstract: {result.summary}")
            print(f"PDF Link: {result.pdf_url}\n")
        
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)
        
        result.download_pdf(dirpath=self.pdf_directory)

    def extract_text(self):
        # Open the output file in write mode
        with open(self.output_file, 'w', encoding='utf-8') as outfile:
            # Iterate over all files in the directory
            for filename in os.listdir(self.pdf_directory):
                if filename.lower().endswith('.pdf'):
                    pdf_path = os.path.join(self.pdf_directory, filename)
                    try:
                        # Open the PDF file
                        with open(pdf_path, 'rb') as pdf_file:
                            reader = PdfReader(pdf_file)
                            # Extract text from each page
                            for page_num, page in enumerate(reader.pages):
                                text = page.extract_text()
                                if text:
                                    outfile.write(f"\n--- {filename} - Page {page_num + 1} ---\n")
                                    outfile.write(text)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

        print(f"Extraction complete. Combined text saved to '{self.output_file}'.")


    def run(self):
        self.delete_extraction_txt()
        self.delete_extraction_pdfs()
        self.retrieve()
        self.extract_text()


if __name__ == "__main__":
    retriever = ArxivRetriever(query="large language models", max_results=1)
    retriever.run()