import abc
import dataclasses
import enum

import requests

from bs4 import BeautifulSoup

spread = 0.5

class ExchangeCodes(enum.Enum):
    USD = 840
    EUR = 978
    UAH = 980


@dataclasses.dataclass(frozen=True)
class SellBuy:
    sell: float
    buy: float


class ExchangeBase(abc.ABC):
    """
    Base class for exchange providers, should define get_rate() method
    """

    def __init__(self, vendor, currency_a, currency_b):
        self.vendor = vendor
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.pair: SellBuy = None

    @abc.abstractmethod
    def get_rate(self):
        raise NotImplementedError("Method get_rate() is not implemented")


class MonoExchange(ExchangeBase):
    def get_rate(self):
        a_code = ExchangeCodes[self.currency_a].value
        b_code = ExchangeCodes[self.currency_b].value
        r = requests.get("https://api.monobank.ua/bank/currency")
        r.raise_for_status()
        for rate in r.json():
            currency_code_a = rate["currencyCodeA"]
            currency_code_b = rate["currencyCodeB"]
            if currency_code_a == a_code and currency_code_b == b_code:
                self.pair = SellBuy(rate["rateSell"], rate["rateBuy"])

                return


class PrivatExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        r.raise_for_status()
        for rate in r.json():
            if rate["ccy"] == self.currency_a and rate["base_ccy"] == self.currency_b:
                self.pair = SellBuy(float(rate["sale"]), float(rate["buy"]))


class NBUExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
        r.raise_for_status()
        for rate in r.json():
            if rate["r030"] == ExchangeCodes[self.currency_a].value:
                self.pair = SellBuy(float(rate["rate"]), float(rate["rate"]) - spread)


class OschadbankExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://www.oschadbank.ua/currency-rate")
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_="heading-block-currency-rate__table")
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row.find_all('td')])
        if self.currency_a == "USD":
            self.pair = SellBuy(float(rows[1][4]), float(rows[1][3]))
        if self.currency_a == "EUR":
            self.pair = SellBuy(float(rows[2][4]), float(rows[2][3]))


class KredoBankExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://kredobank.com.ua/info/kursy-valyut/commercial")
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table')
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row.find_all('td')])
        if self.currency_a == "USD":
            self.pair = SellBuy(float(rows[1][2]), float(rows[1][3]))
        if self.currency_a == "EUR":
            self.pair = SellBuy(float(rows[2][2]), float(rows[2][3]))
