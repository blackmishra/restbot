import datetime
import json
from celery import shared_task
import requests
from resy.models import Licenses_wo_add, Reservation_request, Restaurant
from celery.utils.log import get_task_logger
from rest_framework import status
from resy.views import SearchTemplateView


logger = get_task_logger(__name__)
base_url='http://127.0.0.1:8000/restbot'
oc_api_limit = 991
open_corporates_key = 'oiuMXS7IR9uXFbXeeQ9D'
google_maps_key = 'AIzaSyCMc9b59TwYBKOmiKgs5dpHQZnnysEp5tw'
estated_key = 'oTg71JShNoudAaLsCKAaKaTD1sJMSn'


  
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

        if req.remove_booking_req:
            req.delete()


@shared_task
def make_booking_req():
    book_reqs = Reservation_request.objects.filter(is_booking_date_active=True).values()
    base_url='http://127.0.0.1:8000/restbot'

    for req in book_reqs:
        rest_id = int(req['rest_id'])
        endpoint = f"{base_url}/search/{rest_id}"
        response = requests.get(endpoint)
        data = response.json()
        logger.info(data)

        # Get Booking Token and try making a reservation.
        for slot in data['data']['config_details']:

            # Get Booking Token
            url = f"{base_url}/get_booking_token"

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
            url = f"{base_url}/make_booking"

            payload = {"booking_token": booking_token}
            response = requests.post(url, data=payload)
            data = response.json()
            logger.info(data['status'])
            logger.info(data)
            break
        break


@shared_task
def update_restaurants():
    Restaurant.objects.all().delete()
    current_date = str(datetime.date.today())

    endpoint = f"{base_url}/fetch_and_add_rest"

    response = requests.post(endpoint)
    data = response.json()
    if response.status_code==201:
        logger.info("Restaurants List updated.")
    else:
        logger.info("Restaurants List could not be updated. Please try again.")


def update_address(uuid, address):
    # rec.address = address
    try:
        Licenses_wo_add.objects.get(id=uuid).using('pelorus').update(address=address)

        # rec.save(save_fields=['address'])
        logger.info('Record updated successfully.')
        return True
    except Exception as e:
        logger.info('Could not update the record.')
        return False


@shared_task
def fetch_addresses():
    add_not_found_count=0
    values = Licenses_wo_add.objects.all().values().using('pelorus')[:oc_api_limit]
    logger.info('Printing results from Pelorus table.')
    # Find business address from OpenCorporates when not available
    for item in values:
        business_name = str(item['business_legal_name'])
        state_name = str(item['state'])
        if item.get('address') is None:
            
            parameters = {
                'api_token': open_corporates_key,
                'q': business_name + ", "+ str(state_name),
                'order': 'score'
            }
            response = requests.get('https://api.opencorporates.com/v0.4/companies/search', params=parameters)
            response = response.json()
            address = '~'
            try:
                if response['results'] and len(response['results']['companies']) > 0 and response['results']['companies'][0]['company']['registered_address_in_full']:
                    address = response['results']['companies'][0]['company']['registered_address_in_full']
                    logger.info(address)
                    logger.info('Trying to update address of %s', item['id'])

                    update_address(item['id'], address)

                # item['address'] = address
            except Exception as e:
                logger.info('Could not found the address of %s', business_name)
                add_not_found_count+=1

    logger.info('Could not found the addresses of %s businesses', add_not_found_count)
    return add_not_found_count, values









            


