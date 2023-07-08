from django.contrib import admin
from .models import Booking_details, Resy, Reservation_request, Restaurant, User


# Register your models here.
admin.site.register(Reservation_request)
admin.site.register(Restaurant)
admin.site.register(User)
admin.site.register(Booking_details)

