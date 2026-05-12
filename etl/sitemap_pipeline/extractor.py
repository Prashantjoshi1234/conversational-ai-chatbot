import requests
import xml.etree.ElementTree as ET
import hashlib 
import json
import logging
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

#----------- Logger Configuration -------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sitemap_extracter.log")

# ---------- CONSOLE HANDLER ----------
console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.handlers:
     logger.addHandler(file_handler)
     logger.addHandler(console_handler)


#----------- Directory Location ------------

sitemap_url = "https://klearcom.com/sitemap.xml"

STATE_FILE_DIR = "data/raw_sitemap_files/sitemap_state.json"

OUTPUT_DIR = "data/raw_sitemap_files"

os.makedirs(OUTPUT_DIR, exist_ok=True)

DELAY = 1
TIMEOUT = 15
REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (RAG-ETL-Crawler/1.0)"
}


#------------------------------ Helper Funcions ----------

def sha256(text :str):
    return hashlib.sha256(text.encode()).hexdigest()

def URL_HASH(url):
    return hashlib.sha256(url.encode()).hexdigest()

def load_state():
    if os.path.exists(STATE_FILE_DIR):
        with open(STATE_FILE_DIR, "r", encoding="utf-8")as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE_DIR, "w", encoding="utf-8") as f:
        json.dump(state, f, indent = 2)


def safe_txt_filename(url):
    path = urlparse(url).path.strip("/").replace("/", "_")
    if not path:
        path = "home"
    return f"{path}.txt"

def clean_text(text : str):           #This will remove extra spaces from text
    return " ".join(text.split())

def remove_noise(soup):
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

def extract_text(soup):
    blocks = []
    for tag in soup.find_all(["h1","h2","h3","h4","h5","h6","p","li"]):
        text = clean_text(tag.get_text())
        if len(text)>20:
            blocks.append(text)

    return "\n".join(blocks)


def fetch_url_list():
    urls = []
    try:
        response = requests.get(sitemap_url, timeout=10)
        xml_data = response.content
        root = ET.fromstring(xml_data)
 
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        

        for url in root.findall("ns:url", ns):

            loc = url.find("ns:loc", ns)
            if loc is not None:
                urls.append(loc.text)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error Requesting file : {e}")

    return urls



#--------- MAIN METHOD ------------------------------------------

def run_extracter():

    url_list = fetch_url_list()

    logger.info("sitemap_extractor log started")

    state = load_state()

    saved_pages = 0

    for url in url_list:
    
        url_hash = URL_HASH(url)

        logger.info(f"crawling of {url} has started")

        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT )
            if response.status_code != 200:
                logger.error(f"Failed URL: {url} | Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "lxml")
            remove_noise(soup)
            text = extract_text(soup)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} | {e}")
            continue
        except Exception as e:
            logger.error(f"Error Parsing for {url} : {e}")
            continue


        if not text:
            logger.info(f"There is no text available for {url}")
            continue

        content_hash = sha256(text)

        if url_hash in state:
            if state[url_hash]["content_hash"] == content_hash:
                logger.info("NO CHANGE (skipped) ")
                continue
            else:
                logger.info(f"CONTENT CHANGED → updating: {url}")

        else:
            logger.info(f" NEW PAGE : {url}")

        filename = safe_txt_filename(url)
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)

        except Exception as e:
            logger.error(f"File write failed for {url}: {e}")
            continue

        state[url_hash] = {
            "url" : url,
            "content_hash" : content_hash,
            "file" : filename
        }

        saved_pages += 1


        time.sleep(DELAY)

       

    save_state(state)
    

    logger.info("\n===================================")
    logger.info("CRAWL FINISHED SUCCESFULLY")
    logger.info(f"PAGES SAVED {saved_pages}")
    logger.info(f"state entries {len(state)}")
    logger.info("====================================\n")





 








