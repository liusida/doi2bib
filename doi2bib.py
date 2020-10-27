#!/usr/bin/env python
#
# get bibtex from doi.org using an online API
#
# bash version for geeks:
#   curl -LH "Accept: application/x-bibtex; charset=utf-8" https://doi.org/$1

# API = "doi.org"
# API = "data.crossref.org"
API = "data.crosscite.org"

import urllib.parse
import urllib.request
import urllib.error
import argparse
import re
import time

def main(args):
    if args.input_file is not None:
        with open(args.input_file.strip(), "r") as f:
            urls = f.readlines()
    else:
        urls = args.urls.split(" ")
    output_item = 0
    error_item = 0
    for url in urls:
        raw_dois = re.findall(pattern=r'10.\d{4,9}/[-._;()/:A-Za-z0-9]+', string=url)
        if raw_dois is None:
            continue
        for raw_doi in raw_dois:
            the_page = get_bib(raw_doi)
            output_item += 1
            if the_page is None:
                error_item += 1
            else:
                print(the_page)
    print(f"% {output_item} items in total.")
    print(f"% {error_item} items have errors.")

visited = {}
def get_bib(raw_doi, retry=10):
    global visited
    url = f"https://{API}/{raw_doi}"
    if url in visited:
        print(f"% Error: duplicated item {raw_doi}, ignored.")
        return None
    the_page = None
    while(retry):
        try:
            headers = {'Accept': 'application/x-bibtex; charset=utf-8'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                the_page = response.read().decode("utf-8")
            break
        except urllib.error.HTTPError as err:
            retry -= 1
            print(f"% Error when fetching {url}\n% {err}")
            time.sleep(3)
            continue
    visited[url] = True
    return the_page

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='doi2bib')
    parser.add_argument('urls', metavar='doi', type=str, default=[], nargs='?', help='doi url')
    parser.add_argument('-i', '--input-file', type=str, default=None, help="a file contains doi list")
    args = parser.parse_args()
    main(args)

