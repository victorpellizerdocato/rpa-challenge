# rpa-challenge
> Code to demonstrate my knowledge in Python RPA development.

This robot accesses a given general news website, apply some filters and then gather information from news.

## PARAMS
It receives a dict with 3 indexes:

query - the query you want the robot to search for

topic - the news topic

months_delta - number of months for which you need to receive news

## Features on v1.0
1. Opens https://www.latimes.com/
2. Inserts query, topic and order news by Newest
3. Downloads the new's image and saves its path
4. Saves in an Excel file:
    - title
    - date
    - description
    - image's path
    - count of search query in the title and description
    - True or False, depending on whether the title or description contains any amount of money
        > Formatos possíveis: $11.1 | $111,111.11 | 11 dollars | 11 USD
5. Repeats steps 3 and 4 for all news that falls within the required time period
