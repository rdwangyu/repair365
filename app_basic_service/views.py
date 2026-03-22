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


'''
def login(request):
    data = json.loads(request.body)
    if 'code' not in data:
        return JsonResponse(create_response_data(-1, 'missing parameters'))

    master = UserMasterModel.objects.filter(openid=wx_resp['openid'])
    if master:
        master.update(
            access_token=wx_resp['session_key'],
            token_expired = timezone.now() + timedelta(days=7)
        )    
    else:
        customer = UserCustomerModel.objects.filter(openid=wx_resp['openid'])
        if not customer:
            customer = UserCustomerModel.objects.create(
                openid=wx_resp['openid'],
            )
            if not customer:
                return JsonResponse(create_response_data(-1, 'failed to register customer'))
        customer.update(
            access_token=wx_resp['session_key'],
            token_expired = timezone.now() + timedelta(days=7)
        )    
    return JsonResponse(create_response_data(errmsg='login success'))
'''

def updateCustomerProfile(request):
    data = json.loads(request.body) # todo: use request.data
    if 'openid' not in data:
        return JsonResponse(create_response_data(-1, "missing parameters"))
        
    data_updated = {}
    if 'nickname' in data:
        data_updated['nickname'] = data['nickname']
    if 'phone' in data:
        data_updated['phone'] = data['phone']
    if 'sex' in data:
        data_updated['sex'] = data['sex']
    if 'age' in data:
        data_updated['age'] = data['age']
    if not data_updated:
        return JsonResponse(create_response_data(-1, 'missage updated parameters'))
    customer = UserCustomerModel.objects.filter(openid=data['openid'])
    if not customer:
        return JsonResponse(create_response_data(-1, f'user({data["openid"]}) not found'))
    rows = customer.update(**data_updated)
    return JsonResponse(create_response_data(result={'updated': rows}))

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
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_400_NOT_FOUND)
        serializer = UserMasterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result=serializer.data))

    def delete(self, request):
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(-1, 'user not found', status=status.HTTP_400_NOT_FOUND)
        data = { 'account_status': 3}
        serializer = UserMasterSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(create_response_data(result='delete success'))
        

def updateMasterProfile(request):
    data = json.loads(request.body)
    try:
        master = UserMasterModel.objects.get(openid=data['openid'])
    except UserMasterModel.DoesNotExist:
        return JsonResponse(create_response_data(-1, 'user not found'), status=status.HTTP_404_NOT_FOUND)

    serializer = UserMasterSerializer(master, data=data, partial=True)
    if serializer.is_valie():
        serializer.save()
    else:
        return JsonResponse(create_request.data(-1, 'check not pass'), status=status.HTTP_400_BAD_REQUEST)
        
    return JsonResponse(create_response_data(result=serializer.data))


def deleteUser(request):
    data = json.loads(request.body)
    openid = data['openid']
    customer = UserCustomerModel.objects.filter(openid=openid)
    if customer:
        customer.update(account_status=2)
    else:
        master = UserMasterModel.objects.filter(openid=openid)
        if master:
            master.update(account_status=3)
        else:
            return JsonResponse(create_request_data(-1, 'user not found', status=status.HTTP_400_BAD_REQUEST))
    return JsonResponse(create_response_data(0))


class RepireOrderView(APIView):
    def get(self, request):
        return JsonResponse(create_response_data())


    def post(self, request):
        return JsonResponse(create_response_data())


    def put(self, request):
        return JsonResponse(create_respnse_data())


    def delete(self, request):
        return JsonResponse(create_response_data())





