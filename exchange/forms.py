from django import forms

CURRENCY_CHOICES = [
    ("UAH", "UAH"),
    ("USD", "USD"),
    ("EUR", "EUR"),
]


class ExchangeForm(forms.Form):
    sell_currency = forms.ChoiceField(label="Sell Currency", choices=CURRENCY_CHOICES)
    buy_currency = forms.ChoiceField(label="Buy Currency", choices=CURRENCY_CHOICES)
    sell_amount = forms.DecimalField(label="Sell Amount", min_value=0)
