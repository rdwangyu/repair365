from django.http import JsonResponse # todo: delete after
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
import requests
import json
from .models import *
from .serializers import *
from rest_framework import status
import random

def create_response_data(errcode = 0, errmsg = '', result = {}):
    return {'errcode': errcode, 'errmsg': errmsg, 'result': result}

def login_wechat(code):
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': 'PPwx2576c4210717a45b',
        'secret': 'f03e98a6fdcac7e37390cf2b2bb4a986',
        'js_code': code,
        'grant_type': 'authorization_code',
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        result = {'openid': 'test1234openid', 'session_key': 'session123'} # test
    except Exception as e:
        return create_response_data(-1, f'failed to request api: {e}')

    return create_response_data(result=result)


class UserCustomerView(APIView):
    def post(self, request):
        if 'code' not in request.data:
            return Response(create_response_data(-1, 'code not found'))

        login_response = login_wechat(request.data.get('openid'))
        if login_response['errcode'] != 0:
            return Response(create_response_data(-1, f"failed to login({login_response['errcode']}'): {login_response['errmsg']}"))

        data = {
            'openid': login_response['result']['openid'],
            'access_token': login_response['result']['session_key'],
            'token_expired': timezone.now() + timedelta(days=7)
        }
        
        serializer = UserCustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
        return Response(create_response_data(result=serializer.data))

    def put(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token not found'))
        try:
            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserCustomerSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result=serializer.data))


    def delete(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token not found'))
        try:

            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'), status=status.HTTP_404_NOT_FOUND)
        data = {'account_status': 2}
        serializer = UserCustomerSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result='delete success'))



'''
User Master

'''
class UserMasterView(APIView):
    # login
    def post(self, request):
        if 'code' not in request.data:
            return Response(create_response_data(-1, 'code not found'))

        login_response = login_wechat(request.data.get('openid'))
        if login_response['errcode'] != 0:
            return Response(create_response_data(-1, f"failed to login({login_response['errcode']}'): {login_response['errmsg']}"))

        data = {
            'openid': login_response['result']['openid'],
            'access_token': login_response['result']['session_key'],
            'token_expired': timezone.now() + timedelta(days=7),
            'fullname': request.data.get('fullname'),
            'age': request.data.get('age'),
            'sex': request.data.get('sex'),
            'phone': request.data.get('phone'),
            'address': request.data.get('address'),
            'work_year': request.data.get('work_year'),
            'avatar': request.data.get('avatar'),
            'identity_card_0': request.data.get('identity_card_0'),
            'identity_card_1': request.data.get('identity_card_1'),
            'business_license': request.data.get('business_license'),
        }
        serializer = UserMasterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
        return Response(create_response_data(result=serializer.data))

    def put(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token not found'))
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_404_NOT_FOUND)
        serializer = UserMasterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result=serializer.data))

    def delete(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token not found'))
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_404_NOT_FOUND)
        data = { 'account_status': 3}
        serializer = UserMasterSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result='delete success'))




'''
Repair Order

'''
class RepairOrderView(APIView):
    def get(self, request):
        return JsonResponse(create_response_data())

    def post(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token not fount'))

        try:
            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_404_NOT_FOUND)

        data = {
            'order_number': f"BYQG{timezone.now().strftime('%Y%m%d%H%M%s')}{random.randint(0, 999)}",
            'sponsor': user.id,
            'location': request.data.get('location'),
            'repair_category': request.data.get('repair_category'),
            'contact_phone': request.data.get('contact_phone'),
            'issue_description': request.data.get('issue_description'),
        }
        if 'appointment_time' in request.data:
            data['appointment_time'] = request.data.get('appointment_time')
        if 'comment' in request.data:
            data['comment'] = request.data.get('comment')

        serializer = RepairOrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result=serializer.data))
            


    def put(self, request):
        return JsonResponse(create_respnse_data())


    def delete(self, request):
        return JsonResponse(create_response_data())








