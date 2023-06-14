from django.template import RequestContext
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from resybookingproject.settings import BASE_URL
from .models import Reservation_request, Restaurant, Resy
from .serializers import BookingSerializer, RestaurantSerializer, ResySerializer
from rest_framework.renderers import JSONRenderer
from django.views.generic.base import TemplateView
import json 
import requests
from django.shortcuts import render
from datetime import date, datetime
import datetime
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
import yagmail



def send_email(subject, message, to_email = 'mishra.shashank9598@gmail.com'):
    from_email = 'rockdtaz@gmail.com'
    user = yagmail.SMTP(user=from_email, password='scxywbidvtgmkwqp')
    user.send(to=to_email, subject=subject, contents=message)
    
class SearchTemplateView(TemplateView):
    template_name = 'index.html'
    context={}

    def get_context_data(self, *args, **kwargs):
        '''
        List all available restaurants.
        '''

        url='https://api.resy.com/3/venuesearch/search'
        payload = json.dumps({
            "availability": True,
            "page": 1,
            "per_page": 5000,
            "slot_filter": {
                "day": "2023-04-21",
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
        values = []
        for item in data['search']['hits']:
            temp={}
            temp['name'] = item['name'],
            temp['id'] = item['id']['resy'],
            temp['rating'] = round(item['rating']['average'], 2),
            temp['image'] = item['images'][0] if item['images'] else 'https://upload.wikimedia.org/wikipedia/commons/d/d1/Image_not_available.png'
            temp['region'] = item['region'],
            temp['cuisine'] = item['cuisine'],
            temp['availability_dates'] = item['inventory_any'],
            temp['min_guests'] = item['min_party_size'],
            temp['max_guests'] = item['max_party_size'],
            temp['description'] = item['content'][0]['body']
            values.append(temp)

        values = sorted(values, key=lambda d: d['name']) 
        self.context['data'] = values
        return self.context
    

class RestTemplateView(APIView):
    context={}

    def get(self, request, *args, **kwargs):
        
        rest_id = request.data.get('rest_id') or None
        current_date = request.data.get('booking_date') or datetime.date.today()
        #Search specific restaurant details
        url = f"https://api.resy.com/4/find?lat=0&long=0&day={current_date}&party_size=2&venue_id={rest_id}"
        payload={}
        headers = {
            'authority': 'api.resy.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.8',
            'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            'cache-control': 'no-cache',
            'origin': 'https://resy.com',
            'referer': 'https://resy.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'x-origin': 'https://resy.com',  
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        rest_details={}
        rest_details['date'] = current_date
        rest_details['venue_id'] = rest_id

        if data['results']['venues']:
            item = data['results']['venues'][0]
            rest_details['name'] = item['venue']['name']
            status='200'
            slots = item['slots']
            config_details = []
            for item in slots:
                slot_details={}
                details = item['config']['token'].split('/')
                time, sitting_type = details[-3], details[-1]
                slot_details['party_size'] = details[-2]
                slot_details['date'] = current_date
                slot_details['time'] = time
                slot_details['sitting_type'] = sitting_type
                slot_details['config_token'] = item['config']['token']
                config_details.append(slot_details)

            rest_details['config_details'] = config_details
            print(rest_details)
        else:
            status='400'

        rest_details['status'] = status
        self.context['data'] = rest_details
        return Response(self.context)


class Request_booking(APIView):

    def get(self, request, *args, **kwargs):
        rest_objs = list(Restaurant.objects.all().order_by('rest_name').values())
        context = { 'data': rest_objs}
        return render(request, 'booking.html', context) 

    def post(self, request, *args, **kwargs):
        '''
        Create the reservation request with given data
        '''
        rest_name, rest_id = request.data.get('rest_name').split(',')
        booking_id = str(uuid.uuid1())
        resy_email = request.data.get('resy_email')
        data = {
            'rest_name': rest_name, 
            'rest_id': rest_id, 
            'date': request.data.get('date_picker'), 
            'number_of_guests': request.data.get('num_guests') or request.data.get('guests_size'),
            'booking_available_till': datetime.date.today(),
            'resy_email': resy_email,
            'resy_pwd': request.data.get('resy_pwd'),
            'from_time': request.data.get('from_time'),
            'to_time': request.data.get('to_time'),
            'booking_id': booking_id,
        }

        serializer = BookingSerializer(data=data)
        context = {}

        if serializer.is_valid():
            serializer.save()

            subject = 'Booking Request: Successfully created.'
            message = f"{subject} \n\n Your Booking ID : {booking_id}. \n\n\nYou may receive another notification when your reservation is confirmed. This mail is just to inform you that we have received your booking request. It does not guarentee you will get the reservation."

            context['result'] = serializer.data
            context['message'] = message

            send_email(subject, context['message'], resy_email)
            return render(request, context=context, status=status.HTTP_201_CREATED, template_name='status.html')
        context['result'] = serializer.errors
        context['message'] = 'BAD INPUT. Booking Request: Failed to create. Please try again with valid input.'
        print(context)

        return render(request, context=context, status=status.HTTP_400_BAD_REQUEST, template_name='status.html')

class Populate_Restaurants(APIView):
    def get(self, request, *args, **kwargs):

        current_date = str(datetime.date.today())
        # print(str(current_date))
        # print(current_date.strftime('%Y-%m-%d'))
        url='https://api.resy.com/3/venuesearch/search'
        payload = json.dumps({
            "availability": True,
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
        }
        response = requests.post(url, headers=headers, data = payload)
        print(response.status_code)
        data = response.json()

        # All values
        validated_data = []
        try:
            for item in data['search']['hits']:
                validated_data.append([item['name'], item['id']['resy']])

            rest_data = [Restaurant(rest_name=item[0], rest_id=item[1]) for item in validated_data]
            Restaurant.objects.bulk_create(rest_data)
            return Response("All records inserted.", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response("Insertion failed. "+str(e), status=status.HTTP_400_BAD_REQUEST)


class Get_Booking_Token(APIView):
    def post(self, request, *args, **kwargs):
        config_token = request.data.get('config_token')
        booking_date = request.data.get('booking_date')
        party_size = request.data.get('party_size')

        url = "https://api.resy.com/3/details"
        payload = json.dumps({
            "commit": 1,
            "config_id": config_token,
            "day": booking_date,
            "party_size": party_size
        })

        print(payload)
        headers = {
            'authority': 'api.resy.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.8',
            'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://widgets.resy.com',
            'referer': 'https://widgets.resy.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'x-origin': 'https://widgets.resy.com',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        print(data)
        booking_token = data['book_token']['value']

        return Response({'data':booking_token})

class Make_Booking(APIView):
    def post(self, request, *args, **kwargs):
        booking_token = request.data.get('booking_token')
        auth_token = request.data.get('auth_token')
        url = "https://api.resy.com/3/book"
        payload=f'book_token={booking_token}&source_id=resy.com-venue-details'
        
        # add replace = 1 in payload to update booking slot
        headers = {
            'authority': 'api.resy.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.8',
            'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://widgets.resy.com',
            'referer': 'https://widgets.resy.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'x-origin': 'https://widgets.resy.com'
            }
        headers['x-resy-auth-token'] = auth_token
        headers['x-resy-universal-auth'] = auth_token
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print(response.status_code)
            data = response.json()
            print(data)
        except Exception as e:
            return Response("Booking Request Failed to create. "+str(e), status=status.HTTP_400_BAD_REQUEST)

        if response.status_code==201:
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(data, status=response.status_code)


class Add_Restaurant(APIView):
    def get(self, request, *args, **kwargs):
        self.context={'data':None}
        return render(request, 'add_rest.html', self.context)


    def post(self, request, *args, **kwargs):
        rest_name = request.data.get('rest_name')
        print(rest_name)
        current_date = str(datetime.date.today())

        url = "https://api.resy.com/3/venuesearch/search"

        payload = json.dumps({
        "geo": {
            "latitude": 40.712941,
            "longitude": -74.006393
        },
        "highlight": {
            "pre_tag": "<b>",
            "post_tag": "</b>"
        },
        "per_page": 5,
        "query": rest_name,
        "slot_filter": {
            "day": current_date,
            "party_size": 2
        },
        "types": [
            "venue",
            "cuisine"
        ]
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
        'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'x-origin': 'https://resy.com'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        records = data['search']['hits'][0]
        if records:
            obj_id = records['objectID']
            try:
                Restaurant.objects.get(rest_id=obj_id)
                message = 'Restaurant already exists in DB.'
                req_status = status.HTTP_409_CONFLICT
            except Restaurant.DoesNotExist:
                message = 'Congrats! New Restaurant found and inserted.'
                data={}
                data['rest_id'] = obj_id
                data['rest_name'] = records['name']
                serializer = RestaurantSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return render(request, context={'message': message}, status=status.HTTP_201_CREATED, template_name='status.html')
                return render(request, context={'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST, template_name='status.html')
        else:
            message="Could not find restaurant. Please try again.."
            req_status = status.HTTP_404_NOT_FOUND

        
        return render(request, context={'message': message}, status=req_status, template_name='status.html')
                

class User_auth_token(APIView):
    def post(self, request, *args, **kwargs):
        url = "https://api.resy.com/3/auth/password"
        user_email = request.data.get('resy_email')
        user_pwd = request.data.get('resy_pwd')
        payload=f"email={user_email}&password={user_pwd}"
        headers = {
            'authority': 'api.resy.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.9',
            'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://resy.com',
            'referer': 'https://resy.com/',
            'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'x-origin': 'https://resy.com'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        data = response.json()

        user_token = data['token']
        context = {}
        context['details'] = data
        context['token'] = user_token

        return Response(context, status=status.HTTP_200_OK)


class Cancel_Booking(APIView):
    def get(self, request, *args, **kwargs):
        self.context={'data':None}
        return render(request, 'cancel_booking.html', self.context)
    
    def post(self, request, *args, **kwargs):
        resy_url = "https://api.resy.com/3/cancel"
        booking_id = request.data.get('booking_id')
        print(booking_id)
        req = Reservation_request.objects.get(booking_id=booking_id)
        auth_token = req.user_token
        reservation_cnf_token = req.reservation_cnf_token

        payload=f"resy_token={reservation_cnf_token}"
        headers = {
            'authority': 'api.resy.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.9',
            'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://resy.com',
            'referer': 'https://resy.com/',
            'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'x-origin': 'https://resy.com'
        }
        headers['x-resy-auth-token'] = auth_token
        headers['x-resy-universal-auth'] = auth_token

        response = requests.request("POST", resy_url, headers=headers, data=payload)
        if response.status_code==200:
            subject = "Booking Cancelled Successfully."
            message = f"Your Reservation with Booking-ID: {booking_id}, cancelled successfully."
            req.booking_status="Cancelled"
            req.save()
            send_email(subject, message, req.resy_email)
        else:
            message = "Could not cancel the booking. Please try again."

        return render(request, context={'message': message}, status=response.status_code, template_name='status.html')
    


