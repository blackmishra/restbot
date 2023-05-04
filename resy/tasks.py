import datetime
import json
from celery import shared_task
import requests
from resy.models import Reservation_request, Restaurant
from celery.utils.log import get_task_logger
from rest_framework import status
from resy.views import SearchTemplateView
from resybookingproject.settings import BASE_URL


logger = get_task_logger(__name__)


  
@shared_task
def update_is_booking_date_flag():
    book_reqs = Reservation_request.objects.all()
    current_date = str(datetime.date.today())

    url='https://api.resy.com/3/venuesearch/search'
    payload = json.dumps({
        "page": 1,
        "per_page": 5000,
        "slot_filter": {
            "day": current_date,
            "party_size": 2
        },
        "types": [
            "venue"
        ],
        "geo": {
            "latitude": 40.712941,
            "longitude": -74.006393,
            "radius": 35420
        },
        "query": ""
    })
    headers = {
        'authority': 'api.resy.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.8',
        'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://resy.com',
        'referer': 'https://resy.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'x-origin': 'https://resy.com',
        # 'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC',
        # 'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC'
    }
    response = requests.post(url, headers=headers, data = payload)
    data = response.json()

    # All values
    values = {}
    for item in data['search']['hits']:
        temp={}
        temp['name'] = item['name'],
        temp['id'] = item['id']['resy'],
        temp['availability_dates'] = item['inventory_any'],

        values[item['id']['resy']] = temp

    # logger.info(list(values.keys()))

    for req in book_reqs:

        # booking_date = getattr(req, 'date')
        rest_id = getattr(req, 'rest_id')
        logger.info(rest_id)

        date_str = values[rest_id]['availability_dates'][-1][-1]
        
        req.booking_available_till = datetime.date(*map(int, date_str.split('-')))
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
    booking_staus=False
    book_reqs = Reservation_request.objects.filter(is_booking_date_active=True)

    for req in book_reqs:
        req_values = list(req.values())
        rest_id = int(req_values['rest_id'])
        endpoint = f"{BASE_URL}/search/{rest_id}"
        response = requests.get(endpoint)

        data = response.json()
        logger.info(data)

        # Get Booking Token and try making a reservation.
        for slot in data['data']['config_details']:

            # Get Booking Token
            url = f"{BASE_URL}/get_booking_token"

            payload = {
                "config_token": slot['config_token'],
                "booking_date": slot['date'],
                "party_size": slot['party_size']
            }

            response = requests.post(url, data=payload)
            data = response.json()
            logger.info(data)
            booking_token = data.get('data')
            #Making a reservation
            url = f"{BASE_URL}/make_booking"

            payload = {"booking_token": booking_token}
            response = requests.post(url, data=payload)
            data = response.json()
            logger.info(data['status'])
            logger.info(data)
            if response.status_code==201:
                booking_staus = True
                break
        else:
            if booking_staus:
                req.booking_status = 'Confirmed'
                req.save()


@shared_task
def update_restaurants():
    Restaurant.objects.all().delete()
    current_date = str(datetime.date.today())

    endpoint = f"{BASE_URL}/fetch_and_add_rest"

    response = requests.post(endpoint)
    data = response.json()
    if response.status==status.HTTP_201_CREATED:
        logger.info("Restaurants List updated.")
    else:
        logger.info("Restaurants List could not be updated. Please try again.")


@shared_task
def update_auth_token():
    book_reqs = Reservation_request.objects.all()

    current_date = str(datetime.date.today())

    endpoint = f"{BASE_URL}/refresh_auth_token"
    payload = {}
    logger.info('Inside task function')
    print('Inside task function')

    for req in book_reqs:
        req_values = list(req.values())
        payload['resy_email'] = req_values['resy_email']
        payload['resy_pwd'] = req_values['resy_pwd']
        logger.info(payload)
        response = requests.post(endpoint, payload)
        data = response.json()
        logger.info(response)
        logger.info(data)
        req.user_token = data['token']
        req.save()
