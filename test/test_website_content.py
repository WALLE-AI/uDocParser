import os
import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# URL of the website
base_url = "https://huggingface.co/Papers"
# base_url = "https://huggingface.co/papers/2407.20743"

# Directory to save downloaded PDFs
download_dir = "downloaded_pdfs"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set to store visited URLs to avoid downloading the same PDF multiple times
visited_urls = set()

# Function to download a file
def download_file(url, download_dir):
    local_filename = os.path.join(download_dir, url.split('/')[-1])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def re_pattern(url):
    pattern = r'https://huggingface\.co/papers/[0-9]+\.[0-9]+'
    match = re.search(pattern, url)
    return match

def process_url(url):
    axiv_pdf_id = url.split("https://huggingface.co/papers/")
    axiv_pdf_id = axiv_pdf_id[1].split("#community")
    axiv_pdf_url = "https://arxiv.org/pdf/" + axiv_pdf_id[0] +".pdf"
    return axiv_pdf_url
# Function to find and download all PDFs from a webpage
def find_pdfs_and_links(url, download_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    pdf_links = set()
    other_links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            full_url = urljoin(url, href)
            ##正则匹配一下文档
            if full_url.endswith(".pdf") or re_pattern(full_url):
                pdf_links.add(process_url(full_url))
            elif urlparse(full_url).netloc == urlparse(base_url).netloc:  # Check if the link is within the same domain
                other_links.append(full_url)

    return pdf_links, other_links

# Recursive function to crawl the website and download PDFs
def crawl_website(url, download_dir):
    if url in visited_urls:
        return
    visited_urls.add(url)
    print(f"Visiting: {url}")

    pdf_links, other_links = find_pdfs_and_links(url, download_dir)

    for pdf_link in pdf_links:
        if pdf_link not in visited_urls:
            visited_urls.add(pdf_link)
            print(f"Downloading PDF: {pdf_link}")
            download_file(pdf_link, download_dir)
            time.sleep(1)  # Be polite and avoid overloading the server

    for link in other_links:
        crawl_website(link, download_dir)


def test_example():
    # Start the crawling process
    crawl_website(base_url, download_dir)