from typing import Any
from rest_framework.decorators import api_view
import ast
import datetime
import json
import uuid
from datetime import date, datetime

import requests
import yagmail
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from resybookingproject import constants as CONST


from .models import Reservation_request, Restaurant, Resy, User
from .serializers import (
    BookingSerializer,
    RestaurantSerializer,
    ResySerializer,
    UserSerializer,
)


today_date = date.today()


def send_email(subject, message, to_email=CONST.DEFAULT_RECEPIENT):
    from_email = CONST.SENDER_EMAIL
    user = yagmail.SMTP(user=from_email, password=CONST.SENDER_PASSWORD)
    user.send(to=to_email, subject=subject, contents=message)


class SearchTemplateView(TemplateView):
    template_name = "index.html"
    context = {}

    def get_context_data(self, *args, **kwargs):
        """
        List all available restaurants.
        """
        url = CONST.SEARCH_API
        payload = json.dumps(
            {
                "availability": True,
                "page": 1,
                "per_page": 5000,
                "slot_filter": {"day": "2023-04-21", "party_size": 2},
                "types": ["venue"],
                "geo": {
                    "latitude": 40.712941,
                    "longitude": -74.006393,
                    "radius": 35420,
                },
                "query": "",
            }
        )
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
            # 'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC',
            # 'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC'
        }
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        # All values
        values = []
        for item in data["search"]["hits"]:
            temp = {}
            temp["name"] = (item["name"],)
            temp["id"] = (item["id"]["resy"],)
            temp["rating"] = (round(item["rating"]["average"], 2),)
            temp["image"] = (
                item["images"][0] if item["images"] else CONST.IMG_NOT_AVAIALABLE_ICON
            )
            temp["region"] = (item["region"],)
            temp["cuisine"] = (item["cuisine"],)
            temp["availability_dates"] = (item["inventory_any"],)
            temp["min_guests"] = (item["min_party_size"],)
            temp["max_guests"] = (item["max_party_size"],)
            temp["description"] = item["content"][0]["body"]
            values.append(temp)

        values = sorted(values, key=lambda d: d["name"])
        self.context["data"] = values
        return self.context


class RestTemplateView(APIView):
    context = {}

    def get(self, request, *args, **kwargs):
        rest_id = request.data.get("rest_id") or None
        current_date = request.data.get("booking_date") or today_date
        # Search specific restaurant details
        url = f"{CONST.FIND_REST_API}{current_date}&party_size=2&venue_id={rest_id}"
        payload = {}
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        rest_details = {}
        rest_details["date"] = current_date
        rest_details["venue_id"] = rest_id

        if data["results"]["venues"]:
            item = data["results"]["venues"][0]
            rest_details["name"] = item["venue"]["name"]
            status = "200"
            slots = item["slots"]
            config_details = []
            for item in slots:
                slot_details = {}
                details = item["config"]["token"].split("/")
                time, sitting_type = details[-3], details[-1]
                slot_details["party_size"] = details[-2]
                slot_details["date"] = current_date
                slot_details["time"] = time
                slot_details["sitting_type"] = sitting_type
                slot_details["config_token"] = item["config"]["token"]
                config_details.append(slot_details)

            rest_details["config_details"] = config_details
            print(rest_details)
        else:
            status = "400"

        rest_details["status"] = status
        self.context["data"] = rest_details
        return Response(self.context)


class Session_save(APIView):
    def get(self, request):
        print(request.session["booking_details"])
        print(request.session["user_details"])

        # return Response("Session Data Saved. ", status=status.HTTP_201_CREATED)
        return redirect("booking_page")


