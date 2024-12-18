import json
import csv
from abc import ABC, abstractmethod
from lr5 import *

class CurrenciesList:
    def __init__(self, currency_rates):
        self.currency_rates = currency_rates

    def get_currencies(self):
        """Получить данные о валютах в виде словаря"""
        return self.currency_rates.get_all_currencies()

class Decorator(ABC):
    """Абстрактный базовый декоратор"""
    def __init__(self, component):
        self._component = component

    @abstractmethod
    def get_currencies(self):
        pass

class ConcreteDecoratorJSON(Decorator):
    """Декоратор, преобразующий данные в формат JSON"""
    def get_currencies(self):
        data = self._component.get_currencies()
        try:
            return json.dumps(data, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка преобразования в JSON: {e}")
            return None

class ConcreteDecoratorCSV(Decorator):
    """Декоратор, преобразующий данные в формат CSV"""
    def get_currencies(self):
        data = self._component.get_currencies()

        try:
            csv_output = []
            for currency in data:
                for code, (name, rate) in currency.items():
                    csv_output.append([code, name, rate])

            output = ""
            writer = csv.writer(output := [])
            writer.writerow(["Code", "Name", "Rate"])
            writer.writerows(csv_output)

            return "\n".join(output)
        except Exception as e:
            print(f"Ошибка преобразования в CSV: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    # Создаем объект для работы с курсами валют
    rates = CurrencyRates()

    # Базовый класс для получения словаря
    base_component = CurrenciesList(rates)

    # Получение данных в базовом формате (словарь)
    print("--- Базовые данные ---")
    print(base_component.get_currencies())

    # Декорируем базовый класс для преобразования в JSON
    json_decorator = ConcreteDecoratorJSON(base_component)
    print("\n--- Данные в формате JSON ---")
    print(json_decorator.get_currencies())

    # Декорируем JSON-декоратор для преобразования в CSV
    csv_decorator = ConcreteDecoratorCSV(json_decorator)
    print("\n--- Данные в формате CSV ---")
    print(csv_decorator.get_currencies())

    # Также можно декорировать базовый класс напрямую для CSV
    csv_decorator_direct = ConcreteDecoratorCSV(base_component)
    print("\n--- Данные в формате CSV (без JSON-декоратора) ---")
    print(csv_decorator_direct.get_currencies())