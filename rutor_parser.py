import requests
import webbrowser
import pickle
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, TypedDict
from os import path

proxies = {"http": "https://185.42.60.242:8080"}

class TorrentInfo(TypedDict):
    topic_name:     str
    torrent_name:   str
    magnet_link:    str
    torrent_link:   str
    creator_name:   str
    torrent_size:   str
    seeds:          str
    leeches:        str
    download_count: str
    created_at:     str
    tracker:        str


class OverallInfo(TypedDict):
    results_count: int
    start:         int
    results:       List[TorrentInfo]


class RutorParser:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'close',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate, lzma, sdch',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        self.cookie_fp = './cookies_rutor'
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.base_url = "http://rutor.info/search/"
        if Path(self.cookie_fp).is_file():
            self.session.cookies.update(pickle.load(open(self.cookie_fp, 'rb')))

    def search(self, query, start=0) -> OverallInfo:
        r = self.session.get(self.base_url+"/"+query, proxies=proxies)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.find("div", { "id" : "index" })#.find('table')
        unwanted = body.find(class_="backgr").extract()

        results: List[BeautifulSoup] = body.find_all('tr')
        results_count = int(body.find("b").next_sibling.split(' Результатов поиска ')[1].split('(max. 2000)')[0].strip())

        search_results = []
        if results_count == 0:
            return OverallInfo(
                results_count=0,
                start=0,
                results=[]
            )
        else:
            for result in results:
                data: List[BeautifulSoup] = result.find_all('td')
                topic_name = data[1].text
                torrent_name = data[1].text
                torrent_soup: BeautifulSoup = data[1]
                torrent_link = torrent_soup.find('a')['href']
                magnet_link = torrent_soup.find('a').next_element.next_element['href']
                torrent_size = data[2].text
                seeds = data[3].text.split()[0]
                leeches = data[3].text.split()[-1]
                created_at = data[0].text
                download_count=str(0)

                serialized = TorrentInfo(
                    topic_name=topic_name.strip(),
                    torrent_name=topic_name.strip(),
                    torrent_link=torrent_link.strip(),
                    magnet_link = magnet_link.strip(),
                    torrent_size=torrent_size.strip(),
                    seeds=seeds.strip(),
                    leeches=leeches.strip(),
                    download_count=download_count.strip(),
                    tracker = 'rutor.org'.strip(),
                    created_at=created_at.strip().replace(u'\xa0', ' ')

                )

                search_results.append(serialized)

        return OverallInfo(
            results_count=round(results_count),
            start=start,
            results=search_results
        )

    def dl_torrent(self, torrent: TorrentInfo, pth: str):
        r = self.session.get(torrent['torrent_link'], proxies=proxies)
        with open(path.join(pth, '{}.torrent'.format(torrent['topic_name'].replace("/","-"))), 'wb') as torrent_file:
            torrent_file.write(r.content)

    def get_magnet_link(self, selected_torrent: str) -> str:
        return selected_torrent['magnet_link']
