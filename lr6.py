import json
import csv
from abc import ABC, abstractmethod
import requests
import time
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET


class SingletonMeta(type):
    """Метакласс для Singleton"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class CurrencyRates(metaclass=SingletonMeta):
    """Класс, методы которого позволяют работать с курсами валют на сайте ЦБ РФ"""
    def __init__(self, url="http://www.cbr.ru/scripts/XML_daily.asp", request_interval=1):
        self.url = url
        self.request_interval = request_interval
        self.last_request_time = 0
        self.all_currencies = []
        self.currencies_data = []

    def _can_request(self):
        """Контроль частоты запросов"""
        current_time = time.time()
        if current_time - self.last_request_time >= self.request_interval:
            self.last_request_time = current_time
            return True
        return False

    def get_particular_currency(self, wanted_currencies: list) -> list:
        """Получение информации о конкретных валютах из списка"""
        if not self._can_request():
            return [{'R9999': None}]

        try:
            cur_res_str = requests.get(self.url)
            cur_res_str.raise_for_status()  # Проверка на ошибки HTTP запроса

            # Парсинг XML
            root = ET.fromstring(cur_res_str.content)
            valutes = root.findall("Valute")

            result = []
            for _v in valutes:
                valute_id = _v.get('ID')
                if valute_id in wanted_currencies:
                    valute_id = _v.get('ID')
                    valute_cur_name = _v.find('Name').text
                    valute_cur_val = _v.find('Value').text
                    valute_charcode = _v.find('CharCode').text
                    result.append({valute_charcode: (valute_cur_name, valute_cur_val)})

            self.all_currencies = result

            return result
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе данных с сайта: {e}")
            return [{'R9999': None}]
        except ET.ParseError as e:
            print(f"Ошибка при парсинге XML: {e}")
            return [{'R9999': None}]
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return [{'R9999': None}]


    def get_all_currencies(self):
        """Получение информации о всех валютах с сайта ЦБ РФ"""
        if not self._can_request():
            return [{'R9999': None}]
        try:
            cur_res_str = requests.get(self.url)
            cur_res_str.raise_for_status()  # Проверка на ошибки HTTP запроса

            # Парсинг XML
            root = ET.fromstring(cur_res_str.content)
            valutes = root.findall("Valute")

            result = []
            for _v in valutes:
                valute_id = _v.get('ID')
                valute_cur_name = _v.find('Name').text
                valute_cur_val = _v.find('Value').text
                valute_charcode = _v.find('CharCode').text
                result.append({valute_charcode: (valute_cur_name, valute_cur_val)})

            self.currencies_data = result

            return result
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе данных с сайта: {e}")
            return [{'R9999': None}]
        except ET.ParseError as e:
            print(f"Ошибка при парсинге XML: {e}")
            return [{'R9999': None}]
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return [{'R9999': None}]

    def print_selected_currencies(self, wanted_currencies):
        """Метод для вывода информации о выбранных валютах"""
        selected_currencies = self.get_particular_currency(wanted_currencies)

        if not selected_currencies or selected_currencies == [{'R9999': None}]:
            print("Не удалось получить данные о валютах.")
            return

        for currency in selected_currencies:
            for code, (name, rate) in currency.items():
                print(f'{code}: {name} - {rate} руб.')

    def visualize_all_currencies(self):
        """Метод для визуализации всех валют"""
        all_currencies = self.get_all_currencies()

        if all_currencies == [{'R9999': None}]:
            print("Не удалось получить данные о валютам для визуализации.")
            return

        names = []
        rates = []

        for currency in all_currencies:
            for code, (name, rate) in currency.items():
                names.append(name)
                rates.append(float(rate.replace(',', '.')))

        plt.figure(figsize=(12, 10))
        bars = plt.bar(names, rates, color=plt.cm.Paired.colors[:len(names)])


        plt.xlabel('Валюты', fontsize=12)
        plt.ylabel('Курс', fontsize=12)
        plt.title('Курсы валют по данным ЦБ РФ', fontsize=14, fontweight='bold')

        # Настройка внешнего вида графика
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Сохранение графика в файл
        try:
            plt.savefig('currencies.jpg', dpi=300)
            print("График успешно сохранен в файл 'currencies.jpg'")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")


class CurrencyDecorator:
    def __init__(self, currencies_list):
        self._currencies_list = currencies_list

    def get_currencies(self, currencies_ids_lst):
        return self._currencies_list.get_particular_currency(currencies_ids_lst)


class ConcreteDecoratorJSON(CurrencyDecorator):
    def get_currencies(self, currencies_ids_lst):
        data = super().get_currencies(currencies_ids_lst)
        return json.dumps(data, ensure_ascii=False, indent=1)


class ConcreteDecoratorCSV(CurrencyDecorator):
    def __init__(self, currencies_list):
        self._currencies_list = currencies_list

    def get_currencies(self, currencies_ids_lst):
        currencies = self._currencies_list.get_particular_currency(currencies_ids_lst)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['CharCode', 'Name', 'Value'])  # Заголовки
        for currency in currencies:
            charcode = list(currency.keys())[0]
            name, value = currency[charcode]
            writer.writerow([charcode, name, value])
        return output.getvalue()


currencies_list = CurrencyRates()
try:
    result = currencies_list.get_particular_currency(['R01770', 'R01335', 'R01090B'])
    print("Базовое представление данных:")
    print(result)

    time.sleep(5)
    # Декоратор для JSON
    json_currencies = ConcreteDecoratorJSON(currencies_list)
    print("\nДанные в формате JSON:")
    print(json_currencies.get_currencies(['R01770', 'R01335', 'R01090B']))

    time.sleep(5)
    # Декоратор для CSV
    csv_currencies = ConcreteDecoratorCSV(currencies_list)
    print("\nДанные в формате CSV:")
    print(csv_currencies.get_currencies(['R01770', 'R01335', 'R01090B']))

except Exception as e:
    print(e)