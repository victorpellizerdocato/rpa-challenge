"""

> Packages used to start the robot execution

logging - logs every relevant step
os - path handling
re - regex operations
datetime - multiple date operations
quote - changes whitespaces from queries
quote_plus - changes whitespaces to '+' from queries to be used in the url
Selenium - the browser used to scrape the web
DataHandling - class to handle the data scraped from the web

"""
import logging
import os
import re
from datetime import datetime
from urllib.parse import quote, quote_plus

from RPA.Browser.Selenium import Selenium

from src.utils.data_handling import DataHandling


class LATimesService():
    """
    Class where the LATimes website is scraped for data
    """
    def __init__(
        self
    ):
        self.data_handling = DataHandling()
        self.file_count = 3
        # file_count starts with 3 because I considered the 2 default
        # output files and the resulting sheet file.
        self.files_size = 1000000
        # files_size starts with this number because the sum of the
        # weight of the default output files is close to it.
        self.SIZE_LIMIT = 20000000
        self.browser = Selenium()

    def exec(
        self,
        payload: dict
    ) -> dict:
        """
        The main method of the class: opens then closes the browser,
        accesses the website, gathers HTML info, and calls the sheet
        generator method
        """
        exec_response = {
            'success': False
        }
        try:
            base_url = 'https://www.latimes.com/'

            self.browser.open_browser(
                url=base_url+'search',
                service_log_path=os.path.devnull
            )

            logging.info("Accessing the default search page.")
            html_topics = self.browser.find_elements(
                "xpath://label[@class='checkbox-input-label']/input")

            topic_id = self.get_topic_id(
                html_topics=html_topics,
                topic=payload['topic']
            )
            if not topic_id:
                logging.error("Failed to obtain the topic's id.")
                return exec_response

            self.browser.close_browser()

            endpoint = self.endpoint_generate(
                query=payload['query'],
                topic_id=topic_id,
            )

            logging.info("Accessing the search result page.")
            self.browser.open_browser(
                url=base_url+endpoint,
                service_log_path=os.path.devnull
            )

            last_acceptable_date = self.data_handling.get_last_acceptable_date(
                months_delta=payload['months_delta']
            )

            extracted_data = self.extract_from_html(
                last_acceptable_date=last_acceptable_date,
                query=payload['query']
            )
            self.browser.close_browser()

            sheet_name = f"{quote(payload['query'])}_{payload['topic']}_"
            sheet_name += f"delta_{payload['months_delta']}.xlsx"
            sheet_path = self.data_handling.build_sheet(
                extracted_data=extracted_data,
                sheet_name=sheet_name
            )
            if sheet_path:
                logging.info(
                    "Successfully created the sheet file %s", sheet_name)
                exec_response.update({
                    'success': True
                })

        finally:
            return exec_response

    def extract_from_html(
        self,
        last_acceptable_date: datetime,
        query: str
    ) -> list:
        """
        Scrapes through the endpoint to gather data
        """
        try:
            index = 0
            extracted_data = []
            news = self.browser.find_elements("class:promo-wrapper")
            while index < len(news):
                news_object = {
                    'picture_filename': '',
                    'title': '',
                    'description': '',
                    'date': '',
                    'search_phrase_count': 0,
                    'contains_money': False
                }
                news_date = self.data_handling.date_filter(
                    date=self.browser.find_elements(
                        "xpath://p[@class='promo-timestamp']")[index].text
                )
                if news_date < last_acceptable_date:
                    logging.info(
                        "All news from given period have been extracted")
                    break

                logging.info("Extracting info from the new's HTML.")

                news_object['title'] = self.browser.find_elements(
                    "xpath://h3[@class='promo-title']")[index].text
                news_object['description'] = self.browser.find_elements(
                    "xpath://p[@class='promo-description']")[index].text

                news_object = self.string_comparisons(
                    news_object=news_object,
                    query=query
                )
                news_object['date'] = news_date.strftime("%m/%d/%Y")

                download_response = self.data_handling.download_file(
                    url=self.browser.find_elements(
                        "xpath://div[@class='promo-media']//img")[
                            index].get_attribute('src'),
                    date=news_date.strftime("%Y_%m_%d"),
                    query=query
                )
                if not download_response.get('success'):
                    logging.error(
                        "The robot failed to download the new's image.")
                else:
                    news_object['picture_filename'] = download_response.get(
                        'picture_filename')
                    self.file_count += 1
                    self.files_size += download_response['file_size']

                extracted_data.append(news_object)
                if self.file_count >= 50 or self.files_size >= self.SIZE_LIMIT:
                    logging.warning("The robot has reached its file limit.")
                    break
                index += 1

        finally:
            return extracted_data

    def endpoint_generate(
        self,
        query: str,
        topic_id: str
    ) -> str:
        """
        Generates the search url's endpoint
        """
        logging.info("Generating the search endpoint.")
        sort_by_newest_param = 1
        endpoint = f"search?q={quote_plus(query)}"
        endpoint += f"&f0={topic_id}"
        endpoint += f"&s={sort_by_newest_param}"
        return endpoint

    def get_topic_id(
        self,
        html_topics: list,
        topic: str
    ) -> str:
        """
        Gathers the topic's id from the HTML
        """
        logging.info("Gathering the topic's id value.")
        topic_id = ''
        for html_topic in html_topics:
            if topic == html_topic.accessible_name:
                topic_id = html_topic.get_attribute('value')
                break
        return topic_id

    def string_comparisons(
        self,
        news_object: dict,
        query: str
    ) -> dict:
        """
        Scrapes the new's title and description to find mentions
        to the search query and money.
        """
        message = "Scraping the new's title and description to find"
        message += "mentions to the search query and money."
        logging.info(message)
        mixed_strings = f"{news_object.get('title')} "
        mixed_strings += f"{news_object.get('description')}"
        news_object['search_phrase_count'] = len(
            re.findall(query, mixed_strings))

        regex_pattern = r'(\$?([\d]{1,3}\,)?[\d]{1,3}\.[\d]{1,2}'
        regex_pattern += r'|[\d]+ (dollars|USD))'
        if re.search(regex_pattern, mixed_strings):
            news_object['contains_money'] = True

        return news_object
