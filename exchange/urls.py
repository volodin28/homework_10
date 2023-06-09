from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calculator/", views.exchange_view, name="exchange_view"),
]
