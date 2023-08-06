import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def complex_field_calculator(instruction, dialect):

    if instruction is not "" and dialect is not "":

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "instruction": instruction,
            "dialect": dialect
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = "https://api-dev.askdata.com/cfc/complexfieldcalculator"

        r = s.post(url=url, headers=headers, json=data)
        r.raise_for_status()

        try:
            response = r.json()['calculated_field']
            return response
        except Exception as e:
            logging.error(str(e))
            print(e)
            return None
    else:
        print("An input is empty!")
        return None


def complex_filter_calculator(instruction, dialect):

    if instruction is not "" and dialect is not "":

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "instruction": instruction,
            "dialect": dialect
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = "https://api-dev.askdata.com/cfc/complexfiltercalculator"

        r = s.post(url=url, headers=headers, json=data)
        r.raise_for_status()

        try:
            response = r.json()['calculated_filter']
            return response
        except Exception as e:
            logging.error(str(e))
            print(e)
            return None
    else:
        print("An input is empty!")
        return None


def smartjoin(tables):

    if bool(tables):

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "tables": tables
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = "https://api-dev.askdata.com/cfc/smartjoin"

        r = s.post(url=url, headers=headers, json=data)
        r.raise_for_status()

        try:
            response = r.json()['join_list']
            return response
        except Exception as e:
            logging.error(str(e))
            print(e)
            return None
    else:
        print("The input is empty!")
        return None
