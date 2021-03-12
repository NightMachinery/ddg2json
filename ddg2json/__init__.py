# try:
#     from IPython import embed
# except:
#     pass
import traceback
import logging
import json
import sys
import os
from bs4 import BeautifulSoup
import urllib.parse


def main():
    ## inputs
    brish_mode = False
    if len(sys.argv) >= 2:  # otherwise reads stdin
        query = sys.argv[1]
        if query in ["-h", "--help"]:
            print(
                "Usage: ddg2json < HTML_of_the_query_page_of_DuckDuckGo\nOutput: JSON of the results in that HTML"
            )
            exit(0)
        brish_mode = True
    ##
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    logger = logging.getLogger(__name__)
    ##
    html = None
    if brish_mode:
        if not os.environ.get("NIGHTDIR"):
            logger.error(
                "You are trying to use the brish_mode, which needs my personal scripts loaded into your system (which you do not have currently). Aborting."
            )
            exit(1)

        from brish import z

        query_encoded = urllib.parse.quote(query)

        zres = z("ddg-html {query_encoded}")
        if not zres:
            logger.error(f"Could not download page for query '{query}'")
            exit(1)

        html = zres.outrs
    else:
        html = sys.stdin.read()

    soup = BeautifulSoup(html, features="lxml")
    results = soup.find("div", id="links")
    if not results:
        logger.error(f"Did not find div with id 'links' for query '{query}'")
        exit(1)
        results = results.find_all("div", "result__body")
        # embed() ; exit(0)
    processed = []
    for r in results:
        try:
            link = r.find("a", "result__a")
            if not link:
                continue
            url = link.get("href")
            if url.startswith("https://duckduckgo.com") or (not url.startswith("http")):
                continue
            title = link.getText(strip=True)
            snippet = ""
            try:
                snippet = r.find("div", "result__snippet").getText(strip=True)
            except:
                pass
            processed.append({"title": title, "url": url, "abstract": snippet})
        except:
            logger.warning(traceback.format_exc())

    print(json.dumps(processed))

    ### fast and dirty way to just get the titles and links:
    # html = z("eval-memoi withchrome full-html2 'https://duckduckgo.com/?q=lorde+site%3Ahttps%3A%2F%2Fopen.spotify.com%2Fartist%2F&t=h_&ia=web' | pup 'div.result .result__a '").outrs

    # soup = BeautifulSoup(html, features='lxml')

    # links = soup.find_all('a')
    # for link in links:
    #     url = link.get('href')
    #     if url.startswith('https://duckduckgo.com'):
    #         continue
    #     title = link.getText(strip=True)
    ###
