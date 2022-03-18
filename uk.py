import os.path, re, time
import requests
import lxml.html

uk_base_url = "https://nats-uk.ead-it.com/cms-nats/opencms/en/Publications/AIP/"
pdf_url_templ = "https://www.aurora.nats.co.uk/htmlAIP/Publications/{date}-AIRAC/pdf/EG-{title}-en-GB.pdf"
menu_url_templ = "https://www.aurora.nats.co.uk/htmlAIP/Publications/{date}-AIRAC/html/eAIP/EG-menu-en-GB.html"

os.makedirs("pdf", exist_ok=True)


def pdf_links():
    page = lxml.html.fromstring(requests.get(uk_base_url).content)
    current = page.xpath('//img[contains(@title, "CURRENT")]/../@href')[0]
    print(current)
    date = re.search(r".*/([0-9\-]+)\-[^0-9]+/.*", current).group(1)
    folder = os.path.join("pdf", date)
    os.makedirs(folder, exist_ok=True)

    page = lxml.html.fromstring(requests.get(menu_url_templ.format(date=date)).content)
    hrefs = page.xpath('//div[contains(@id, "details")]//a/@href')

    def _titles():
        for href in hrefs:
            try:
                title = href.split("#")[0].split("/EG-")[1].split("-en-GB")[0]
                yield title, None
            except Exception as ex:
                yield None, f"{href}: {ex}"

    titles, errors = zip(*list(_titles()))
    titles = list(set(filter(None, titles)))
    errors = list(set(filter(None, errors)))

    for error in errors:
        print(error)

    for title in titles:
        path = os.path.join(folder, f"EG-{title}-en-GB.pdf")
        if not os.path.exists(path):
            yield path, pdf_url_templ.format(date=date, title=title)


from utils import batches, async_download_get_all

import aiofiles


def download_all():
    for batch in batches(list(pdf_links()), 8):
        paths, links = zip(*batch)
        results = async_download_get_all(links, paths)
        time.sleep(0.5)
        for result, link in zip(results, links):
            if not result:
                print(result, link)


start = time.time()
download_all()
stop = time.time()
print(stop - start, "seconds")
