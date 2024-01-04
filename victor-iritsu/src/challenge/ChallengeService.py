import requests
import traceback
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from src.challenge.utils.data_handling import DataHandling
from challenge.systems.latimes.LATimesService import LATimes


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


class ChallengeService():
    def __init__(
        self,
        data_handling: DataHandling
    ):
        self.data_handling=data_handling
        self.la_times=LATimes(
            data_handling=self.data_handling
        )

    def exec_robots(
        self,
        package
    ):
        systems = [
            self.la_times
        ]
        for system in systems:
            system.exec(package)