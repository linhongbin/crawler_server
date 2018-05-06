from bs4 import BeautifulSoup
import re
import urllib.parse
class HtmlParser(object):
    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        soup =  BeautifulSoup(html_cont, 'html.parser',
                              from_encoding='utf-8')
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        video_nodes = soup.find_all('div', class_="video-item")
        for node in video_nodes:
            new_url = node.div.a['href']
            new_full_url = urllib.parse.urljoin(page_url, new_url)
            new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data = {}

        # try:
        # url
        res_data['url'] = page_url
        #<dd class="lemmaWgt-lemmaTitle-title">
        title_node = soup.find('h2', class_ ="video-title")
        if title_node == None:
            return None


        res_data['title'] = title_node.get_text()

        view_node = soup.find('span', class_="view-count")
        if view_node == None:
            return None
        res_data['view'] = view_node.span.get_text()
        print("view_count: ", res_data['view'])

        return res_data