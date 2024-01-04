import requests
import traceback
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, quote
from src.challenge.utils.data_handling import DataHandling


class LATimes():
    def __init__(
        self,
        data_handling: DataHandling
    ):
        self.data_handling = data_handling

    def exec(
        self,
        package
    ):
        execution_response = {
            'success': False
        }
        try:
            print("Accessing LA Times")
            url = 'https://www.latimes.com/search'
            news_info = []

            request_response = requests.get(
                url=url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            if not request_response or request_response.status_code != 200:
                raise Exception("Error accessing the website")

            topic_id = self.get_topic_id(
                request_response=request_response,
                topic=package['topic']
            )

            endpoint = self.endpoint_generate(
                query=package['query'],
                topic_id=topic_id,
            )
            print("Accessing the search page")
            request_response = requests.get(
                url=url+endpoint,
                headers={
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            if not request_response or request_response.status_code != 200:
                raise Exception("Error accessing the website")

            last_acceptable_date = self.data_handling.get_last_acceptable_date(
                months_delta=package['months_delta']
            )

            site_html = BeautifulSoup(request_response.text, 'html.parser')
            news = site_html.select('.promo-wrapper')
            for new in news:
                news_date = self.data_handling.date_filter(date=new.contents[0].next_sibling.contents[2].next)
                if news_date < last_acceptable_date:
                    print("All news from given period have been extracted.")
                    break
                extracted_data = self.extract_from_html(
                    new=new,
                    date=news_date,
                    query=package['query']
                )
                news_info.append(extracted_data)

            file_name = f"{package['topic']}_{quote(package['query'])}_{package['months_delta']}_delta.xlsx"
            file_path = f'./cache/{file_name}'
            self.data_handling.build_sheet(
                extracted_data=news_info,
                file_path=file_path
            )

            execution_response.update({
                'sheet_path': file_path,
                'success': True
            })

        except:
            traceback.print_exc()
            print(f"The bot was interrupted.")

        finally:
            return execution_response

    def endpoint_generate(
        self,
        query,
        topic_id
    ):
        print("Generating the search endpoint.")
        sort_by_newest_param = 1
        endpoint = f"?q={quote_plus(query)}&f0={topic_id}&s={sort_by_newest_param}"
        return endpoint

    def get_topic_id(
        self,
        request_response,
        topic
    ):
        print("Obtaining the topic's id value.")
        site_html = BeautifulSoup(request_response.text, 'html.parser')
        html_topics = site_html.select('.checkbox-input-label')
        for html_topic in html_topics:
            if topic in html_topic.text:
                topic_id = html_topic.contents[0].attrs['value']
                break
        return topic_id

    def extract_from_html(
        self,
        new,
        date,
        query
    ):
        print("Extracting news info from the HTML.")
        image_path = self.data_handling.download_file(
            url=new.contents[0].contents[0].contents[0].contents[3].attrs['src']
        )
        title = new.contents[0].next_sibling.contents[0].contents[3].text.strip()
        description = new.contents[1].contents[1].text

        search_phrase_count, contains_money = self.string_comparisons(
            title=title,
            description=description,
            query=query
        )

        formatted_date = date.strftime("%m/%d/%Y")

        return {
            'picture_filename': image_path,
            'title': title,
            'description': description,
            'date': formatted_date,
            'search_phrase_count': search_phrase_count,
            'contains_money': contains_money
        }

    def string_comparisons(
        self,
        title,
        description,
        query
    ):
        split_strings = f'{title} {description}'.split(' ')

        split_query = query.split(' ')
        search_phrase_count = 0

        money_signs = [
            '$',
            'dollars',
            ' USD'
        ]
        contains_money = False

        index = 0
        while index < len(split_strings):
            for j in money_signs: # search the big text for money signs
                if split_strings[index] == j:
                    contains_money = True
                    break
            if split_strings[index] == split_query[0]:
                query_index = 1
                while query_index < len(split_query): # iterates through every split part of the search term in the big text
                    if split_strings[index+query_index] != split_query[query_index]:
                        break
                    query_index += 1
                if query_index ==  len(split_query): # if the whole search term is found, the counter is increased
                    search_phrase_count += 1
            index += 1

        return search_phrase_count, contains_money