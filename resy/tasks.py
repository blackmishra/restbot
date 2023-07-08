import ast
import datetime
import json
from datetime import date, datetime


import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from resy.models import Booking_details, Reservation_request, Restaurant, User
from resybookingproject import constants as CONST
from resybookingproject.settings import BASE_URL
from json import dumps
from django.core.serializers.json import DjangoJSONEncoder



logger = get_task_logger(__name__)
today_date = json.dumps(date.today(), cls=DjangoJSONEncoder)

default_headers = {
    "authority": "api.resy.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en;q=0.9",
    "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
    "cache-control": "no-cache",
    "origin": "https://resy.com",
    "referer": "https://resy.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "x-origin": "https://resy.com",
    "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "content-type": "application/json",
}


@shared_task
def update_is_booking_date_flag():
    book_reqs = Reservation_request.objects.all()

    current_date = today_date

    url = CONST.SEARCH_API
    payload = json.dumps(
        {
            "page": 1,
            "per_page": 5000,
            "slot_filter": {"day": current_date, "party_size": 2},
            "types": ["venue"],
            "geo": {"latitude": 40.712941, "longitude": -74.006393, "radius": 35420},
            "query": "",
        }
    )
    headers = default_headers
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    # All values
    values = {}
    for item in data["search"]["hits"]:
        temp = {}
        temp["name"] = (item["name"],)
        temp["id"] = (item["id"]["resy"],)
        temp["availability_dates"] = (item["inventory_any"],)

        values[item["id"]["resy"]] = temp

    # logger.info(list(values.keys()))

    for req in book_reqs:
        # booking_date = getattr(req, 'date')
        rest_id = getattr(req, "rest_id")
        logger.info(rest_id)

        date_str = values[rest_id]["availability_dates"][-1][-1]

        req.booking_available_till = datetime.date(*map(int, date_str.split("-")))
        req.save()

        if req.is_booking_date_available:
            req.is_booking_date_active = True
            req.save()
        else:
            req.is_booking_date_active = False
            req.save()

        # if req.remove_booking_req:
        #     req.delete()


@shared_task
def make_booking_req():
    booking_status = False
    book_reqs = Reservation_request.objects.filter(
        booking_status="Pending", is_booking_date_active=True
    )

    for req in book_reqs:
        rest_id = int(req.rest_id)
        endpoint = f"{BASE_URL}/find"

        payload = {"booking_date": req.date, "rest_id": rest_id}
        response = requests.get(endpoint, data=payload)
        auth_token = req.user_token
        data = response.json()

        # Get Booking Token and try making a reservation.
        for slot in data["data"]["config_details"]:
            # Get Booking Token
            slot_time = datetime.datetime.strptime(slot["time"], "%H:%M:%S").time()
            if slot_time >= req.from_time and slot_time <= req.to_time:
                url = f"{BASE_URL}/get_booking_token"
                payload = {
                    "config_token": slot["config_token"],
                    "booking_date": slot["date"],
                    "party_size": slot["party_size"],
                }

                response = requests.post(url, data=payload)
                data = response.json()
                booking_token = data.get("data")
                logger.info(booking_token)

                # Making a reservation
                url = f"{BASE_URL}/make_booking"
                payload = {"booking_token": booking_token, "auth_token": auth_token}
                response = requests.post(url, data=payload)
                logger.info(response)
                logger.info(response.status_code)
                data = response.json()
                logger.info(data)
                if response.status_code == 201:
                    booking_status = True
                    req.booking_status = "Confirmed"
                    req.save()

                    book_det_obj = Booking_details(
                        booking_id=req.booking_id,
                        reservation_id=data["reservation_id"],
                        booking_status="Confirmed",
                        reservation_cnf_token=data["resy_token"],
                    )
                    book_det_obj.save()

                    break
        else:
            if booking_status is False:
                logger.info("All the slots are occupied for the date.")


@shared_task
def update_restaurants():
    Restaurant.objects.all().delete()
    current_date = today_date
    endpoint = f"{BASE_URL}/fetch_and_add_rest"

    response = requests.get(endpoint)
    data = response.json()
    if response.status_code == 201:
        logger.info("Restaurants List updated.")
    else:
        logger.info("Restaurants List could not be updated. Please try again.")


@shared_task
def update_auth_token():
    user_objs = User.objects.all()
    endpoint = f"{BASE_URL}/refresh_auth_token"
    payload = {}

    for req in user_objs:
        payload["resy_email"] = req.resy_email
        payload["resy_pwd"] = req.resy_pwd

        response = requests.post(endpoint, payload)
        data = response.json()
        req.user_token = data["token"]
        if response.status_code == 200:
            logger.info("Token refreshed.")
            req.save()
        else:
            logger.info("Failed to update Token.")
