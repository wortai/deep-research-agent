# main_loader.py
import re
import logging
import os
from typing import List, Dict, Any, Optional

from langchain_community.document_loaders import (
    YoutubeLoader,
    GithubFileLoader,
    WebBaseLoader,
)

#importing package manually , error not resolved yet 


from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UniversalLoader:
    def __init__(self, github_access_token: Optional[str] = None):
        self.github_access_token = github_access_token
        # logging.info("UniversalLoader initialized.") # Reduced verbosity

    def _is_youtube_url(self, url: str) -> bool:
        # Checks if the given URL is a YouTube video URL.
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        return bool(re.match(youtube_regex, url))

    def _is_github_url(self, url: str) -> bool:
        # Checks if the given URL is a GitHub repository or file URL.
        # This regex will match base repo URLs like https://github.com/owner/repo
        # and also URLs with paths like https://github.com/owner/repo/tree/branch or /blob/branch/file
        github_regex = r'(https?://)?(www\.)?github\.com/([^/]+)/([^/]+)(/.*)?'
        return bool(re.match(github_regex, url))

    def _get_github_repo_details(self, url: str) -> Optional[Dict[str, str]]:
        # Extracts repository owner and name from a GitHub URL.
        # It expects loader_specific_kwargs to provide branch, file_filter, etc.
        match = re.match(r'(https?://)?(www\.)?github\.com/([^/]+)/([^/]+)(?:/.*)?', url)
        if match:
            # The first group after github.com is owner, second is repo name
            owner = match.group(3)
            repo = match.group(4)
            print(f"owner  {owner}  repo {repo}")
            return {"owner": owner, "repo": repo}
        return None







    def get_loader(self, url: str, loader_specific_kwargs: Optional[Dict[str, Any]] = None) -> Any:
        if loader_specific_kwargs is None:
            loader_specific_kwargs = {}

        # logging.info(f"Determining loader for URL: {url}") # Reduced verbosity

        try:
            if self._is_youtube_url(url):
                # logging.info(f"Identified YouTube URL. Using YoutubeLoader for {url}")
                params = {
                    "add_video_info": False,
                    "language": ["en"], # Default language preference
                    "translation": "en", # Default translation
                    **loader_specific_kwargs
                }
                return YoutubeLoader.from_youtube_url(url, **params)

            elif self._is_github_url(url):
                # logging.info(f"Identified GitHub URL. Using GithubFileLoader for {url}")
                repo_details = self._get_github_repo_details(url)
                if not repo_details:
                    raise ValueError(f"Could not parse GitHub repository owner/name from URL: {url}")

                # Ensure 'branch' is provided, default if not. 'file_filter' is highly recommended.
                if "branch" not in loader_specific_kwargs:
                    loader_specific_kwargs["branch"] = "master" # Common default
                    logging.warning(f"GitHub 'branch' not specified for {url}, defaulting to 'master'.")
                
                if "file_filter" not in loader_specific_kwargs:
                    logging.warning(f"GitHub 'file_filter' not specified for {url}. This might load many files or fail.")
                    # Default to no filter, which loads all files if not specified by user.
                    # User should ideally always provide a file_filter.

                params = {
                    "repo": f"{repo_details['owner']}/{repo_details['repo']}",
                    "access_token": self.github_access_token,
                    "github_api_url": "https://api.github.com", # Default API URL
                    **loader_specific_kwargs # Branch, file_filter, etc. are expected here
                }
                return GithubFileLoader(**params)

            else:
                # logging.info(f"Identified generic web URL. Using WebBaseLoader for {url}")
                params = {
                    "requests_per_second": 2, # Sensible default
                    "continue_on_failure": True, # Important for robustness
                    **loader_specific_kwargs
                }
                return WebBaseLoader(web_paths=[url], **params)
        except Exception as e:
            logging.error(f"Error creating loader for URL {url}: {e}")
            raise # Re-raise the exception to be caught by load_data or the caller







    def load_data(self, url: str, loader_specific_kwargs: Optional[Dict[str, Any]] = None) -> List[Document]:
        if loader_specific_kwargs is None:
            loader_specific_kwargs = {}


        try:
            loader = self.get_loader(url, loader_specific_kwargs)
            logging.info(f"Loading data from {url} with {type(loader).__name__}...")
            documents = loader.load()
            logging.info(f"Successfully loaded {len(documents)} document(s) from {url}.")
            return documents
        except Exception as e:
            # The error in get_loader will be caught here if it raises,
            # or new errors from loader.load() will be caught.
            logging.error(f"Failed to load data from {url}: {e}")
            raise


if __name__ == "__main__":
    # --- Configuration ---
    # Ensure GIT_HUB_TOKEN is set in your .env file or environment variables
    GITHUB_TOKEN = os.environ.get("GIT_HUB_TOKEN")

    if GITHUB_TOKEN is None:
        logging.warning("GIT_HUB_TOKEN environment variable not set. GitHubLoader might have limited access or be rate-limited.")

    universal_scraper = UniversalLoader(github_access_token=GITHUB_TOKEN)

    # --- Test Cases ---
    test_suite = [
        {

            "url": "https://www.youtube.com/watch?v=yD2JaAnMMo0", # Example: Lex Fridman
            "params": {"language": ["en"], "translation": "en"}
        },
        # {

        #     "url": "https://www.youtube.com/watch?v= माफी", # Example: 3Blue1Brown (Hindi title, check transcript)
        #     "params": {"language": ["hi", "en"], "translation": "en", "add_video_info": True}
        # },
        # {

        #     "url": "https://github.com/langchain-ai/langchain", # Base repo URL
        #     "params": {
        #         "branch": "master",
        #         "file_filter": lambda file_path: file_path.endswith((".md", ".ipynb")) and "docs/extras/" in file_path,
        #     }
        # },
        # {
     
        #     "url": "https://github.com/madhvantyagi/Mahfuzz_project",
        #     "params": {
        #         "branch": "main", # Assuming 'main' branch exists
        #         "file_filter": lambda file_path: file_path.endswith((".html")),
        #     }
        # },
        # {
   
        #     "url": "https://lilianweng.github.io/posts/2023-06-23-agent/",
        #     "params": {"requests_per_second": 1}
        # },
        # {

        #     "url": "https://thissitedefinitelyshouldnotexist12345xyz.com",
        #     "params": {} # WebBaseLoader will try and fail
        # }
    ]

    for item in test_suite:
        print(f"\n--- Testing  {item['url']} ---")
        try:
            docs = universal_scraper.load_data(item['url'], item['params'])
            print(f"Content loaded: {len(docs)} document(s).")
            if docs:
                # print(f"First document metadata: {docs[0].metadata}")
                print(f"First document content snippet: {docs[0].page_content[:1000]}...")
        except Exception as e:
            print(f"An error occurred during test for {item['url']}: {e}")
        print("-" * 40)

