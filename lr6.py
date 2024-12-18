import json
import requests
import time
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET
from datetime import datetime
from lr5 import *


class BaseCurrenciesList():
    def get_currencies(self, wanted_currencies: list) -> dict:
        pass


class CurrenciesList(BaseCurrenciesList):
    def __init__(self):
        self.rates_available = False
        self.times = time.time()
        self.date_now = datetime.now().day
        self.rates = None
        self.url = "http://www.cbr.ru/scripts/XML_daily.asp"

    def get_currencies(self, wanted_currencies: list) -> dict:
        times = time.time()
        date_now = datetime.today().day

        result = {}
        if self.rates_available:
            return self.rates

        if not self.rates_available or (times - self.times > 3600 or date_now != self.date_now):
            if wanted_currencies is None:
                wanted_currencies = ['R01239', 'R01235', 'R01035', 'R01815', 'R01585F']

            res = requests.get(self.url)
            cur_res_str = res.text

            # Парсинг XML
            root = ET.fromstring(cur_res_str)
            valutes = root.findall("Valute")

            for val in valutes:
                valute_id = val.get('ID')
                if valute_id in wanted_currencies:
                    valute_name = val.find('Name').text
                    valute_value = val.find('Value').text

                    result[valute_id] = (valute_value, valute_name)
            self.rates = result
            self.available = True
        return result


class Decorator(BaseCurrenciesList):
    __wrapped_object: BaseCurrenciesList = None

    def __init__(self, wanted_currencies: BaseCurrenciesList):
        self.__wrapped_object = wanted_currencies

    @property
    def wrapped_object(self) -> str:
        return self.__wrapped_object

    def get_currencies(self, wanted_currencies: list = None) -> dict:
        return self.__wrapped_object.get_currencies(wanted_currencies)


class ConcreteDecoratorJSON(Decorator):
    def get_currencies(self, wanted_currencies: list = None) -> str:
        return json.dumps(self.wrapped_object.get_currencies(wanted_currencies), ensure_ascii=False, indent=4)


class ConcreteDecoratorCSV(Decorator):
    def get_currencies(self, wanted_currencies: list = None) -> str:
        currency_data = self.wrapped_object.get_currencies(wanted_currencies)

        if type(currency_data) is str:
            currency_data = json.loads(currency_data)

        csv_data = "ID;Rate;Name\n"
        for currency, val in currency_data.items():
            csv_data += f'{currency};{val[0]};{val[1]}\n'
        csv_data = csv_data.rstrip()
        return csv_data

def show_currencies(currencies: BaseCurrenciesList):
    print(currencies.get_currencies())




curlistdict = CurrenciesList
wrappedcurlist = Decorator(curlistdict)
wrappedcurlist_json = ConcreteDecoratorJSON(curlistdict)
wrappedcurlist_csv = ConcreteDecoratorCSV(curlistdict)

show_currencies(wrappedcurlist_json)
show_currencies(wrappedcurlist_csv)
show_currencies(wrappedcurlist)
