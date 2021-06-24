# -*- coding: utf-8 -*-

import difflib
import json
import time
from os import listdir
from os.path import isfile, join, isdir
import difflib

from jinja2 import FileSystemLoader, Environment

from toolkit import make_html
from toolkit.file_upload import *

import main
logger = main.logging_func()

def get_websites():
    # Returns list of all websites information from json file

    with open(constants.JSON_PATH, encoding="utf-8") as data_file:
        data = json.load(data_file)

    return list(data["sites"])


def get_all_files(path):
    all_files_list = [f for f in listdir(path) if (isfile(join(path, f)))]
    return all_files_list


def get_all_folders(path):
    all_folders_list = [f for f in listdir(path) if (isdir(join(path, f)))]
    return all_folders_list


def get_data(folder_name, name, url, selector, init=False):
    page = requests.get(url)

    if (str(page.status_code).startswith('2')):
        soup = BeautifulSoup(page.content, "lxml")

        data = '\n'.join([str(s) for s in soup.find_all(selector["name"], selector["attrs"])])
        data = BeautifulSoup(data, "lxml").prettify()

        if init:
            path = os.path.join(constants.DATA_PATH, folder_name, name + ".html")
            _file = open(path, "w+", encoding="utf8")
            _file.write(data)
            _file.close()

        return data

    print (page)
    logger.info(page)
    raise Exception(page.status_code)


def get_difference(old_version, new_version):
    context_diff = []

    res = difflib.context_diff(old_version.splitlines(), new_version.splitlines(), n=4)

    for data in res:
        context_diff.append(data)

    return context_diff


def get_changes(mailer, website_url, context_diff, page=1):

    generated_html_from_context_diff = make_html.make_html_from_context_diff(context_diff, page)

    # Check if there's any text change in the differences
    if (generated_html_from_context_diff):
        logger.info(generated_html_from_context_diff)

        file_loader = FileSystemLoader(constants.TEMPLATE_PATH)
        env = Environment(loader=file_loader)

        template = env.get_template("site_changed.html")
        body = template.render(site_url=website_url, generated_content=generated_html_from_context_diff)

        # message = mailer.create_message("me", "lost.func@gmail.com, ekz@bos.rs", "EKŽ praćenje sajtova", body)
        message = mailer.create_message("me", constants.MAILTO, "EKŽ praćenje sajtova", body)

        mailer.send_message(message)


def init_data(gdrive):
    if not os.path.exists(constants.DATA_PATH):
        os.mkdir(constants.DATA_PATH)

    all_websites = get_websites()

    for website in all_websites:
        name = website["name"]

        if not check_existance(constants.DATA_PATH, name):
            create_directory(constants.DATA_PATH, name)

        if not gdrive.GetFolderID(name):
            gdrive.CreateFolder(name)

    for website in all_websites:
        name = website["name"]
        url = website["url"].rstrip()
        selector = website["selector"]
        pages = selector["pages"]

        if pages == 1:
            try:
                if (name + ".html") in get_all_files(os.path.join(constants.DATA_PATH, name)):
                    logger.info("%s.html already exists!", name)
                else:
                    current_version = get_data(name, name, url, selector, init=True)

                    if website["fileUpload"]:
                        upload_files_to_drive(current_version, website["fileSelector"], name, gdrive)

            except Exception as e:
                logger.info("Exception caught in ::: %s", name)
                logger.exception(e)
                print(e)

            time.sleep(10)

            if selector["deepScrape"]:
                try:
                    deep_selector = selector["deepSelector"]
                    html_data = get_data(name, name, url, deep_selector)
                    soup = BeautifulSoup(html_data, "lxml")
                except Exception as e:
                    logger.info("Exception caught in getting deep scrape links!")
                    logger.exception(e)
                    continue

                for link in soup.find_all(deep_selector["link_extractor"]):
                    try:
                        link_url = link.get(deep_selector["link_url"])
                        link_name = eval("'" + link_url + "'" + deep_selector["link_name"])

                        if (link_name + ".html") in get_all_files(os.path.join(constants.DATA_PATH, name)):
                            logger.info("%s.html already exists!", link_name)
                        else:
                            website_piece = get_data(name, link_name, deep_selector["link_prefix"] + link_url,
                                                     {"name": "div", "attrs": {"id": "main"}}, init=True) # these values are hardcoded for Javni uvid

                            title = BeautifulSoup(website_piece, "lxml").select(deep_selector["deepName"])[0].text.strip()

                            if deep_selector["deepFileUpload"]:
                                upload_files_to_drive(website_piece, deep_selector["deepFileSelector"], name, gdrive, title)

                    except Exception as e:
                        logger.info("Exception caught in ::: %s", link_name)
                        logger.exception(e)
                        continue

        elif pages != 1:
            try:
                num_of_pages = get_num_of_pages(url, pages)
            except Exception as e:
                logger.info("Exception caught in getting the number of pages!")
                logger.exception(e)
                continue

            for page_num in range(1, num_of_pages + 1):
                try:
                    paged_name = name + "_page_{}".format(page_num)
                    paged_url = url + "{}/".format(page_num)

                    if (paged_name + ".html") in get_all_files(os.path.join(constants.DATA_PATH, name)):
                        logger.info("%s.html already exists!", paged_name)
                    else:
                        get_data(name, paged_name, paged_url, selector, init=True)
                except Exception as e:
                    logger.info("Exception caught in ::: %s", paged_name)
                    logger.exception(e)
                    continue


def create_directory(path, name):
    os.mkdir(os.path.join(path, name))


def check_existance(path, name):
    return os.path.exists(os.path.join(path, name))


def get_num_of_pages(url, selector):
    page = requests.get(url)

    if (str(page.status_code).startswith('2')):
        soup = BeautifulSoup(page.content, "lxml")
        num_of_pages = int(soup.select(selector)[0].getText())

        return num_of_pages

    raise Exception(page.status_code)