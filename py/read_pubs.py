import requests
import json
import re
# Optional: from bs4 import BeautifulSoup # Uncomment if using BeautifulSoup

# --- Configuration ---
INPUT_JSON_URL = "https://raw.githubusercontent.com/samapriya/awesome-gee-community-datasets/refs/heads/master/community_datasets.json"
OUTPUT_JSON_FILE = "community_datasets_with_publications.json"
# Set a timeout for web requests (in seconds)
REQUEST_TIMEOUT = 15
# User-Agent to mimic a browser
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Helper Functions ---

def fetch_json_data(url):
    """Fetches JSON data from a URL."""
    print(f"Fetching initial JSON from: {url}")
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching JSON from {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {url}: {e}")
        return None

def find_publication_url(doc_url):
    """
    Fetches content from the doc_url and searches for the 'Publication URL:'.
    Returns the found URL string or None.
    """
    if not doc_url or not doc_url.startswith(('http://', 'https://')):
        print(f"Skipping invalid doc URL: {doc_url}")
        return None

    print(f"  Fetching docs page: {doc_url}")
    try:
        response = requests.get(doc_url, timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        response.raise_for_status()
        content = response.text

        # --- Method 1: Simple String Search (Less Robust) ---
        # Look for "Publication URL:" followed by a URL
        # This regex looks for "Publication URL:" (case-insensitive)
        # possibly followed by whitespace, then captures the URL (starting with http/https).
        match = re.search(r'Publication URL:\s*(https?://[^\s<>"\'`]+)', content, re.IGNORECASE)
        if match:
            pub_url = match.group(1).strip()
            print(f"    Found Publication URL (regex): {pub_url}")
            return pub_url

        # --- Method 2: BeautifulSoup (More Robust - Uncomment to use) ---
        # soup = BeautifulSoup(content, 'html.parser')
        # # Example: Find a <p> or <div> tag containing "Publication URL:" and then find the <a> tag within it
        # # This needs adaptation based on the actual HTML structure of the doc pages
        # pub_tag = soup.find(lambda tag: tag.name in ['p', 'div', 'li', 'span'] and 'Publication URL:' in tag.get_text())
        # if pub_tag:
        #     link_tag = pub_tag.find('a', href=True)
        #     if link_tag:
        #         pub_url = link_tag['href']
        #         print(f"    Found Publication URL (BeautifulSoup): {pub_url}")
        #         return pub_url
        #     else:
        #          # Maybe the URL is just text after the label?
        #          text_after_label = pub_tag.get_text().split("Publication URL:")[1].strip()
        #          if text_after_label.startswith('http'):
        #               print(f"    Found Publication URL (BeautifulSoup, text): {text_after_label}")
        #               return text_after_label


        print(f"    'Publication URL:' not found on page: {doc_url}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"  Error fetching docs page {doc_url}: {e}")
        return None
    except Exception as e:
        # Catch potential parsing errors etc.
        print(f"  Error processing page {doc_url}: {e}")
        return None


def find_doi(publication_url):
    """
    Placeholder function to find a DOI based on a publication URL.
    This is complex and often requires specific APIs (e.g., CrossRef) or advanced scraping.
    Returns a DOI string or None.
    """
    if not publication_url:
        return None

    print(f"    Attempting to find DOI for: {publication_url}")

    # --- Potential Strategies (Implement one or more) ---
    # 1. Check if the URL itself contains a DOI:
    doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', publication_url, re.IGNORECASE)
    if doi_match:
        doi = doi_match.group(0)
        print(f"      Found potential DOI in URL: {doi}")
        return doi

    # 2. Fetch the publication page and search for DOI pattern:
    try:
        response = requests.get(publication_url, timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        response.raise_for_status()
        content = response.text
        # Look for common DOI patterns (e.g., "doi:10...", "https://doi.org/10...")
        doi_match = re.search(r'(doi:?\s*|https?://doi\.org/)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', content, re.IGNORECASE)
        if doi_match:
            doi = "10."+ doi_match.group(2).split("10.", 1)[-1] # Extract the DOI part starting with 10.
            print(f"      Found DOI on page: {doi}")
            return doi
    except requests.exceptions.RequestException as e:
        print(f"      Error fetching publication page {publication_url}: {e}")
    except Exception as e:
        print(f"      Error processing publication page {publication_url}: {e}")


    # 3. Use an API (e.g., CrossRef): Requires libraries like 'habanero'
    #    from habanero import Crossref
    #    cr = Crossref()
    #    try:
    #        # This is a metadata search, might not always link URL to DOI directly
    #        results = cr.works(query=publication_url, limit=1)
    #        if results['message']['items']:
    #            doi = results['message']['items'][0].get('DOI')
    #            if doi:
    #                 print(f"      Found DOI via CrossRef API: {doi}")
    #                 return doi
    #    except Exception as e:
    #        print(f"      Error querying CrossRef API: {e}")

    # 4. Fallback: Construct a Google Search query (requires manual intervention or scraping Google)
    #    search_query = f'"doi" "{publication_url}"'
    #    print(f"      Consider searching for DOI manually, e.g., Google search for: {search_query}")


    print(f"    DOI not automatically found for {publication_url}")
    return None

# --- Main Script Logic ---

def main():
    original_data = fetch_json_data(INPUT_JSON_URL)
    if not original_data:
        print("Failed to retrieve or parse the initial JSON. Exiting.")
        return

    if not isinstance(original_data, list):
        print("Expected a list of datasets in the JSON, but got a different structure. Exiting.")
        return

    new_data = []
    print(f"\nProcessing {len(original_data)} datasets...")

    for index, item in enumerate(original_data):
        print(f"\n--- Processing item {index+1}: {item.get('title', 'No Title')} ---")
        if not isinstance(item, dict):
            print("  Skipping item - not a dictionary.")
            continue

        new_item = item.copy() # Start with original data

        doc_url = item.get("docs")
        publication_url = None
        doi = None

        if doc_url:
            publication_url = find_publication_url(doc_url)
            if publication_url:
                new_item["publication_url"] = publication_url
                # Only search for DOI if we found a publication URL
                doi = find_doi(publication_url)
                if doi:
                    new_item["doi"] = doi
            else:
                 new_item["publication_url"] = None # Explicitly add null if not found
                 new_item["doi"] = None
        else:
            print("  No 'docs' URL found in this item.")
            new_item["publication_url"] = None # Explicitly add null if no docs url
            new_item["doi"] = None


        new_data.append(new_item)

    print(f"\n--- Finished processing. Writing output to {OUTPUT_JSON_FILE} ---")

    try:
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        print("Successfully wrote updated JSON data.")
    except IOError as e:
        print(f"Error writing output JSON file: {e}")
    except TypeError as e:
        print(f"Error serializing data to JSON: {e}")

if __name__ == "__main__":
    main()
