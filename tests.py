import json
import unittest
from unittest.mock import patch, MagicMock
from lr6 import CurrencyRates, ConcreteDecoratorCSV, ConcreteDecoratorJSON


def test_singleton(self):
    """Тест является ли класс CurrencyRates синглтоном."""
    another_instance = CurrencyRates()
    self.assertIs(self.currency_rates, another_instance, "CurrencyRates должен быть синглтоном.")

@patch('lr6.requests.get')
def test_get_rates_success(mock_get):
    '''Тест на корректный вывод конкретных валют (Юань)'''
    xml_response = """<ValCurs Date="14.01.2023" name="Foreign Currency Market">
        <Valute ID="R01375">
            <CharCode>CNY</CharCode>
            <Name>Юань</Name>
            <Value>13,8184</Value>
        </Valute>
    </ValCurs>"""
    mock_get.return_value = MagicMock(status_code=200, content=xml_response)

    currency_rates = CurrencyRates()
    rates = currency_rates.get_particular_currency(["R01375"])

    expected_rates = [{'CNY': ('Юань', '13,8184')}]
    assert rates == expected_rates


@patch('lr6.requests.get')
def test_get_rates_json(mock_get):
    """Тест получения курсов валют в формате JSON."""
    xml_response = '''
        <ValCurs Date="13.01.2025" name="Foreign Currency Market">
            <Valute ID="R01235">
                <CharCode>USD</CharCode>
                <Name>Доллар США</Name>
                <Value>74,23</Value>
            </Valute>
        </ValCurs>
        '''
    mock_get.return_value = MagicMock(status_code=200, content=xml_response)

    currencies_list = CurrencyRates()
    json_decorator = ConcreteDecoratorJSON(currencies_list)
    json_rates = json_decorator.get_currencies(["R01235"])

    expected_json = json.dumps([{"USD": ("Доллар США", "74,23")}], ensure_ascii=False, indent=1)
    assert json_rates == expected_json


class TestConcreteDecoratorCSV(unittest.TestCase):

    @patch('lr6.requests.get')
    def test_get_rates_csv(self, mock_get):
        """Тест получения курсов валют в формате CSV."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
            <ValCurs Date="14.01.2025" name="Foreign Currency Market">
                <Valute ID="R01235">
                    <CharCode>USD</CharCode>
                    <Name>Доллар США</Name>
                    <Value>73,50</Value>
                </Valute>
            </ValCurs>
            """
        mock_get.return_value = mock_response

        currencies_list = CurrencyRates()
        csv_decorator = ConcreteDecoratorCSV(currencies_list)
        csv_rates = csv_decorator.get_currencies(["R01235"])

        expected_csv = "'CharCode', 'Name', 'Value'\r\nUSD, Доллар США, 73,50\r\n"
        assert csv_rates == expected_csv
