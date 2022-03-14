import os.path, re, time
import requests
import lxml.html

chromedriver_path = r"C:\Users\z004dn0z\chromedriver.exe"
uk_base_url = "https://nats-uk.ead-it.com/cms-nats/opencms/en/Publications/AIP/"
pdf_url_templ = "https://www.aurora.nats.co.uk/htmlAIP/Publications/{date}-AIRAC/pdf/EG-{title}-en-GB.pdf"
titles = ['ENR-3.3', 'AD-2.EGEW', 'AD-2.EGBE', 'AD-2.EGNF', 'AD-2.EGES', 'AD-2.EGEN', 'AD-2.EGKK', 'AD-2.EGPN', 'AD-2.EGHF', 'AD-2.EGPB', 'AD-2.EGSH', 'ENR-1.11', 
    'GEN-2.2', 'ENR-1.14', 'AD-2.EGBJ', 'GEN-1.3', 'AD-2.EGTO', 'ENR-1.10', 'GEN-2.5', 'AD-2.EGTU', 'AD-2.EGCJ', 'AD-2.EGTC', 'ENR-4.5', 'AD-2.EGBD', 
    'AD-2.EGNT', 'AD-2.EGCC', 'AD-2.EGGD', 'AD-2.EGHC', 'AD-2.EGNV', 'AD-2.EGCF', 'GEN-0.1', 'AD-2.EGBP', 'AD-2.EGSF', 'ENR-4.4', 'ENR-5.4', 'AD-2.EGCV', 
    'AD-2.EGFF', 'AD-2.EGBK', 'AD-2.EGBM', 'AD-2.EGPC', 'AD-2.EGEL', 'AD-2.EGJB', 'AD-2.EGTR', 'AD-2.EGNX', 'AD-2.EGCL', 'GEN-2.3', 'GEN-1.4', 'AD-3.EGBC', 
    'GEN-2.7', 'GEN-1.6', 'GEN-0.6', 'AD-2.EGBB', 'AD-2.EGEC', 'AD-2.EGNO', 'AD-2.EGJA', 'GEN-3.3', 'ENR-2.1', 'ENR-5.6', 'AD-2.EGNJ', 'AD-2.EGCM', 
    'AD-2.EGMD', 'AD-2.EGHE', 'AD-2.EGSG', 'AD-2.EGFH', 'AD-2.EGPD', 'AD-2.EGFP', 'AD-2.EGBW', 'ENR-3.2', 'GEN-3.6', 'AD-2.EGPA', 'GEN-2.4', 'AD-2.EGMC', 
    'AD-2.EGGP', 'AD-2.EGBF', 'ENR-3.4', 'AD-2.EGPR', 'ENR-4.2', 'AD-2.EGPO', 'AD-3.EGHT', 'ENR-1.2', 'GEN-0.5', 'ENR-2.2', 'ENR-5.1', 'ENR-1.4', 'AD-2.EGLD', 
    'GEN-3.1', 'AD-2.EGHQ', 'AD-2.EGAD', 'AD-2.EGKA', 'AD-2.EGHO', 'AD-2.EGEO', 'AD-2.EGCN', 'AD-2.EGCK', 'AD-1.4', 'AD-2.EGED', 'AD-1.3', 'AD-2.EGAA', 
    'AD-2.EGNH', 'AD-2.EGLC', 'AD-2.EGPH', 'ENR-3.5', 'AD-2.EGSL', 'AD-2.EGSR', 'ENR-1.3', 'AD-2.EGJJ', 'AD-2.EGAE', 'AD-2.EGTB', 'AD-2.EGET', 'menu',
     'AD-2.EGKR', 'GEN-1.7', 'AD-2.EGNR', 'AD-2.EGNC', 'GEN-4.1', 'AD-2.EGNM', 'GEN-3.2', 'ENR-6', 'AD-2.EGPT', 'AD-1.5', 'AD-2.EGPE', 'ENR-1.8', 'ENR-5.2', 
     'AD-2.EGAC', 'AD-2.EGNL', 'AD-2.EGTE', 'ENR-1.1', 'AD-2.EGGW', 'AD-2.EGHH', 'ENR-5.5', 'AD-2.EGBS', 'AD-2.EGTH', 'AD-2.EGCB', 'GEN-3.5', 'ENR-5.3', 
     'ENR-1.7', 'ENR-1.12', 'GEN-2.1', 'AD-1.1', 'AD-2.EGPI', 'AD-2.EGLJ', 'AD-2.EGLK', 'AD-2.EGPU', 'AD-2.EGLM', 'AD-2.EGPF', 'GEN-0.4', 'AD-2.EGFE', 
     'AD-2.EGKB', 'GEN-0.2', 'AD-2.EGNW', 'AD-2.EGHR', 'ENR-1.13', 'AD-2.EGSC', 'AD-2.EGTK', 'GEN-2.6', 'AD-2.EGFA', 'GEN-3.4', 'GEN-1.2', 'GEN-1.5', 
     'AD-2.EGPL', 'AD-2.EGHI', 'AD-2.EGLL', 'ENR-3.6', 'ENR-1.5', 'ENR-1.9', 'AD-2.EGLF', 'AD-3.EGHK', 'GEN-1.1', 'AD-2.EGCW', 'AD-2.EGSU', 'AD-2.EGEP', 
     'GEN-0.3', 'AD-2.EGBO', 'AD-2.EGSS', 'AD-2.EGHG', 'AD-2.EGPG', 'ENR-1.6', 'ENR-3.1', 'AD-2.EGEY', 'AD-1.2', 'AD-2.EGEF', 'AD-3.EGLW', 'AD-2.EGPK', 
     'ENR-4.1', 'AD-2.EGKH', 'GEN-4.2', 'AD-2.EGNE', 'AD-2.EGTF', 'AD-2.EGSV', 'AD-2.EGNS', 'ENR-4.3', 'AD-2.EGSY', 'AD-2.EGBN', 'AD-2.EGER', 'AD-2.EGBG', 
     'AD-2.EGAB', 'AD-0.1', 'AD-2.EGHA', 'ENR-0.1']

os.makedirs("pdf", exist_ok=True)

def pdf_links():
    page = lxml.html.fromstring(requests.get(uk_base_url).content)
    current = page.xpath('//img[contains(@title, "CURRENT")]/../@href')[0]
    print(current)
    date = re.search(r".*/([0-9\-]+)\-[^0-9]+/.*", current).group(1)
    folder = rf"pdf\{date}"
    os.makedirs(folder, exist_ok=True)
    for title in titles:
        path = os.path.join(folder, f"EG-{title}-en-GB.pdf")
        if not os.path.exists(path):
            yield path , pdf_url_templ.format(date=date, title=title)

from utils import *

import aiofiles

def download_all():
    for batch in batches(list(pdf_links()), 8):
        paths, links = zip(*batch)
        async_download_get_all(links, paths)
        time.sleep(0.5)

start = time.time()
download_all()
stop = time.time()
print(stop - start, "seconds")