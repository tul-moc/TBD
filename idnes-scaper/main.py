import asyncio
import aiohttp
import idnes_handler

COOKIES = {'kolbda': '1'}
URL_PARAMS = '?datum=&idostrova=idnes'
BASE_URL = 'https://www.idnes.cz/zpravy/archiv/'
MAX_RETRIES = 3
TIMEOUT = aiohttp.ClientTimeout(total=10)
CHUNK_SIZE = 10

unique_article_urls = set()

async def fetch(session, url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            async with session.get(url, cookies=COOKIES, timeout=TIMEOUT) as response:
                return await response.text()
        except Exception as e:
            print(f"There was an error fetching the url: {url} - retrying {retries+1}")
            retries += 1
            await asyncio.sleep(5)
    return None 

async def get_article_urls(session, size):    
    tasks = []
    for i in range(size, size + CHUNK_SIZE):
       url = BASE_URL + str(i) + URL_PARAMS
       tasks.append(fetch(session, url))

    responses = await asyncio.gather(*tasks)

    article_urls = set()
    for data in responses:
       if data:
           article_urls.update(idnes_handler.parse_article_urls(data))

    return article_urls

async def process_articles(session, article_urls):
    tasks = []
    for url in article_urls:
        tasks.append(fetch(session, url))
    
    responses = await asyncio.gather(*tasks)

    for data in responses:
        if data:
            idnes_handler.parse_article(data)

async def scrape_idnes():
    global unique_article_urls
    print('Starting scraping')
    async with aiohttp.ClientSession() as session:
        for chunk in range(1, 42002, CHUNK_SIZE):
            print(f'Processing chunk {chunk} - {chunk+CHUNK_SIZE}')

            article_urls = await get_article_urls(session, chunk)
            new_urls = article_urls - unique_article_urls
            unique_article_urls.update(new_urls)

            if new_urls:
                await process_articles(session, new_urls)
                idnes_handler.save_articles()

if __name__ == '__main__':
    asyncio.run(scrape_idnes())
