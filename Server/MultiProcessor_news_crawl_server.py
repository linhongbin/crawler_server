import socket
import sys
import logging
import json
import time
from craw_tool import html_downloader, html_parser,\
    html_outputer, url_manager, tk_clientgui

from multiprocessing import Process, Queue, Manager
import threadpool


def server_worker(client_socket, address, m_hypertext_list, index ):

    logger = logging.getLogger('logger'+str(index))
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s], [%(levelname)s], [%(processName)s], [%(threadName)s] :  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("Recieve Client ('%s', %s)." % (address[0], address[1]))

    recieve_string = ""

    # Read data from a client
    while True:
        data = client_socket.recv(2048)
        data_decode = data.decode(("utf-8"))
        recieve_string = recieve_string + data_decode
        # All the message from client is recieved completely
        if recieve_string.find("[END]") != -1:
            break
    recieve_string= recieve_string[:-5]
    logger.info("Client submitted URL %s" % recieve_string)

    hypertext_list = [k for k in m_hypertext_list]

    send_cont = json.dumps(hypertext_list) + "[END]"
    client_socket.sendall(send_cont.encode("utf-8"))
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
        self.MAX_CRAW_NUM = 30
        self.count = 0
    def craw(self, root_url):
        self.urls.add_new_url(root_url)
        while(self.urls.has_new_url()):
            new_url = self.urls.get_new_url()
            print("craw %d : %s" % (self.count, new_url))
            html_cont = self.downloader.download(new_url)
            new_urls, new_data = self.parser.parse(new_url, html_cont)
            self.urls.add_new_urls(new_urls)
            if new_data is not None:
                self.hypertext_list.append((new_data['url'], new_data['title'],new_data['view']))
            self.count = self.count + 1
            if self.count > self.MAX_CRAW_NUM:
                break

        return self.hypertext_list

def tcpServerProcess(connect_queue, m_hypertext_list):

    MAX_THREADING_NUM = 5
    pool = threadpool.ThreadPool(MAX_THREADING_NUM)
    index = 0
    try:
        while(True):
            (q_socket, q_address) = connect_queue.get()
            index = index + 1
            dic_vars = {'client_socket': q_socket, 'address': q_address, 'm_hypertext_list':m_hypertext_list, 'index': index }
            reqs = threadpool.makeRequests(server_worker, args_list=[(None, dic_vars),])
            for req in reqs:
                pool.putRequest(req)
    except:
        print("counter except, exit the process-" )
        pool.joinAllDismissedWorkers()


def crawProcess(m_hypertext_list):
    root_url = "http://www.vhiphop.com/"
    obj_craw = CrawMain()
    logger = logging.getLogger('logger_craw')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s], [%(levelname)s], [%(processName)s], [%(threadName)s] :  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    while(True):
        try:
            hypertext_list = obj_craw.craw(root_url)
            count = 0
            hypertext_list_sorted = sorted(hypertext_list, key=lambda x: int(x[2]),reverse=True)
            for hypertext in hypertext_list_sorted:
                if(len(m_hypertext_list)>=count+1):
                    m_hypertext_list[count] = hypertext
                else:
                    m_hypertext_list.append(hypertext)
                count = count + 1
            #logger.info("craw Process finish")
            print(m_hypertext_list)
            logger.info("update 1 minute later")
            time.sleep(60)
        except:
            logger.info("crawling failed")


def main():
    TCP_PROCESS_NUM = 3

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


    manager = Manager()


    m_hypertext_list = manager.list()

    p = Process(target=crawProcess, args=(m_hypertext_list, ))
    logger.info("Created process Craw Process")
    p.start()

    connect_queue = Queue()

    for i in range(TCP_PROCESS_NUM):
        p = Process(target=tcpServerProcess, args=(connect_queue,m_hypertext_list,))
        logger.info("Created process Server Process %d", i)
        p.start()

    count = 0

    while True:
        # Waiting for connection
        count = count + 1
        (client_socket, address) = server_socket.accept()
        connect_queue.put((client_socket, address))
        logger.info("Client ('%s', %s) connected." % (address[0], address[1]))

if __name__ == '__main__':
    main()
