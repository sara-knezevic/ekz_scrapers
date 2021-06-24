import difflib
import os

from toolkit.scraping import *
from DriveAPI import DriveAPI
from toolkit.file_upload import *
from toolkit.mailer import Mailer
import constants
import logging
import time

def main(mailer, gdrive):
    # Main function that goes through website links and scrapes new versions.

    all_folders = get_all_folders(constants.DATA_PATH)
    all_websites = get_websites()

    for website in all_websites:
        url = website["url"].rstrip()
        name = website["name"]
        selector = website["selector"]

        all_files = get_all_files((os.path.join(constants.DATA_PATH, name)))
        if (name + ".html" in all_files) and (selector['pages'] == 1):
            try:
                path = os.path.join(constants.DATA_PATH, name, name + ".html")

                older_version = open(path, "r", encoding="utf8").read()
                current_version = get_data(name, name, url, selector)

                difference = get_difference(older_version, current_version)

                if not difference:
                    logger.info("%s: No changes!", name)
                else:
                    logger.info("%s: changed!", name)

                    # inserts, deletions = get_inserts_and_deletions(difference, older_version, current_version)
                    get_changes(mailer, url, difference)

                    if (website["fileUpload"]):  # and inserts):
                        upload_files_to_drive(current_version, website["fileSelector"], name, gdrive)

                    website_file = open(path, "w", encoding="utf8")
                    website_file.write(current_version)
                    website_file.close()
            except Exception as e:
                logger.info("Exception caught in ::: %s", name)
                logger.exception(e)
                print (e)
                # continue

            time.sleep(10)
            # Do deep scraping even if the main page returns !200.
            if (selector["deepScrape"]):
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

                        website_piece = get_data(name, link_name, deep_selector["link_prefix"] + link_url,
                                                 {"name": "div", "attrs": {"id": "main"}})

                        deep_path = os.path.join(constants.DATA_PATH, name, link_name + ".html")
                        older_version_deep = open(deep_path, "r", encoding="utf8").read()

                        difference_deep = get_difference(older_version_deep, website_piece)

                        if difference_deep:
                            logger.info("%s changed!", link_name)

                            title = BeautifulSoup(website_piece, "lxml").select(deep_selector["deepName"])[0].text.strip()

                            get_changes(mailer, deep_selector["link_prefix"] + link_url, difference_deep)

                            if deep_selector["deepFileUpload"]:  # and inserts:
                                upload_files_to_drive(website_piece, deep_selector["deepFileSelector"], name, gdrive, title)

                            piece_file = open(deep_path, "w", encoding="utf8")
                            piece_file.write(website_piece)
                            piece_file.close()

                        else:
                            logger.info("%s: No changes!", link_name)
                    except Exception as e:
                        logger.info("Exception caught in ::: %s", link_name)
                        logger.exception(e)
                        continue

        elif selector["pages"] != 1:
            try:
                num_of_pages = get_num_of_pages(url, selector["pages"])
            except Exception as e:
                logger.info("Exception caught in getting the number of pages!")
                logger.exception(e)
                continue

            for page_num in range(1, num_of_pages + 1):
                try:
                    paged_name = name + "_page_{}".format(page_num)
                    paged_url = url + "{}/".format(page_num)

                    if (paged_name + ".html" in all_files):
                        path = os.path.join(constants.DATA_PATH, name, paged_name + ".html")

                        older_version = open(path, "r", encoding="utf8").read()
                        current_version = get_data(name, paged_name, paged_url, selector)

                        difference = get_difference(older_version, current_version)

                        if not difference:
                            logger.info("%s: No changes!", paged_name)
                        else:
                            logger.info("%s: changed!", paged_name)

                            # inserts, deletions = get_inserts_and_deletions(difference, older_version, current_version)
                            if (page_num == 1):
                                get_changes(mailer, paged_url, difference)
                            else:
                                get_changes(mailer, paged_url, difference, page_num)

                            if (website["fileUpload"]):  # and inserts):
                                upload_files_to_drive(current_version, website["fileSelector"], name, gdrive)

                            website_file = open(path, "w", encoding="utf8")
                            website_file.write(current_version)
                            website_file.close()
                except Exception as e:
                    logger.info("Exception caught in ::: %s", paged_name)
                    logger.exception(e)
                    continue


def logging_func():

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(constants.LOGGER_PATH, "w", "utf-8")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(u'%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


if __name__ == "__main__":
    gdrive = DriveAPI()
    mailer = Mailer()

    logger = logging_func()

    init_data(gdrive)
    main(mailer, gdrive)

    log_msg = mailer.create_message_with_attachment("me", "lost.func@gmail.com", "EKŽ Logger", "", constants.LOGGER_PATH)
    mailer.send_message(log_msg)