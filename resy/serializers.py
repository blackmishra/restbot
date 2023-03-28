from datetime import date
from rest_framework import serializers
from .models import Resy, Reservation_request, Restaurant

class ResySerializer(serializers.ModelSerializer):
    class Meta:
        model = Resy
        fields = ["task", "completed", "timestamp", "updated", "user"]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["rest_name", "rest_id"]

    # def create(self, validated_data):  
    #         rest_data = [Restaurant(**item) for item in validated_data]  
    #         return Restaurant.objects.bulk_create(rest_data)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation_request
        fields = '__all__'

    def validate(self, data):
        if data['date'] < date.today():
            raise serializers.ValidationError("Date provided must be current or future.")
        return data

        