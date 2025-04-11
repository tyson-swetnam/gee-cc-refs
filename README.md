# gee-cc-refs
building APA style references of the GEE Community Catalog

# GEE Community Datasets - Publication Link Extractor

This script (`read_pubs.py`) fetches dataset metadata from the Awesome GEE Community Datasets JSON file, visits the documentation URL for each dataset, attempts to extract the primary "Publication URL", and optionally searches for the corresponding DOI (Digital Object Identifier). It then outputs a new JSON file containing the original dataset information augmented with the found publication URLs and DOIs.

## Prerequisites

* [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Mamba](https://mamba.readthedocs.io/en/latest/installation.html) package manager installed. Mamba is recommended for faster environment solving and package installation.

## Installation

1.  **Clone or Download:** Get the script (`read_pubs.py`) and the environment file (`environment.yml`) into a local directory.

2.  **Create Conda Environment:** Open your terminal or Anaconda Prompt, navigate to the directory containing the files, and run the following command using Mamba:

    ```bash
    mamba env create -f environment.yml
    ```
    This will create a new conda environment named `read-pubs-env` with all the necessary packages (`python`, `requests`, `beautifulsoup4`, `lxml`, `habanero`).

3.  **Activate Environment:** Before running the script, activate the newly created environment:
    ```bash
    conda activate read-pubs-env
    ```

## Running the Script

Once the environment is activated, simply run the Python script from your terminal:

```bash
python read_pubs.py
```

The script will:
1.  Fetch the main JSON file from the configured URL.
2.  Iterate through each dataset entry.
3.  For each entry with a `docs` URL:
    * Fetch the documentation page.
    * Attempt to find a "Publication URL:" link using regular expressions (or BeautifulSoup if uncommented/customized).
    * If a Publication URL is found, attempt to find its DOI using various strategies (checking the URL, scanning the publication page, potentially using the CrossRef API via `habanero`).
4.  Print progress messages to the console.
5.  Write the results (original data + `publication_url` + `doi` fields) to `community_datasets_with_publications.json` in the same directory.

## Output

The script generates a file named `community_datasets_with_publications.json`. Each object in this JSON file corresponds to an original dataset entry, with two potential new fields:
* `publication_url`: The URL found by searching the `docs` page (or `null` if not found/applicable).
* `doi`: The DOI found based on the `publication_url` (or `null` if not found/applicable).

## Customization Notes

* **Web Scraping Reliability:** The functions `find_publication_url` and `find_doi` rely on searching web page content. The structure of websites varies greatly. You may need to inspect the HTML of the `docs` pages and `publication_url` pages and adjust the Python code (especially the regular expressions or BeautifulSoup selectors) for better accuracy.
* **DOI Finding:** Programmatically finding DOIs is challenging. The script provides several strategies, but none are guaranteed. Using the CrossRef API via `habanero` (included in the environment) might yield better results but requires understanding its usage and limitations. Manual verification or more sophisticated DOI finding services might be necessary for comprehensive results.
* **Rate Limiting/Blocking:** Running the script might involve making many web requests in quick succession. Some websites may temporarily block your IP address if they detect excessive requests. Consider adding delays (`time.sleep()`) between requests within the loop if you encounter issues.
