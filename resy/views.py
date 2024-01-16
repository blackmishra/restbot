import ast
import datetime
import json
import uuid
from datetime import date, datetime, timedelta
from typing import Any
import re
import requests
import yagmail
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from dateutil import parser as date_parser


from resybookingproject import constants as CONST

from .models import Reservation_request, Restaurant, Resy, User, Restaurant_details
from .serializers import (
    BookingSerializer,
    RestaurantSerializer,
    ResySerializer,
    UserSerializer,
)

today_date = date.today()
tomorrow_date = date.today() + timedelta(days=1)
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
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
    "x-origin": "https://resy.com",
    "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "content-type": "application/json",
}


def send_email(subject, message, to_email=CONST.DEFAULT_RECEPIENT):
    from_email = CONST.SENDER_EMAIL
    user = yagmail.SMTP(user=from_email, password=CONST.SENDER_PASSWORD)
    user.send(to=to_email, subject=subject, contents=message)


class SearchTemplateView(APIView):
    # template_name = "index.html"
    # context = {}

    def get(self, request, *args, **kwargs):
        """
        List all available restaurants.
        """
        context = {}
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
        }
        response = requests.post(url, headers=headers, data=payload)
        print(response)
        data = response.json()

        # All values
        values = []
        for item in data["search"]["hits"]:
            temp = {}
            temp["name"] = item["name"]
            temp["id"] = item["id"]["resy"]
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
        context["data"] = values
        # return context
        return Response(values, status=status.HTTP_200_OK)


class RestTemplateView(APIView):
    context = {}

    def get(self, request, *args, **kwargs):
        # rest_id = request.data.get("rest_id") or None
        # current_date = request.data.get("booking_date") or today_date
        rest_id = self.kwargs.get("rest_id") or None
        # print(rest_id)
        current_date = self.kwargs.get("booking_date") or tomorrow_date
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
        # print(data)

        rest_details = {}
        rest_details["date"] = current_date
        rest_details["venue_id"] = rest_id

        if data["results"]["venues"]:
            item = data["results"]["venues"][0]
            template_details = next(iter(item.get("templates").values()))
            rest_details["images_list"] = template_details.get("images")
            rest_details["name"] = item["venue"]["name"]
            rest_details["rating"] = round(item["venue"]["rating"], 1)

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

        else:
            status = "400"

        rest_details["status"] = status
        self.context["data"] = rest_details
        # print(data)
        # return Response(self.context)
        return Response(rest_details, status=status)


