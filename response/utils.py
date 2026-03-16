import re
from typing import List, Dict
from urllib.parse import urlparse

def _extract_citation_label(title: str, url: str) -> str:
        """
        Derive a short citation label from the source title or URL.

        Tries the last segment of "X - Y - Z" title patterns (usually the publication name).
        Falls back to the domain hostname stripped of 'www.'.

        Args:
            title: The SOURCE TITLE from the search result.
            url: The SOURCE URL from the search result.

        Returns:
            Clean label like "Reuters", "Wikipedia", "CNBC".
        """
        if title and " - " in title:
            label = title.split(" - ")[-1].strip()
            if len(label) > 2:
                # Clean up known suffixes
                return re.sub(r'(?i)\.(com|org|net|co\.uk)$', '', label).strip()

        if title and " | " in title:
            label = title.split(" | ")[-1].strip()
            if len(label) > 2:
                return re.sub(r'(?i)\.(com|org|net|co\.uk)$', '', label).strip()

        try:
            host = urlparse(url).hostname or ""
            host = re.sub(r'^www\.', '', host)
            return host.split(".")[0].capitalize() if host else (title[:30] if title else "Source")
        except Exception:
            return title[:30] if title else "Source"

def _build_citation_map(entries: List[Dict[str, str]]) -> str:
        """
        Build a preformatted citation map from search result entries.

        Each line is a ready-to-copy markdown citation like:
        - [Reuters](https://reuters.com/article/xyz)

        The model is instructed to use these verbatim, preventing raw URL citations.

        Args:
            entries: List of dicts with 'label' and 'url' keys.

        Returns:
            Formatted citation map string.
        """
        seen = set()
        lines = []
        for entry in entries:
            url = entry["url"]
            if url in seen:
                continue
            seen.add(url)
            # Ensure label is clean
            clean_label = entry['label'].replace('[', '').replace(']', '')
            lines.append(f"- [{clean_label}]({url})")
        return "\n".join(lines) if lines else "No citations available."
