from django.urls import path, include
from .views import (
    RestTemplateView,
    SearchTemplateView,
    Request_booking,
    Populate_Restaurants,
    Get_Booking_Token,
    Make_Booking,
    Add_Restaurant,
    User_auth_token,
    Cancel_Booking,
    Fetch_user,
    BookingListView,
    TestAPI,
    # Session_save,
)

urlpatterns = [
    path('search', SearchTemplateView.as_view()),
    path('find', RestTemplateView.as_view()),
    path('', Request_booking.as_view(), name = "booking_page"),
    path('fetch_and_add_rest', Populate_Restaurants.as_view()),
    path('get_booking_token', Get_Booking_Token.as_view()),
    path('make_booking', Make_Booking.as_view()),
    path('add_rest', Add_Restaurant.as_view(), name='add_rest'),
    path('refresh_auth_token', User_auth_token.as_view(), name='refresh_auth_token'),
    path('cancel_booking', Cancel_Booking.as_view(), name = "cancel_booking"),
    path('fetch_user', Fetch_user.as_view(), name = "fetch_user"),
    path('view_bookings', BookingListView.as_view(), name = "view_bookings"),
    path('test_api', TestAPI.as_view(), name = "test_api"),


    # path('save_in_session', Session_save.as_view(), name = "save_in_session"),



]
