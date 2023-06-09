import datetime
import decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from .forms import ExchangeForm
from .models import Rate
from django.shortcuts import render


class DecimalAsFloatJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


def index(request):
    current_date = datetime.date.today()
    current_rates = Rate.objects.filter(date=current_date).all().values()
    return JsonResponse(
        {"current_rates": list(current_rates)}, encoder=DecimalAsFloatJSONEncoder
    )


def exchange_view(request):
    if request.method == "POST":
        form = ExchangeForm(request.POST)
        if form.is_valid():
            sell_currency = form.cleaned_data["sell_currency"]
            buy_currency = form.cleaned_data["buy_currency"]
            sell_amount = form.cleaned_data["sell_amount"]

            if sell_currency != "UAH":
                rates = Rate.objects.filter(
                    currency_a=sell_currency, currency_b=buy_currency
                )
                if rates.exists():
                    rate = rates.order_by("-date").order_by("-sell")
                    latest_rate = rate.first()
                    exchange_rate = latest_rate.sell
                    converted_amount = round(sell_amount * exchange_rate, 2)
                else:
                    converted_amount = None
            elif sell_currency == "UAH":
                rates = Rate.objects.filter(
                    currency_b=sell_currency, currency_a=buy_currency
                )
                if rates.exists():
                    rate = rates.order_by("-date").order_by("-buy")
                    latest_rate = rate.first()
                    exchange_rate = latest_rate.buy
                    converted_amount = round(sell_amount / exchange_rate, 2)
                else:
                    converted_amount = None

            context = {
                "form": form,
                "sell_currency": sell_currency,
                "buy_currency": buy_currency,
                "sell_amount": sell_amount,
                "converted_amount": converted_amount,
            }
            return render(request, "result.html", context)
    else:
        form = ExchangeForm()

    context = {
        "form": form,
    }
    return render(request, "exchange.html", context)
