import socket
import sys
import logging
from craw_tool import tk_clientgui
import json
def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Wait_Flag = False

    # Setting logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(processName)s] [%(threadName)s] :  %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # connect to the server (change localhost to an IP address if necessary)
    while True:
        try:
            if len(sys.argv) is not 4:
                logger.error("you should set arguments, server name:localhost ,port number:55703.")
                return 0
            else:
                soc.connect((sys.argv[1], int(sys.argv[2])))
                logger.info("Connected to server at (%s, %s)" % (sys.argv[1], sys.argv[2]))
                break
        except ConnectionRefusedError:
            if Wait_Flag is False:
                logger.error("Cannot Connected to server at (%s, %s)" % (sys.argv[1], sys.argv[2]))
                return 0

    # Send a message to the server
    msg = sys.argv[3]
    msg = msg + "[END]"
    #logger.info(msg)
    msg = msg.encode("utf-8")
    soc.send(msg)
    logger.info("URL sent to the server")

    # Receive data from the server
    recieve_string = ""
    Info_Flag = True
    while True:
        while True:
            data = soc.recv(2048)
            data_decode = data.decode(("utf-8"))
            recieve_string = recieve_string + data_decode
            print(recieve_string)
            # All the message from client is recieved completely
            if recieve_string.find("[END]") != -1:
                break
        if recieve_string is not "[]":
            break
        if Info_Flag:
            Info_Flag = False
            logger.info("Waiting for Server Updating....")
    recieve_string = recieve_string[:-5]
    result = json.loads(recieve_string)


    # Always close the socket after use
    soc.close()
    hypertext_list = []

    for temp in result:
        hypertext_list.append((temp[0],temp[1],temp[2]))

    DISPLAY_NUM = 20
    if len(hypertext_list)>DISPLAY_NUM:
        hypertext_list = hypertext_list[:20]
    obj_tkgui = tk_clientgui.TKGUI()
    obj_tkgui.update_hypertext(hypertext_list)
    obj_tkgui.set_hypertext_button()
    obj_tkgui.set_picture()
    obj_tkgui.mainloop()

if __name__ == '__main__':
    main()