class Request_booking(APIView):
    def get(self, request, *args, **kwargs):
        rest_objs = list(
            Restaurant.objects.all()
            .order_by("rest_name")
            .values("rest_name", "rest_id")
        )
        context = {"data": rest_objs}
        # return render(request, "booking.html", context)
        return Response(context, status=status.HTTP_200_OK)

    def format_dateTime(self, obj_type, obj):
        if obj_type == "Date":
            obj = obj.split("T")[0]
            obj = datetime.strptime(obj, "%Y-%m-%d").date()
        else:
            result = re.search("T(.*)Z", obj)
            if result:
                obj = result.group(1)
                obj = obj.split(".")[0]
            obj = datetime.strptime(obj, "%H:%M:%S").time()
        return obj

    def post(self, request, *args, **kwargs):
        """
        Create the reservation request with given data
        """
        print('Request Booking is getting called')
        rest_name, rest_id = request.data.get("rest_name").split(",")

        rervation_date = request.data.get("date_picker")
        rervation_date = self.format_dateTime("Date", rervation_date)

        from_time = request.data.get("time_slot")[0]
        from_time = self.format_dateTime("Time", from_time)

        to_time = request.data.get("time_slot")[1]
        to_time = self.format_dateTime("Time", to_time)

        booking_id = str(uuid.uuid1())
        data = {
            "rest_name": rest_name,
            "rest_id": int(rest_id),
            "date": rervation_date,
            "number_of_guests": request.data.get("guests_size"),
            "booking_available_till": today_date,
            "from_time": from_time,
            "to_time": to_time,
            "booking_id": booking_id,
        }

        serializer = BookingSerializer(data=data)
        context = {}

        if serializer.is_valid():
            serializer.save()

            subject = "Booking Request: Successfully created."
            message = f"{subject} \n\n Your Booking ID : {booking_id}. \n\n"
            f"\nYou may receive another notification when your reservation is confirmed. "
            f"This mail is just to inform you that we have received your booking request. "
            f"It does not guarentee you will get the reservation."

            booking_details = {
                "booking_id": booking_id,
                "subject": subject,
                "message": message,
            }
            context["result"] = serializer.data
            context["message"] = message
            request.session["booking_details"] = booking_details
            return Response("Booking created", status=status.HTTP_201_CREATED)

            # return redirect("fetch_user")
            # return render(
            #     request,
            #     context=context,
            #     status=status.HTTP_201_CREATED,
            #     template_name="user_page.html",
            # )

        context["result"] = serializer.errors
        context[
            "message"
        ] = "BAD INPUT. Booking Request: Failed to create. Please try again with valid input."

        # return render(
        #     request,
        #     context=context,
        #     status=status.HTTP_400_BAD_REQUEST,
        #     template_name="status.html",
        # )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        headers["content-type"] = "application/x-www-form-urlencoded"
        headers["x-resy-auth-token"] = auth_token
        headers["x-resy-universal-auth"] = auth_token
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()

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
            "origin": "https://resy.com",
            "referer": "https://resy.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "x-origin": "https://resy.com",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()

        records = data["search"]["hits"]
        if records:
            records = records[0]
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
        # headers["content-type"] = "application/x-www-form-urlencoded"

        response = requests.request("POST", url, headers=headers, data=payload)
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
        headers = {
            "authority": "api.resy.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.5",
            "authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://widgets.resy.com",
            "referer": "https://widgets.resy.com/",
            "sec-ch-ua": '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "x-origin": "https://widgets.resy.com",
        }
        resy_url = CONST.CANCEL_API
        booking_id = request.data.get("booking_id")
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
        user_queryset = None
        if request.session.get("user"):
            user_email = request.session.get("user")["userinfo"]["email"]
            user_queryset = User.objects.filter(user_email=user_email).values(
                "resy_email", "resy_pwd", "user_name", "user_email"
            )
            if user_queryset:
                request.session["user_details"] = (
                    list(user_queryset)[0] if user_queryset else None
                )

        booking_details = request.session.get("booking_details")

        return render(
            request,
            "user_page.html",
            context={
                "session": request.session.get("user"),
                "pretty": json.dumps(request.session.get("user"), indent=4),
                "booking_details": request.session.get("booking_details"),
                "user_details": list(user_queryset)[0] if user_queryset else None,
            },
        )

    def post(self, request, *args, **kwargs):
        if request.session.get("user_details") is None:
            data = {
                "resy_email": request.data.get("resy_email"),
                "resy_pwd": request.data.get("resy_pwd"),
                "user_name": request.data.get("resy_email"),
                "user_email": request.data.get("resy_email"),
            }
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                if User.objects.filter(user_email=data["user_email"]):
                    message = "User already exists."
                    req_status = status.HTTP_200_OK
                else:
                    serializer.save()
                    message = "Resy Details saved successfully."
                    req_status = status.HTTP_201_CREATED
                    request.session["user_details"] = data
                    if request.session.get("booking_details") is not None:
                        booking_details = request.session.get("booking_details")
                        Reservation_request.objects.filter(
                            booking_id=booking_details["booking_id"]
                        ).update(user_email=data["user_email"])

                        # Send Email on successfull booking_request
                        send_email(
                            booking_details["subject"],
                            booking_details["message"],
                            data["user_email"],
                        )
            else:
                message = serializer.errors
                req_status = status.HTTP_400_BAD_REQUEST

            return render(
                request,
                context={"message": message},
                status=req_status,
                template_name="status.html",
            )
        if request.session.get("booking_details") is not None and request.session.get(
            "user"
        ):
            booking_details = request.session.get("booking_details")
            user_email = request.session.get("user")["userinfo"]["email"]

            Reservation_request.objects.filter(
                booking_id=booking_details["booking_id"]
            ).update(user_email=user_email)

            send_email(
                booking_details["subject"],
                booking_details["message"],
                user_email,
            )

        return Response("Booking Completed.", status=status.HTTP_201_CREATED)


