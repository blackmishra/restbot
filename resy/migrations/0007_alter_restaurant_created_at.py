# Generated by Django 4.1.7 on 2023-03-23 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("resy", "0006_rename_updated_restaurant_updated_at")]

    operations = [
        migrations.AlterField(
            model_name="restaurant",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        )
    ]