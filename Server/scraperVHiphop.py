from craw_tool import html_downloader, html_parser,\
    html_outputer, url_manager, tkgui

class SpiderMain():
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.tkgui = tk_clientgui.TKGUI()
        self.hypertext_list = []
    def craw(self, root_url):
        count = 1
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
            # try:
            new_url = self.urls.get_new_url()
            print("craw %d : %s" % (count, new_url))
            html_cont = self.downloader.download(new_url)
            new_urls, new_data = self.parser.parse(new_url, html_cont)
            self.urls.add_new_urls(new_urls)
            if new_data is not None:
                self.hypertext_list.append((new_data['url'], new_data['title']))
            if count == 10:
                break
            count = count + 1
            # except:
            #     print("craw failed")
            #self.outputer.output_html()

        self.tkgui.update_hypertext(self.hypertext_list)
        self.tkgui.set_hypertext_button()
        self.tkgui.mainloop()

if __name__ == "__main__":
    root_url = "http://www.vhiphop.com/"
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)