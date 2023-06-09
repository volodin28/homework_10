import json
import pathlib

import pytest
import responses
from django.core.management import call_command

from .exchange_provider import MonoExchange, PrivatExchange, NBUExchange

root = pathlib.Path(__file__).parent


@pytest.fixture
def mocked():
    def inner(file_name):
        return json.load(open(root / "fixtures" / file_name))
    return inner


@responses.activate
def test_exchange_mono(mocked):
    mocked_response = mocked("mono_response.json")
    responses.get(
        "https://api.monobank.ua/bank/currency",
        json=mocked_response,
    )
    e = MonoExchange("mono", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.4406


@responses.activate
def test_privat_rate(mocked):
    mocked_response = mocked("privat_response.json")
    responses.get(
        "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11",
        json=mocked_response,
    )
    e = PrivatExchange("privat", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.45318


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@responses.activate
def test_nbu_rate(mocked):
    mocked_response = mocked("NBU_response.json")
    responses.get(
        "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json",
        json=mocked_response,
    )
    e = NBUExchange("nbu", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 36.5686