class Request_booking(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.context = {}

    def get(self, request, *args, **kwargs):
        rest_objs = list(Restaurant.objects.all().order_by("rest_name").values())
        user_details = None
        booking_obj = request.session.get("booking_details")

        if request.session.get("user"):
            user_email = request.session.get("user")["userinfo"]["email"]
            user_queryset = User.objects.filter(user_email=user_email).values(
                "resy_email", "resy_pwd", "user_name", "user_email"
            )
            user_details = list(user_queryset)[0]
            if user_details:
                request.session["user_details"] = user_details
                print("Writing User details")
            else:
                print("User details not found")

        self.context = {
            "data": rest_objs,
            "session": request.session.get("user"),
            "booking_obj": booking_obj,
        }

        return render(request, "booking.html", self.context)

    def post(self, request, *args, **kwargs):
        """
        Create the reservation request with given data
        """

        if "btnform2" in request.POST:
            print("Random Joe 1")

            booking_details = {
                "date": request.data.get("date_picker"),
                "from_time": request.data.get("from_time"),
                "to_time": request.data.get("to_time"),
                "number_of_guests": request.data.get("guests_size"),
            }
            print("Random Joe 2")

            (
                booking_details["rest_name"],
                booking_details["rest_id"],
            ) = request.data.get("rest_name").split(",")
            print("Random Joe 3")
            user_details = []
            print(
                "Email and pwd: ",
                request.data.get("resy_email"),
                request.data.get("resy_pwd"),
            )
            if request.session.get("user"):
                user_details = {
                    "resy_email": request.data.get("resy_email"),
                    "resy_pwd": request.data.get("resy_pwd"),
                    "user_name": request.session.get("user")["userinfo"]["name"],
                    "user_email": request.session.get("user")["userinfo"]["email"],
                }
            print("User details:", user_details)
            if request.session.get("booking_details") is None:
                request.session["booking_details"] = booking_details
            if request.session.get("user_details") is None:
                request.session["user_details"] = user_details
            else:
                print(request.session.get("user_details"))

            # return render(request, "booking.html", self.context)
            # return Response("Session Data Saved. ", status=status.HTTP_201_CREATED)
            return redirect("save_in_session")

        print("Random Joe 4")
        print(
                "Email and pwd: ",
                request.data.get("resy_email"),
                request.data.get("resy_pwd"),
            )
        user_details = request.session.get("user_details")
        print(user_details)



        if user_details is None:
            if request.session.get("user"):
                session_email = request.session.get("user")["userinfo"]["email"]
                session_name = request.session.get("user")["userinfo"]["name"]
            else:
                session_email = request.data.get("resy_email")
                session_name = request.data.get("resy_email")

            user_details = {
                "resy_email": request.data.get("resy_email"),
                "resy_pwd": request.data.get("resy_pwd"),
                "user_name": session_name,
                "user_email": session_email,
            }
        print(user_details)
        rest_name = request.session["booking_details"]["rest_name"]
        rest_id = request.session["booking_details"]["rest_id"]
        booking_id = str(uuid.uuid1())
        resy_email = user_details["resy_email"] if user_details else None
        resy_pwd = user_details["resy_pwd"] if user_details else None
        data = {
            "rest_name": rest_name,
            "rest_id": rest_id,
            "date": request.session["booking_details"]["date"],
            "number_of_guests": (
                request.session["booking_details"]["number_of_guests"]
            ),
            "booking_available_till": today_date,
            "from_time": request.session["booking_details"]["from_time"],
            "to_time": request.session["booking_details"]["to_time"],
            "booking_id": booking_id,
        }
        if resy_email and resy_pwd:
            user_data = {
                "resy_email": resy_email,
                "resy_pwd": resy_pwd,
                "user_email": user_details["user_email"] or None,
                "user_name": user_details["user_name"] or None,
            }
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()

        serializer = BookingSerializer(data=data)
        context = {}

        if serializer.is_valid():
            serializer.save()

            subject = "Booking Request: Successfully created."
            message = (
                f"{subject} \n\n Your Booking ID : {booking_id}. \n\n"
                f"\nYou may receive another notification when your reservation is confirmed."
                f"This mail is just to inform you that we have received your booking request. "
                f"It does not guarentee you will get the reservation."
            )

            context["result"] = serializer.data
            context["message"] = message

            send_email(subject, context["message"], resy_email)
            return render(
                request,
                context=context,
                status=status.HTTP_201_CREATED,
                template_name="status.html",
            )
        context["result"] = serializer.errors
        context[
            "message"
        ] = "BAD INPUT. Booking Request: Failed to create. Please try again with valid input."
        print(context)

        return render(
            request,
            context=context,
            status=status.HTTP_400_BAD_REQUEST,
            template_name="status.html",
        )


class Populate_Restaurants(APIView):
    def get(self, request, *args, **kwargs):
        current_date = str(today_date)
        # print(str(current_date))
        # print(current_date.strftime('%Y-%m-%d'))
        url = CONST.SEARCH_API
        payload = json.dumps(
            {
                "availability": True,
                "page": 1,
                "per_page": 5000,
                "slot_filter": {"day": current_date, "party_size": 2},
                "types": ["venue"],
                "geo": {
                    "latitude": 40.712941,
                    "longitude": -74.006393,
                    "radius": 35420,
                },
                "query": "",
            }
        )
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
        }
        response = requests.post(url, headers=headers, data=payload)
        print(response.status_code)
        data = response.json()

        # All values
        validated_data = []
        try:
            for item in data["search"]["hits"]:
                validated_data.append([item["name"], item["id"]["resy"]])

            rest_data = [
                Restaurant(rest_name=item[0], rest_id=item[1])
                for item in validated_data
            ]
            Restaurant.objects.bulk_create(rest_data)
            return Response("All records inserted.", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                "Insertion failed. " + str(e), status=status.HTTP_400_BAD_REQUEST
            )


