import io
# allows for image formats other than gif
from PIL import Image, ImageTk
# Python3
import tkinter as tk
import urllib.request
import webbrowser
from PIL import ImageTk, Image

class TKGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.hypertext_list = None
        self.title("VHiphop Express: Hot Videos")
    # def display_picture(self，pic_url,title):
    def update_hypertext(self, hypertext_list):
        self.hypertext_list = None
        self.hypertext_list = hypertext_list;

    def set_hypertext_button(self):
        if self.hypertext_list is None:
            return
        count = 0
        links = []
        for (url, title, view) in self.hypertext_list:
            count = count +1
            button = tk.Button(self, text=title+"    [View Count: "+view+" ]", command=GotoUrl(url))
            button.pack()

    def set_picture(self):
        img = ImageTk.PhotoImage(Image.open("vhiphop.jpg"))
        imglabel = tk.Label(self, image=img)
        imglabel.pack()

class GotoUrl(object):
    def __init__(self, url):



        self.url = url
    def __call__(self):
        print('goto', self.url)
        webbrowser.open_new(self.url)