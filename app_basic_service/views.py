from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from datetime import timedelta
import requests
import json
from .models import *

def create_response_data(errcode = 0, errmsg = '', result = {}):
    return {'errcode': errcode, 'errmsg': errmsg, 'result': result}

# Create your views here.
def login(request):
    data = json.loads(request.body)
    if 'code' not in data:
        return JsonResponse(create_response_data(-1, 'missing parameters'))

    wx_resp = {}
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': 'PPwx2576c4210717a45b',
        'secret': 'f03e98a6fdcac7e37390cf2b2bb4a986',
        'js_code': data['code'],
        'grant_type': 'authorization_code',
    }
    try:
        wx_resp = requests.get(url, params=params, timeout=5)
        wx_resp = wx_resp.json()
        wx_resp = {'openid': 'test1234openid', 'session_key': 'session123'} # test
        if 'openid' not in wx_resp:
            return JsonResponse(create_response_data(-1))
    except Exception as e:
        return JsonResponse(create_response_data(-1, f'failed to request wx api: {e}'))

    print('wx response: ', wx_resp)
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


def updateCustomerProfile(request):
    data = json.loads(request.body)
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











