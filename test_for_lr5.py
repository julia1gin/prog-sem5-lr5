import pytest
from unittest.mock import patch, MagicMock
import time
from lr5 import CurrencyRates

@patch('lr5.requests.get')
def test_get_particular_currency_valid_id(mock_get):
    """Тест получения курса валюты с корректным ID"""
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

    rates = CurrencyRates()
    result = rates.get_particular_currency(["R01235"])
    expected = [{"USD": ("Доллар США", "74,23")}]  # Ожидаемый результат
    assert result == expected


@patch('lr5.requests.get')
def test_get_particular_currency_invalid_id(mock_get):
    """Тест получения курса валюты с некорректным ID"""
    xml_response = '''<ValCurs Date="13.01.2025" name="Foreign Currency Market"></ValCurs>'''
    mock_get.return_value = MagicMock(status_code=200, content=xml_response)

    rates = CurrencyRates()
    result = rates.get_particular_currency(["R9999"])
    expected = [{"R9999": None}]  # Ожидаемый результат
    assert result == expected


def test_request_interval():
    """Тест проверки интервала между запросами"""
    rates = CurrencyRates(request_interval=2)  # Интервал 2 секунды

    with patch('lr5.requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content="<ValCurs></ValCurs>")

        rates.get_particular_currency(["R01235"])
        result_first_call = rates.get_particular_currency(["R01235"])

        # Второй вызов должен вернуть [{'R9999': None}] из-за интервала
        assert result_first_call == [{"R9999": None}]

        time.sleep(2)
        result_second_call = rates.get_particular_currency(["R01235"])

        # После паузы запрос должен пройти успешно
        assert result_second_call != [{"R9999": None}]
