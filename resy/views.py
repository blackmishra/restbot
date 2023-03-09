from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Resy
from .serializers import ResySerializer
from rest_framework.renderers import JSONRenderer
import json 
import requests


class ResyListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

   # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # data = {'user_count': 100}
        # url='https://api.resy.com/3/venuesearch/search'
        # payload = json.dumps({
        #     "availability": True,
        #     "page": 1,
        #     "per_page": 1882,
        #     "slot_filter": {
        #         "day": "2023-02-21",
        #         "party_size": 2
        #     },
        #     "types": [
        #         "venue"
        #     ],
        #     "geo": {
        #         "latitude": 40.712941,
        #         "longitude": -74.006393,
        #         "radius": 35420
        #     },
        #     "query": ""
        # })
        # headers = {
        # 'authority': 'api.resy.com',
        # 'accept': 'application/json, text/plain, */*',
        # 'accept-language': 'en-GB,en;q=0.8',
        # 'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
        # 'cache-control': 'no-cache',
        # 'content-type': 'application/json',
        # 'origin': 'https://resy.com',
        # 'referer': 'https://resy.com/',
        # 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors',
        # 'sec-fetch-site': 'same-site',
        # 'sec-gpc': '1',
        # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        # 'x-origin': 'https://resy.com',
        # 'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC',
        # 'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC'
        # }
        # response = requests.post(url, headers=headers, data = payload)
        # print(response.status_code)
        # # data = json.loads(response.json)
        # data = response.json()

        # # All values
        # values = []
        # for item in data['search']['hits']:
        #     temp={}
        #     temp['name'] = item['name'],
        #     temp['id'] = item['id']['resy'],
        #     temp['rating'] = item['rating']['average'],
        #     temp['region'] = item['region'],
        #     temp['cuisine'] = item['cuisine'],
        #     temp['availability_dates'] = item['inventory_any'],
        #     temp['min_guests'] = item['min_party_size'],
        #     temp['max_guests'] = item['max_party_size'],
        #     temp['description'] = item['content'][0]['body']

        #     values.append(temp)

        #Search specific restaurant details
        url = "https://api.resy.com/4/find?lat=0&long=0&day=2023-03-12&party_size=2&venue_id=67398"

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
            'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC',
            'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        slots = data['results']['venues'][0]['slots']
        config_token = [item['config']['token'] for item in slots]
        print(config_token)

        # Slot selection

        url = "https://api.resy.com/3/details"
        # config_token[i] = "rgs://resy/64872/1981324/3/2023-03-25/2023-03-15/16:30:00/2/Dining Room"
        payload = json.dumps({
            "commit": 1,
            "config_id": config_token[2],
            "day": "2023-03-12",
            "party_size": 4
        })
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
            'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC',
            'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2Nzg0OTUwNzQsInVpZCI6Mzg4MDE2OTIsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMjkyNjQ1MDZ9fQ.APZepm-Z5Yl8ECqA315ub0p11SJcvItCrrIZch1mNMrW3tEONvU9h2bLeodTaADeY6ojUzalNP9iQ40CKqhLWxUXAd-OUBqtsfwvSn2zukd14d9WZb1WuPZCPv_8D8jG--hMw3vVjJwvtLDwr0pAefqf_IIl7bzXc74tujLKN24DQRtC'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        booking_token = data['book_token']['value']

        url = "https://api.resy.com/3/book"
        tk='QiUOIvEqCPoSthioWtZQKQM0W8wwg8uMqJeiHA7E8jPXW6OE0ZJBOinEkv45hnCNzFoazKuqacAnY7RS2GeOanNzOl_uk7D3x_ty96MFsXXPfucTWztDX7Mc4FuSKhNOCeDymhNQVUSRMi4Kv9v0N4Z1i1S%7CiwbEQY2nMi23lYojd0QH2xSDyvnkZdMzbG%7CxLUJ_sJJ_mlI9haYpGlMytkkCQx2k2w_g0B0_cZYbtL9eM5lSIISpq7TZ1duZgK7zgCU181NwUoK%7CFS7optqkQyoVmYRapXdDazqGKKur%7CK0S46o4%7CdrFsDJJVlvlO6j2CO%7C_1CrekK6zxNRtBtQ_7phoaRfoLNf_oCPc47vZKywa0o9kiNou0bJufVTj%7Cbkd_S9juGL_NbfqV2avQYn5iGsDjeazIE4wylwpcIXpDex3kaVFMg6Xkbg6KfPNQ5lpCiPS04qQsxPeGCHbxxrRpsTjt2unVK_IzZh6cCTZ%7CZdbOXZQUclqif79z8Z7JAj5_6XbsnXWFoXkFXtRiHA6kvh7Xp9D2P%7CuWkkiTsSfIjEpT%7CLc7dTiL6NrYa8SEP4FPDEGbHKfyYFkXV%7CFf8nX7Ji1JCAdednyPKMj73pbzU17a460_PACU68j71SoqFcs83kfRqQFJ8ePxrgAYzlQdytn8_1NGlKzT7aUB0fDtsCriA_gtOObGwXJB9Vk8PbG-aa6c78da556300ef4530985951fab3f7f2075efbbc77bc10a79e682a'
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
            'x-origin': 'https://widgets.resy.com',
            'x-resy-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2ODE5OTA3MDEsInVpZCI6NDAwMzk5NjMsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMzIxNDYwMTl9fQ.AFsRxEXMVczhJA5rg3dY5w_lG2I2RjywWST3hSeTV6iwataTtiOgU8DYS0BEtjLfbv2ZP00tC-gTL1J2ocu7KSU5ANIW3nzu3Axn7LWFdYVrmD4uCD_WndQFbxRZTTveXfrlifFZLAw-ckNFZOpsxdcY1Q69YEqSNbvxuZEyNYF5m94F',
            'x-resy-universal-auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2ODE5OTA3MDEsInVpZCI6NDAwMzk5NjMsImd0IjoiY29uc3VtZXIiLCJncyI6W10sImV4dHJhIjp7Imd1ZXN0X2lkIjoxMzIxNDYwMTl9fQ.AFsRxEXMVczhJA5rg3dY5w_lG2I2RjywWST3hSeTV6iwataTtiOgU8DYS0BEtjLfbv2ZP00tC-gTL1J2ocu7KSU5ANIW3nzu3Axn7LWFdYVrmD4uCD_WndQFbxRZTTveXfrlifFZLAw-ckNFZOpsxdcY1Q69YEqSNbvxuZEyNYF5m94F'
        }
        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        return Response(data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = {
            'task': request.data.get('task'), 
            'completed': request.data.get('completed'), 
            'user': request.user.id
        }
        serializer = ResySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)