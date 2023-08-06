from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os, sys
import requests
import csv
import re
from lxml import etree
import lxml.html as lh


class Parser:
    """
        :param url: - Url to scraping
        :param max_pages: max_pages on site
        :return:
    """

    def __init__(self, url, max_pages, final_file="parsed.csv", delimiter=";", save_image=True, init_imdb=1,
                 images_folder="images", files_folder="downloads",
                 csv_structure=('name', 'image')):
        self.URL = url
        self.MAX_PAGES = max_pages
        self.FINAL_FILE = final_file
        self.DELIMITER = delimiter
        self.SAVE_IMAGE = save_image
        self.CSV_STRUCTURE = csv_structure
        self.IMAGES_FOLDER = images_folder
        self.FILES_FOLDER = files_folder
        self.init_imdb = init_imdb + 1
        self.current_page = 1
        if not self.check_csv():
            self.create_csv()
        self.parse()

    def parse(self):
        pass

    def get_page(self, url):
        """
            Returns page soup
            :param url: - Url to get page soup
            :return: - HTML Soup
        """
        url = self.create_absolute_url(url)
        self.log("Getting page soup", 0)
        try:
            return bs(requests.get(url, headers=self.get_headers()).text, 'html.parser')
        except:
            self.log(f"[page_url: {url}]:Can't get page soup", 2)
            # self.close()

    def get_page_lxml(self, url):
        """
            Returns page HTML Tree
            :param url: - Url to get page HTML Tree
            :return: - HTML Tree
        """
        self.log("Getting page tree", 0)
        try:
            return etree.HTML(str(self.get_page(url)))
        except:
            self.log(f"[page_url: {url}]:Can't get page tree", 2)

    def get_string_from_html(self, html):
        """
            Returns string from HTML object
            :param html: - HTML object
            :return: - String
        """
        return lh.tostring(html)

    def get_headers(self):
        """
            Returns headers with random user-agent
            :return: - Dict
        """
        return {
            'User-Agent': UserAgent().random
        }

    def get_info_current_err(self):
        """
            Returns info of current exception
            :return: - String
        """
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return f" [{exc_type}, {fname}, {exc_tb.tb_lineno}]"

    def get_info_log_type(self, type):
        """
            Returns info of log-type number
            :param type: - Int
            :return: - String
        """
        list_of_types = {
            0: "Info",
            1: "Warning",
            2: "Error"
        }
        if type in list_of_types:
            return list_of_types[type]

    def search_id_in_csv(self, imdb):
        """
            Finding imdb id in parsed csv file
            :param imdb: - String
            :return: - Bool (found or no)
        """
        with open(self.FINAL_FILE, "r", encoding='utf-8', errors='ignore') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=self.DELIMITER)
            for row in reader:
                if row['imdb'] == imdb:
                    return True
        return False

    def check_csv(self):
        """
            Checking exists final csv file or no
            :return: - Bool (found or no)
        """
        return os.path.exists(self.FINAL_FILE)

    def create_absolute_url(self, url):
        """
            Creating absolute url if url is relative
            :param url: - String
            :return: - String (new url)
        """
        if url[0:4] != 'http':
            if url[0] == '/':
                url = url[1:]
            url = re.search(r"http\w+(://)[\w.]+", self.URL).group(0) + "/" + url
        return url

    def create_csv(self):
        """
           Creating final csv file
           :return: - None
        """
        with open(self.FINAL_FILE, 'w', encoding='utf-8', errors='ignore') as file:
            file.write(f"{self.DELIMITER}".join(self.CSV_STRUCTURE) + "\n")

    def add_element_to_csv(self, *args):
        """
           Adding element to final csv
           :param *any: - Fixed parameter order with CSV_STRUCTURE
           :return: - None
        """
        with open(self.FINAL_FILE, 'a', encoding='utf-8', errors='ignore') as file:
            file.write(f"{self.DELIMITER}".join(args) + "\n")
            print(f"Added film: {self.create_imdb()}")

    def create_imdb(self):
        """
           Creating imdb id with 20 symbols length
           :return: - String (20 symbols imdb)
        """
        return f"{self.init_imdb:020}"

    def download_image(self, url, name):
        """
           Downloading image from url and saving them to images folder
           :param url: - Url to image
           :param name: - Name for file
           :return: - None
        """
        self.download_file(url, name, ext="jpg", folder=self.IMAGES_FOLDER)

    def download_file(self, url, name, ext, folder):
        """
           Downloading file from url and saving them to folder
           :param url: - Url to image
           :param name: - Name for file
           :param ext: - Extension of file
           :param folder: - Folder name where file will be saved
           :return: - None
        """
        if not os.path.isdir(folder):
            os.mkdir(folder)
        if os.path.exists(f"{folder}/{name}.{ext}"):
            self.log(f"file with name:{name}.{ext} already exists", 0)
            return False
        url = self.create_absolute_url(url)

        self.log("Getting file by url", 0)
        file_dirty = requests.get(url, headers=self.get_headers())
        if file_dirty.status_code == 200:
            with open(f"{folder}/{name}.{ext}", 'wb') as image:
                image.write(file_dirty.content)
        else:
            self.log("Can't get file by url", 1)

    def clear_string(self, dirty_str):
        """
           Cleaning the string from unnecessary characters
           :param dirty_str: - Dirty string which must clear
           :return: - String (cleared string)
        """
        return re.sub("[;`\\\]", '', dirty_str.strip())

    def log(self, text, type):
        """
           Logging events on parser to .log file
           :param text: - Text which must save to log
           :param type: - Log type [0 - Info, 1 - Warning, 2 - Error]
           :return: - String (cleared string)
        """
        with open('Parser.log', 'a', encoding='utf-8', errors='ignore') as log:
            # Shit code
            log.write(
                f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} [{self.get_info_log_type(type)}] [page: {self.current_page}, imdb: {self.init_imdb}] :{text}{self.get_info_current_err() if type == 2 else ''} \n")

    def close(self):
        """
           Emergency closing program
           :return: - None
        """
        exit("Parser has been stopped, check `Parser.log` for get more info.")