class BookingListView(ListView):
    model = Reservation_request
    template_name = "view_bookings.html"
    context_object_name = "booking_list"
    # paginate_by = 5

    def get_queryset(self):
        user_details = self.request.session.get("user")
        if not user_details:
            return redirect("fetch_user")

        if user_details.get("user_email"):
            user_email = user_details.get("user_email")
            return Reservation_request.objects.filter(user_email=user_email)
        return Reservation_request.objects.none()


class TestAPI(APIView):
    def get(self, request, *args, **kwargs):
        return Response("All good.", status=status.HTTP_200_OK)


class RestaurantDetails(APIView):
    def get(self, request, *args, **kwargs):
        rest_objs = list(
            Restaurant_details.objects.all()
            .order_by("rest_name")
            .values("rest_name", "rest_id", "rating", "location", "image")
        )
        # print(rest_objs[0])
        for item in rest_objs:
            item['name'] = [item['rest_name']]
        # print(rest_objs[:2])

        context = {"data": rest_objs}

        # return render(request, "booking.html", context)
        return Response(rest_objs, status=status.HTTP_200_OK)


class Populate_Restaurants_Details(APIView):
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
        print("Zero level")
        # All values
        validated_data = []
        try:
            for item in data["search"]["hits"]:
                validated_data.append(
                    [
                        item["name"],
                        item["id"]["resy"],
                        round(item["rating"]["average"], 2),
                        item["region"],
                        next(iter(item["images"] or []), CONST.IMG_NOT_AVAIALABLE_ICON)
                    ]
                )
            print("First pass")
            rest_data = [
                Restaurant_details(
                    rest_name=item[0],
                    rest_id=item[1],
                    image=item[4],
                    location=item[3],
                    rating=item[2],
                    # description=item[5],
                )
                for item in validated_data
            ]
            print("Second pass")

            Restaurant_details.objects.bulk_create(rest_data)
            print("Third pass")

            return Response("All records inserted.", status=status.HTTP_201_CREATED)
        except Exception as e:
            print(
                item["name"],
                item["id"]["resy"],
                item["rating"]["average"],
                item["region"],
                # item['content']['en-us']['about']['body'],
                next(iter(item["images"] or []), None)
            )
            return Response(
                "Insertion failed. " + str(e), status=status.HTTP_400_BAD_REQUEST
            )


