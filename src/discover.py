import time
import random

# 多页异步爬虫 - 搜索包含特定关键词的对象
import aiohttp
import asyncio
from bs4 import BeautifulSoup

keywords = ["pic", "photos", "nu", "models"]
cookies = {
    "_ga": "GA1.2.1501793045.1747059635",
    "_gid": "GA1.2.904887784.1747059635",
    "AD_clic_b_POPUNDER": 1,
    "AD_jav_b_SM_B_728x90": 1,
    "AD_juic_b_SM_T_728x90": 2,
}
headers = {
    "referer": "https://btsow.pics/",
    "sec-ch-ua-platform": "Windows",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}


class Discover:
    def __init__(self, search_word):
        self.base_url = f"https://btsow.pics/search/{search_word}/page/"
        self.max_pages = 100

    async def fetch(self, session, url):
        try:
            # print(f"trying {url}")
            async with session.get(url, headers=headers, cookies=cookies) as response:
                return await response.text()
        except Exception as e:
            print(f"Requests failed: {url}, error: {e}")
            return None

    async def parse(self, html, page):
        if not html:
            return
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.select("div.col-xs-12.col-sm-8.col-lg-9.file")
        for div in divs:
            content = div.get_text(strip=True)
            for k in keywords:
                if k in content:
                    print(
                        f'Got {k} in "{content}" on {page} th page, click {self.base_url+str(page)} togo'
                    )

    async def crawl(self, page):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{page}"
            html = await self.fetch(session, url)
            await self.parse(html, page)
            await asyncio.sleep(random.uniform(0, 2))  # 随机延时，模拟人类操作

    async def main(self):
        tasks = [self.crawl(page) for page in range(1, self.max_pages + 1)]
        await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.main())


if __name__ == "__main__":
    Discover("Pthc").run()
