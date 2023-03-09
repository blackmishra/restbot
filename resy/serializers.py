from rest_framework import serializers
from .models import Resy

class ResySerializer(serializers.ModelSerializer):
    class Meta:
        model = Resy
        fields = ["task", "completed", "timestamp", "updated", "user"]