class Get_Booking_Token(APIView):
    def post(self, request, *args, **kwargs):
        config_token = request.data.get("config_token")
        booking_date = request.data.get("booking_date")
        party_size = request.data.get("party_size")

        url = CONST.DETAILS_API
        payload = json.dumps(
            {
                "commit": 1,
                "config_id": config_token,
                "day": booking_date,
                "party_size": party_size,
            }
        )

        print(payload)
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://widgets.resy.com",
            "referer": "https://widgets.resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "x-origin": "https://widgets.resy.com",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        print(data)
        booking_token = data["book_token"]["value"]

        return Response({"data": booking_token})


class Make_Booking(APIView):
    def post(self, request, *args, **kwargs):
        booking_token = request.data.get("booking_token")
        auth_token = request.data.get("auth_token")
        url = CONST.BOOKING_API
        payload = f"book_token={booking_token}&source_id=resy.com-venue-details"

        # add replace = 1 in payload to update booking slot
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://widgets.resy.com",
            "referer": "https://widgets.resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "x-origin": "https://widgets.resy.com",
        }
        headers["x-resy-auth-token"] = auth_token
        headers["x-resy-universal-auth"] = auth_token
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
            print(response.status_code)
            data = response.json()
            print(data)
        except Exception as e:
            return Response(
                "Booking Request Failed to create. " + str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if response.status_code == 201:
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(data, status=response.status_code)


class Add_Restaurant(APIView):
    def get(self, request, *args, **kwargs):
        self.context = {"data": None}
        return render(request, "add_rest.html", self.context)

    def post(self, request, *args, **kwargs):
        rest_name = request.data.get("rest_name")
        print(rest_name)
        current_date = str(today_date)

        url = CONST.SEARCH_API

        payload = json.dumps(
            {
                "geo": {"latitude": 40.712941, "longitude": -74.006393},
                "highlight": {"pre_tag": "<b>", "post_tag": "</b>"},
                "per_page": 5,
                "query": rest_name,
                "slot_filter": {"day": current_date, "party_size": 2},
                "types": ["venue", "cuisine"],
            }
        )
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        records = data["search"]["hits"][0]
        if records:
            obj_id = records["objectID"]
            try:
                Restaurant.objects.get(rest_id=obj_id)
                message = "Restaurant already exists in DB."
                req_status = status.HTTP_409_CONFLICT
            except Restaurant.DoesNotExist:
                message = "Congrats! New Restaurant found and inserted."
                data = {}
                data["rest_id"] = obj_id
                data["rest_name"] = records["name"]
                serializer = RestaurantSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return render(
                        request,
                        context={"message": message},
                        status=status.HTTP_201_CREATED,
                        template_name="status.html",
                    )
                return render(
                    request,
                    context={"message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                    template_name="status.html",
                )
        else:
            message = "Could not find restaurant. Please try again.."
            req_status = status.HTTP_404_NOT_FOUND

        return render(
            request,
            context={"message": message},
            status=req_status,
            template_name="status.html",
        )


class User_auth_token(APIView):
    def post(self, request, *args, **kwargs):
        url = CONST.AUTH_API
        user_email = request.data.get("resy_email")
        user_pwd = request.data.get("resy_pwd")
        payload = f"email={user_email}&password={user_pwd}"
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.9",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        data = response.json()

        user_token = data["token"]
        context = {}
        context["details"] = data
        context["token"] = user_token

        return Response(context, status=status.HTTP_200_OK)


class Cancel_Booking(APIView):
    def get(self, request, *args, **kwargs):
        self.context = {"data": None}
        return render(request, "cancel_booking.html", self.context)

    def post(self, request, *args, **kwargs):
        headers = ast.literal_eval(settings.RESY_HEADERS)
        resy_url = CONST.CANCEL_API
        booking_id = request.data.get("booking_id")
        print(booking_id)
        req = Reservation_request.objects.get(booking_id=booking_id)
        auth_token = req.user_token
        reservation_cnf_token = req.reservation_cnf_token

        payload = f"resy_token={reservation_cnf_token}"
        headers["x-resy-auth-token"] = auth_token
        headers["x-resy-universal-auth"] = auth_token

        response = requests.request("POST", resy_url, headers=headers, data=payload)
        if response.status_code == 200:
            subject = "Booking Cancelled Successfully."
            message = f"Your Reservation with Booking-ID: {booking_id}, cancelled successfully."
            req.booking_status = "Cancelled"
            req.save()
            send_email(subject, message, req.resy_email)
        else:
            message = "Could not cancel the booking. Please try again."

        return render(
            request,
            context={"message": message},
            status=response.status_code,
            template_name="status.html",
        )


class Fetch_user(APIView):
    def get(self, request, *args, **kwargs):
        if request.session.get("user") is None:
            return redirect("login")
        return render(
            request,
            "user_page.html",
            context={
                "session": request.session.get("user"),
                "pretty": json.dumps(request.session.get("user"), indent=4),
            },
        )

    def post(self, request, *args, **kwargs):
        headers = ast.literal_eval(settings.RESY_HEADERS)
        resy_url = CONST.CANCEL_API
        booking_id = request.data.get("booking_id")
        print(booking_id)
        req = Reservation_request.objects.get(booking_id=booking_id)
        auth_token = req.user_token
        reservation_cnf_token = req.reservation_cnf_token

        payload = f"resy_token={reservation_cnf_token}"
        headers["x-resy-auth-token"] = auth_token
        headers["x-resy-universal-auth"] = auth_token

        response = requests.request("POST", resy_url, headers=headers, data=payload)
        if response.status_code == 200:
            subject = "Booking Cancelled Successfully."
            message = f"Your Reservation with Booking-ID: {booking_id}, cancelled successfully."
            req.booking_status = "Cancelled"
            req.save()
            send_email(subject, message, req.resy_email)
        else:
            message = "Could not cancel the booking. Please try again."

        return render(
            request,
            context={"message": message},
            status=response.status_code,
            template_name="status.html",
        )
