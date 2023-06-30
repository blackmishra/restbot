from django.contrib import admin
from .models import Resy, Reservation_request, Restaurant, User


# Register your models here.
admin.site.register(Reservation_request)
admin.site.register(Restaurant)
admin.site.register(User)
