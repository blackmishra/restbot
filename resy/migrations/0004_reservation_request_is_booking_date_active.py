# Generated by Django 4.1.7 on 2023-03-23 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("resy", "0003_remove_reservation_request_end_time_slot_and_more")]

    operations = [
        migrations.AddField(
            model_name="reservation_request",
            name="is_booking_date_active",
            field=models.BooleanField(default=False),
        )
    ]