class BookingRequest(APIView):
    def get(self, request, *args, **kwargs):
        rest_objs = list(
            Restaurant.objects.all()
            .order_by("rest_name")
            .values("rest_name", "rest_id")
        )
        context = {"data": rest_objs}
        # return render(request, "booking.html", context)
        return Response(context, status=status.HTTP_200_OK)

    def format_dateTime(self, obj_type, obj):
        if obj_type == "Date":

            obj = obj.split("GMT")[0].rstrip()
            print(obj)
            obj = datetime.strptime(obj, '%a %b %d %Y %H:%M:%S').date()
        else:
            result = re.search("T(.*)Z", obj)
            if result:
                obj = result.group(1)
                obj = obj.split(".")[0]
            obj = datetime.strptime(obj, "%H:%M").time()
        return obj

    def post(self, request, *args, **kwargs):
        """
        Create the reservation request with given data
        """
        print('Booking Request is getting called')

        rest_name  = request.data.get("rest_name")
        rest_id = request.data.get("rest_id")
        reservation_date = request.data.get("reservation_date")
        reservation_date = self.format_dateTime("Date", reservation_date)

        from_time = request.data.get("time_slot")
        # from_time = self.format_dateTime("Time", from_time)

        # to_time = request.data.get("time_slot")[1]
        # to_time = self.format_dateTime("Time", to_time)
        to_time = from_time
        print(rest_name, rest_id, reservation_date, from_time, to_time)


        booking_id = str(uuid.uuid1())
        data = {
            "rest_name": rest_name,
            "rest_id": int(rest_id),
            "date": reservation_date,
            "number_of_guests": request.data.get("guests_size"),
            "booking_available_till": today_date,
            "from_time": from_time,
            "to_time": to_time,
            "booking_id": booking_id,
        }

        serializer = BookingSerializer(data=data)
        context = {}
        print(data)
        if serializer.is_valid():
            serializer.save()

            subject = "Booking Request: Successfully created."
            message = f"{subject} \n\n Your Booking ID : {booking_id}. \n\n"
            f"\nYou may receive another notification when your reservation is confirmed. "
            f"This mail is just to inform you that we have received your booking request. "
            f"It does not guarentee you will get the reservation."

            booking_details = {
                "booking_id": booking_id,
                "subject": subject,
                "message": message,
            }
            context["result"] = serializer.data
            context["message"] = message
            request.session["booking_details"] = booking_details
            return Response("Booking created", status=status.HTTP_201_CREATED)

            # return redirect("fetch_user")
            # return render(
            #     request,
            #     context=context,
            #     status=status.HTTP_201_CREATED,
            #     template_name="user_page.html",
            # )

        context["result"] = serializer.errors
        context[
            "message"
        ] = "BAD INPUT. Booking Request: Failed to create. Please try again with valid input."

        # return render(
        #     request,
        #     context=context,
        #     status=status.HTTP_400_BAD_REQUEST,
        #     template_name="status.html",
        # )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Fetch_user_new(APIView):
    def get(self, request, *args, **kwargs):
        user_queryset = None
        if request.data.get("user"):
            user_email = request.session.get("user")["userinfo"]["email"]
            user_queryset = User.objects.filter(user_email=user_email).values(
                "resy_email", "resy_pwd", "user_name", "user_email"
            )
            if user_queryset:
                request.session["user_details"] = (
                    list(user_queryset)[0] if user_queryset else None
                )

        booking_details = request.session.get("booking_details")
        usr_obj = list(user_queryset)[0] if user_queryset else None
        if usr_obj:
            return Response(usr_obj, status=status.HTTP_200_OK)
        return Response(usr_obj, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        if request.session.get("user_details") is None:
            data = {
                "resy_email": request.data.get("resy_email"),
                "resy_pwd": request.data.get("resy_pwd"),
                "user_name": request.data.get("resy_email"),
                "user_email": request.data.get("resy_email"),
            }
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                if User.objects.filter(user_email=data["user_email"]):
                    message = "User already exists."
                    req_status = status.HTTP_200_OK
                else:
                    serializer.save()
                    message = "Resy Details saved successfully."
                    req_status = status.HTTP_201_CREATED
                    request.session["user_details"] = data
                    if request.session.get("booking_details") is not None:
                        booking_details = request.session.get("booking_details")
                        Reservation_request.objects.filter(
                            booking_id=booking_details["booking_id"]
                        ).update(user_email=data["user_email"])

                        # Send Email on successfull booking_request
                        send_email(
                            booking_details["subject"],
                            booking_details["message"],
                            data["user_email"],
                        )
            else:
                message = serializer.errors
                req_status = status.HTTP_400_BAD_REQUEST

            return render(
                request,
                context={"message": message},
                status=req_status,
                template_name="status.html",
            )
        if request.session.get("booking_details") is not None and request.session.get(
            "user"
        ):
            booking_details = request.session.get("booking_details")
            user_email = request.session.get("user")["userinfo"]["email"]

            Reservation_request.objects.filter(
                booking_id=booking_details["booking_id"]
            ).update(user_email=user_email)

            send_email(
                booking_details["subject"],
                booking_details["message"],
                user_email,
            )

        return Response("Booking Completed.", status=status.HTTP_201_CREATED)

