import html
import logging
import requests
from datetime import datetime
from selectolax.parser import HTMLParser
from urllib.parse import quote_plus, quote
from src.challenge.utils.data_handling import DataHandling


class LATimes():
    def __init__(
        self,
        data_handling: DataHandling
    ):
        self.data_handling = data_handling
        self.file_count = 0
        self.files_size = 0

    def exec(
        self,
        package: dict
    ) -> dict:
        exec_response = {
            'success': False
        }

        url = 'https://www.latimes.com/search'
        request_response = requests.get(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW\
                ebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        if not request_response or request_response.status_code != 200:
            logging.error("Error accessing LATimes.")
            return exec_response

        topic_id = self.get_topic_id(
            request_response=request_response,
            topic=package['topic']
        )
        if not topic_id:
            logging.error("Failed to obtain the topic's id.")
            return exec_response

        endpoint = self.endpoint_generate(
            query=package['query'],
            topic_id=topic_id,
        )

        logging.info("Accessing the result page")
        request_response = requests.get(
            url=url+endpoint,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW\
                ebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        if not request_response or request_response.status_code != 200:
            logging.error("Error accessing the result page.")
            return exec_response

        last_acceptable_date = self.data_handling.get_last_acceptable_date(
            months_delta=package['months_delta']
        )

        site_html = HTMLParser(request_response.text)

        news = site_html.css(".promo-wrapper")
        extracted_data = []
        SIZE_LIMIT = 20000000
        for new in news:
            news_date = self.data_handling.date_filter(
                date=new.last_child.last_child.last_child.text_content)

            if news_date < last_acceptable_date:
                logging.info("All news from given period have been extracted")
                break
            news_info = self.extract_from_html(
                new=new,
                date=news_date,
                query=package['query']
            )
            extracted_data.append(news_info)
            if self.file_count >= 50 or self.files_size >= SIZE_LIMIT:
                logging.warning("The robot has reached its file limit.")
                break

        sheet_name = f"{quote(package['query'])}_{package['topic']}_"
        sheet_name += f"delta_{package['months_delta']}"
        sheet_path = self.data_handling.build_sheet(
            extracted_data=extracted_data,
            sheet_name=sheet_name
        )
        if sheet_path:
            logging.info(f"Successfully created the sheet file {sheet_name}.")
            exec_response.update({
                'sheet_path': sheet_path,
                'success': True
            })

        return exec_response

    def endpoint_generate(
        self,
        query: str,
        topic_id: str
    ) -> str:
        logging.info("Generating the search endpoint.")
        sort_by_newest_param = 1
        endpoint = f"?q={quote_plus(query)}"
        endpoint += f"&f0={topic_id}"
        endpoint += f"&s={sort_by_newest_param}"
        return endpoint

    def get_topic_id(
        self,
        request_response,
        topic: str
    ) -> str:
        logging.info("Obtaining the topic's id value.")
        site_html = HTMLParser(request_response.text)

        html_topics = site_html.css(".checkbox-input-label")
        topic_id = ''
        for html_topic in html_topics:
            if topic in html.unescape(html_topic.html):
                topic_id = html_topic.child.attributes['value']
                break
        return topic_id

    def extract_from_html(
        self,
        new,
        date: datetime,
        query: str
    ) -> dict:
        news_object = {
            'picture_filename': '',
            'title': '',
            'description': '',
            'date': '',
            'search_phrase_count': 0,
            'contains_money': False
        }
        logging.info("Extracting info from the new's HTML.")

        if new.child.child.child.last_child:  # checks if a new has an image
            download_response = self.data_handling.download_file(
                url=new.child.child.child.last_child.prev.attributes['src'],
                date=date.strftime("%Y_%m_%d"),
                query=query
            )
            if not download_response.get('success'):
                logging.error("The robot failed to download the new's image.")
            else:
                news_object['picture_filename'] = download_response.get(
                    'picture_filename')
                self.file_count += 1
                self.files_size += download_response['file_size']

        news_object['title'] = new.last_child.child.last_child.prev.child.\
            next.last_child.text_content
        news_object['description'] = new.last_child.last_child.prev.child.\
            text_content

        news_object = self.string_comparisons(
            news_object=news_object,
            query=query
        )

        news_object['date'] = date.strftime("%m/%d/%Y")

        return news_object

    def string_comparisons(
        self,
        news_object: dict,
        query: str
    ) -> dict:
        logging.info("Scraping the new's title and description to find \
            mentions to the search query and money.")
        split_strings = f"{news_object.get('title')} \
            {news_object.get('description')}".split(' ')

        split_query = query.split(' ')

        money_signs = [
            '$',
            'dollars',
            ' USD'
        ]

        index = 0
        while index < len(split_strings):
            for j in money_signs:  # search the big text for money signs
                if split_strings[index] == j:
                    news_object['contains_money'] = True
                    break
            if split_strings[index] == split_query[0]:
                query_index = 1
                # iterates through every split part of the search term
                # in the big text
                while query_index < len(split_query):
                    if split_strings[index+query_index] != \
                            split_query[query_index]:
                        break
                    query_index += 1
                # if the whole search term is found, the counter is increased
                if query_index == len(split_query):
                    news_object['search_phrase_count'] += 1
            index += 1

        return news_object
