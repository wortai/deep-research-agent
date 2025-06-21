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

from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# UniversalLoader class handles loading documents from various sources (YouTube, GitHub, Web).
# It takes an optional github_access_token for GitHub authentication.
# How to use:
# universal_loader = UniversalLoader(github_access_token="YOUR_GITHUB_TOKEN")
# docs = universal_loader.load_data("https://www.youtube.com/watch?v=yD2JaAnMMo0", {"language": ["en"]})
# docs = universal_loader.load_data("https://github.com/owner/repo", {"branch": "main", "file_filter": lambda f: f.endswith(".py")})
# docs = universal_loader.load_data("https://example.com/page")






class UniversalLoader:
    # Initializes the UniversalLoader with an optional GitHub access token.
    # Args:
    #   github_access_token (Optional[str]): Token for GitHub API authentication.
    def __init__(self, github_access_token: Optional[str] = None):
        self.github_access_token = github_access_token

    # Checks if the given URL is a YouTube video URL.
    # Args:
    #   url (str): The URL to check.
    # Returns:
    #   bool: True if the URL is a YouTube URL, False otherwise.
    def _is_youtube_url(self, url: str) -> bool:
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        return bool(re.match(youtube_regex, url))

    # Checks if the given URL is a GitHub repository or file URL.
    # Args:
    #   url (str): The URL to check.
    # Returns:
    #   bool: True if the URL is a GitHub URL, False otherwise.
    def _is_github_url(self, url: str) -> bool:
        github_regex = r'(https?://)?(www\.)?github\.com/([^/]+)/([^/]+)(/.*)?'
        return bool(re.match(github_regex, url))

    # Extracts repository owner and name from a GitHub URL.
    # Args:
    #   url (str): The GitHub URL.
    # Returns:
    #   Optional[Dict[str, str]]: A dictionary with 'owner' and 'repo' keys, or None if parsing fails.
    def _get_github_repo_details(self, url: str) -> Optional[Dict[str, str]]:
        match = re.match(r'(https?://)?(www\.)?github\.com/([^/]+)/([^/]+)(?:/.*)?', url)
        if match:
            owner = match.group(3)
            repo = match.group(4)
            print(f"owner  {owner}  repo {repo}")
            return {"owner": owner, "repo": repo}
        return None




    # Determines and returns the appropriate LangChain document loader based on the URL type.
    # Note: YouTube loading is currently in development and might not function as expected.
    # For GitHub URLs, if 'branch' is not specified, it defaults to 'master'.
    # If 'file_filter' is not specified, all files in the repository will be loaded, which can be inefficient.
    # Args:
    #   url (str): The URL to load.
    #   loader_specific_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments for the specific loader.
    # Returns:
    #   Any: An instance of a LangChain document loader (YoutubeLoader, GithubFileLoader, or WebBaseLoader).
    # Raises:
    #   ValueError: If a GitHub URL cannot be parsed.
    #   Exception: For other errors during loader creation.
    def get_loader(self, url: str, loader_specific_kwargs: Optional[Dict[str, Any]] = None) -> Any:
        if loader_specific_kwargs is None:
            loader_specific_kwargs = {}

        try:
            if self._is_youtube_url(url):
                # YouTube loader is still in working process.
                params = {
                    "add_video_info": False,
                    "language": ["en"],
                    "translation": "en",
                    **loader_specific_kwargs
                }
                return YoutubeLoader.from_youtube_url(url, **params)

            elif self._is_github_url(url):
                repo_details = self._get_github_repo_details(url)
                if not repo_details:
                    raise ValueError(f"Could not parse GitHub repository owner/name from URL: {url}")

                if "branch" not in loader_specific_kwargs:
                    loader_specific_kwargs["branch"] = "master"
                    logging.warning(f"GitHub 'branch' not specified for {url}, defaulting to 'master'.")
                
                if "file_filter" not in loader_specific_kwargs:
                    logging.warning(f"GitHub 'file_filter' not specified for {url}. This might load many files or fail.")

                params = {
                    "repo": f"{repo_details['owner']}/{repo_details['repo']}",
                    "access_token": self.github_access_token,
                    "github_api_url": "https://api.github.com",
                    **loader_specific_kwargs
                }
                return GithubFileLoader(**params)

            else:
                params = {
                    "requests_per_second": 2,
                    "continue_on_failure": True,
                    **loader_specific_kwargs
                }
                return WebBaseLoader(web_paths=[url], **params)
        except Exception as e:
            logging.error(f"Error creating loader for URL {url}: {e}")
            raise





    # Loads data from the specified URL using the determined loader.
    # Args:
    #   url (str): The URL from which to load data.
    #   loader_specific_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments for the loader.
    # Returns:
    #   List[Document]: A list of loaded LangChain Document objects.
    # Raises:
    #   Exception: If data loading fails.
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
            logging.error(f"Failed to load data from {url}: {e}")
            raise


if __name__ == "__main__":
    # --- Configuration ---
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
                print(f"First document content snippet: {docs[0].page_content[:1000]}...")
        except Exception as e:
            print(f"An error occurred during test for {item['url']}: {e}")
        print("-" * 40)
