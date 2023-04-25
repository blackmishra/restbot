from django.urls import path, include
from .views import (
    RestTemplateView,
    SearchTemplateView,
    Request_booking,
    Populate_Restaurants,
    Get_Booking_Token,
    Make_Booking,
    Add_Restaurant
)

urlpatterns = [
    path('', SearchTemplateView.as_view()),
    path('search/<int:rest_id>', RestTemplateView.as_view()),
    path('booking_req', Request_booking.as_view()),
    path('fetch_and_add_rest', Populate_Restaurants.as_view()),
    path('get_booking_token', Get_Booking_Token.as_view()),
    path('make_booking', Make_Booking.as_view()),
    path('add_rest', Add_Restaurant.as_view()),



]
