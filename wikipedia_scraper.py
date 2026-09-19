"""
wikipedia_scraper.py
====================
Talks to the Wikipedia API (MediaWiki Action API) and turns article
information into a Pandas DataFrame.

This module does the "behind the scenes" work:
  1. search_wikipedia()  -> finds article titles for a topic
  2. get_article_data()  -> collects details for one article
  3. build_dataset()     -> puts everything together in a DataFrame

It is used by app.py (the Streamlit user interface).
"""

import time

import pandas as pd
import requests

# Endpoint of the English Wikipedia API
API_URL = "https://en.wikipedia.org/w/api.php"

# Wikipedia asks every app to identify itself with a User-Agent header
HEADERS = {
    "User-Agent": "WikipediaDatasetBuilder/1.0 (beginner learning project)"
}


def _api_request(params, max_attempts=4):
    """Call the Wikipedia API and return the JSON answer as a dict.

    If Wikipedia answers with error 429 ("too many requests"), we wait
    a few seconds and try again instead of giving up.

    Raises ConnectionError when Wikipedia cannot be reached.
    """
    params = {"format": "json", **params}

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                API_URL, params=params, headers=HEADERS, timeout=15
            )
            if response.status_code == 429:
                # We are asking too fast -> wait, then try again
                wait_seconds = int(response.headers.get("Retry-After", 5))
                if attempt < max_attempts:
                    time.sleep(wait_seconds)
                    continue
            response.raise_for_status()  # turns 403/500/... into an exception
            return response.json()
        except (requests.RequestException, ValueError) as error:
            # Network problem, HTTP error, or the answer was not JSON
            if attempt < max_attempts:
                time.sleep(1)
                continue
            raise ConnectionError("Could not reach Wikipedia.") from error

    raise ConnectionError("Could not reach Wikipedia (rate limited).")


def search_wikipedia(query, limit=10):
    """Search Wikipedia and return a list of article titles."""
    data = _api_request(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        }
    )
    results = data.get("query", {}).get("search", [])
    titles = [result["title"] for result in results]

    # Remove duplicate titles while keeping the order (simple approach)
    unique_titles = []
    for title in titles:
        if title not in unique_titles:
            unique_titles.append(title)
    return unique_titles


def get_article_data(title):
    """Collect structured information about ONE Wikipedia article.

    Always returns a dictionary with all expected keys, so that an
    article with missing information produces empty values instead
    of an error.
    """
    data = {
        "Title": title,
        "URL": "",
        "Summary": "",
        "Categories": "",
        "Word Count": 0,
        "References Count": 0,
    }

    try:
        # One API call asks for everything we need:
        #   extracts   -> the plain text of the article
        #   info       -> the full Wikipedia URL
        #   categories -> the article categories
        #   extlinks   -> the external reference links of the article
        result = _api_request(
            {
                "action": "query",
                "titles": title,
                "redirects": 1,  # follow redirects automatically
                "prop": "extracts|info|categories|extlinks",
                "explaintext": 1,  # plain text instead of HTML
                "inprop": "url",
                "cllimit": "max",
                "clshow": "!hidden",  # skip hidden maintenance categories
                "ellimit": "max",
            }
        )

        # The answer contains a "pages" dictionary -> take the first page
        pages = result.get("query", {}).get("pages", {})
        if not pages:
            return data
        page = next(iter(pages.values()))
        if "missing" in page:  # the title does not exist as an article
            return data

        data["Title"] = page.get("title", title)
        data["URL"] = page.get("fullurl", "")

        text = page.get("extract", "") or ""
        if text:
            # The summary is the first paragraph of the article
            data["Summary"] = text.split("\n\n")[0].strip()
            data["Word Count"] = len(text.split())

        categories = []
        for category in page.get("categories", []):
            name = category["title"]
            if name.startswith("Category:"):
                name = name[len("Category:"):]  # remove the "Category:" prefix
            categories.append(name)
        data["Categories"] = ", ".join(categories)

        # External links are the sources/references used in the article
        data["References Count"] = len(page.get("extlinks", []))

    except Exception:
        # A problem with this single article -> return the empty values.
        # The app should keep working for the other articles.
        pass

    return data


def build_dataset(query, limit=10, progress_callback=None):
    """Search Wikipedia and build a DataFrame with article information.

    Parameters
    ----------
    query             : the topic typed by the user
    limit             : maximum number of articles to collect
    progress_callback : optional function(current, total, title) that the
                        app uses to update the progress bar

    Returns an empty DataFrame when no articles were found.
    """
    titles = search_wikipedia(query, limit)
    if not titles:
        return pd.DataFrame()

    # Fetch every article one by one and report progress
    rows = []
    for index, title in enumerate(titles, start=1):
        if progress_callback:
            progress_callback(index, len(titles), title)
        rows.append(get_article_data(title))
        if index < len(titles):
            # Short pause between articles so we stay below the
            # Wikipedia rate limit (error 429 = "too many requests")
            time.sleep(0.5)

    dataset = pd.DataFrame(rows)

    # Remove duplicate articles (same title found more than once)
    dataset = dataset.drop_duplicates(subset=["Title"]).reset_index(drop=True)
    return dataset
