import socket
import sys
import logging
import json
from craw_tool import html_downloader, html_parser,\
    html_outputer, url_manager, tk_clientgui
import threadpool

import threadpool

hypertext_list = []

def server_worker(client_socket, address, index,hypertext_list):

    logger = logging.getLogger('logger'+str(index))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s], [%(levelname)s], [%(processName)s], [%(threadName)s] :  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("Recieve Client ('%s', %s)." % (address[0], address[1]))

    recieve_string = ""

    # Read data from a client and send it response back
    while True:
        data = client_socket.recv(2048)
        data_decode = data.decode(("utf-8"))
        recieve_string = recieve_string + data_decode
        # All the message from client is recieved completely
        if recieve_string.find("[END]") != -1:
            break
    recieve_string= recieve_string[:-5]
    logger.info("Client submitted URL %s" % recieve_string)
    client_socket.sendall(json.dumps(hypertext_list).encode("utf-8"))
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    logger.info("Client connection closed")
    del logger

class CrawMain():
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
            if count == 2:
                break
            count = count + 1

        return self.hypertext_list

def crawThread():
    root_url = "http://www.vhiphop.com/"
    obj_craw = CrawMain()

    lock.acquire()
    hypertext_list = obj_craw.craw(root_url)
    lock.release()
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s], [%(levelname)s], [%(processName)s], [%(threadName)s] :  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("start")
    # bind the socket to the host and a port
    server_socket.bind(('localhost', int(sys.argv[1])))

    # Listen for incoming connections from clients
    server_socket.listen(10)

    root_url = "http://www.vhiphop.com/"
    obj_craw = CrawMain()
    hypertext_list = obj_craw.craw(root_url)

    count =0
    while True:
        count = count +1
        (client_socket, address) = server_socket.accept()
        logger.info("Client ('%s', %s) connected." % (address[0], address[1]))
        server_worker(client_socket, address, count ,hypertext_list)



if __name__ == '__main__':
    main()
