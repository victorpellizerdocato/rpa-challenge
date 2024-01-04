import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, quote
from src.challenge.utils.data_handling import DataHandling


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


class LATimes():
    def __init__(
        self,
        data_handling: DataHandling
    ):
        self.data_handling = data_handling

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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        if not request_response or request_response.status_code != 200:
            print("Error accessing LATimes.")
            return exec_response

        topic_id = self.get_topic_id(
            request_response=request_response,
            topic=package['topic']
        )
        if not topic_id:
            print("Failed to obtain the topic's id.")
            return exec_response

        endpoint = self.endpoint_generate(
            query=package['query'],
            topic_id=topic_id,
        )

        print("Accessing the result page")
        request_response = requests.get(
            url=url+endpoint,
            headers={
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        if not request_response or request_response.status_code != 200:
            print("Error accessing the result page.")
            return exec_response

        last_acceptable_date = self.data_handling.get_last_acceptable_date(
            months_delta=package['months_delta']
        )

        site_html = BeautifulSoup(request_response.text, 'html.parser')
        news = site_html.select('.promo-wrapper')
        extracted_data = []
        for new in news:
            news_date = self.data_handling.date_filter(date=new.contents[0].next_sibling.contents[2].next)
            if news_date < last_acceptable_date:
                print("All news from given period have been extracted.")
                break
            news_info = self.extract_from_html(
                new=new,
                date=news_date,
                query=package['query']
            )
            extracted_data.append(news_info)

        sheet_path = self.data_handling.build_sheet(
            extracted_data=extracted_data,
            sheet_name=f"{package['topic']}_{quote(package['query'])}_{package['months_delta']}_delta"
        )
        if sheet_path:
            print(f"Successfully created the datasheet {sheet_path}.")
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
        print("Generating the search endpoint.")
        sort_by_newest_param = 1
        endpoint = f"?q={quote_plus(query)}&f0={topic_id}&s={sort_by_newest_param}"
        return endpoint

    def get_topic_id(
        self,
        request_response,
        topic: str
    ) -> str:
        print("Obtaining the topic's id value.")
        site_html = BeautifulSoup(request_response.text, 'html.parser')
        html_topics = site_html.select('.checkbox-input-label')
        topic_id = ''
        for html_topic in html_topics:
            if topic in html_topic.text:
                topic_id = html_topic.contents[0].attrs['value']
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
        print("Extracting info from the new's HTML.")

        news_object['image_path'] = self.data_handling.download_file(
            url=new.contents[0].contents[0].contents[0].contents[3].attrs['src']
        )
        if not news_object['image_path']:
            print("The robot failed to download the new's image.")

        news_object['title'] = new.contents[0].next_sibling.contents[0].contents[3].text.strip()
        news_object['description'] = new.contents[1].contents[1].text

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
        print("Scraping the new's title and description to find mentions to the search query and money.")
        split_strings = f"{news_object.get('title')} {news_object.get('description')}".split(' ')

        split_query = query.split(' ')

        money_signs = [
            '$',
            'dollars',
            ' USD'
        ]

        index = 0
        while index < len(split_strings):
            for j in money_signs: # search the big text for money signs
                if split_strings[index] == j:
                    news_object['contains_money'] = True
                    break
            if split_strings[index] == split_query[0]:
                query_index = 1
                while query_index < len(split_query): # iterates through every split part of the search term in the big text
                    if split_strings[index+query_index] != split_query[query_index]:
                        break
                    query_index += 1
                if query_index ==  len(split_query): # if the whole search term is found, the counter is increased
                    news_object['search_phrase_count'] += 1
            index += 1

        return news_object
