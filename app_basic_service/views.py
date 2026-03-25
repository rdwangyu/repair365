from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from datetime import timedelta
import requests
import json
from .models import *
from .serializers import *
from rest_framework import status
import random
from django.db.models import Q

def create_response_data(errcode = 0, errmsg = '', result = {}):
    return {'errcode': errcode, 'errmsg': errmsg, 'result': result}

def login_wechat(code):
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': 'wx2576c4210717a45b',
        'secret': 'f03e98a6fdcac7e37390cf2b2bb4a986',
        'js_code': code,
        'grant_type': 'authorization_code',
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        print(code, result)
    except Exception as e:
        return create_response_data(-1, f'failed to request api: {e}')

    if 'errcode' in result:
        return create_response_data(-1, result['errmsg'])
    return create_response_data(result=result)

class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_result(self, data):
        return {
            'orders': data,
            'pagination': {
                'current_page': self.page.number,
                'page_size': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_prev': self.page.has_previous(),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'prev_page': self.page.previous_page_number() if self.page.has_previous() else None,
            }
        }


class UserCustomerView(APIView):
    def post(self, request):
        if 'code' not in request.data:
            return Response(create_response_data(-1, 'code missing'))

        login_response = login_wechat(request.data.get('code'))
        if login_response['errcode'] != 0:
            return Response(create_response_data(-1, f"failed to login({login_response['errcode']}'): {login_response['errmsg']}"))

        openid = login_response['result']['openid']
        data = {
            'access_token': login_response['result']['session_key'],
            'token_expired': timezone.now() + timedelta(days=7)
        }
        try:
            user = UserCustomerModel.objects.get(openid=openid)
            serializer = UserCustomerSerializer(user, data=data, partial=True)
        except UserCustomerModel.DoesNotExist:
            data['openid'] = openid
            serializer = UserCustomerSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
    
        return Response(create_response_data(result=serializer.data))

    def put(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        try:
            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        
        serializer = UserCustomerSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result=serializer.data))


    def delete(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        try:

            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        data = {'account_status': 2}
        serializer = UserCustomerSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result='delete success'))



'''
User Master

'''
class UserMasterView(APIView):
    # login
    def post(self, request):
        if 'code' not in request.data:
            return Response(create_response_data(-1, 'code missing'))

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
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
    
        return Response(create_response_data(result=serializer.data))

    def put(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        serializer = UserMasterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result=serializer.data))

    def delete(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        data = { 'account_status': 3}
        serializer = UserMasterSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result='delete success'))




'''
Repair Order

'''
class RepairOrderOfCustomerView(APIView):
    def get(self, request, pk=None):
        if 'token' not in request.query_params:
            return Response(create_response_data(-1, 'token missing'))
        try:
            user = UserCustomerModel.objects.get(access_token=request.query_params.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        queryset = RepairOrderModel.objects.filter(sponsor=user)
        if 'status' in request.query_params:
            queryset = queryset.filter(order_status=int(request.query_params.get('status')))
        if 'recent_date' in request.query_params:
            recent_date = request.query_params.get('recent_date')
            recent_date_value = timezone.now()
            if recent_date == 'last 3 days':
                recent_date_value = recent_date_value - timedelta(days=3)
            elif recent_date == 'last a week':
                recent_date_value = recent_date_value - timedelta(days=7)
            elif recent_date == 'last a month':
                recent_date_value = recent_date_value - timedelta(days=30)
            else:
                recent_date_value = recent_date_value - timedelta(days=90)
            queryset = queryset.filter(create_time__gte=recent_date_value)

        if 'search_keyword' in request.query_params:
            search_keyword = request.query_params.get('search_keyword', '').strip()
            search_conditions = Q(order_number__icontains=search_keyword)
            search_conditions |= Q(issue_description__icontains=search_keyword)
            search_conditions |= Q(comment__icontains=search_keyword)
            queryset = queryset.filter(search_conditions)

        queryset = queryset.order_by('-create_time')

        paginator = CustomPagination()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound as e:
            return Response(create_response_data(-1, e.detail))
        serializer = RepairOrderSerializer(page, many=True)
        result = paginator.get_paginated_result(serializer.data)
        return Response(create_response_data(result=result))

    def post(self, request):
        print(request.data)
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        try:
            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

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
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result=serializer.data))
            

    def delete(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        if 'order_number' not in request.data:
            return Response(create_response_data(-1, 'order number missing'))
        
        try:
            user = UserCustomerModel.objects.get(access_token=request.data.get('token'))
            order = RepairOrderModel.objects.get(sponsor=user, order_number=request.data.get('order_number'))
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        except RepairOrderModel.DoesNotExist:
            return Response(create_response_data(-1, 'order not found'))
            
        serializer = RepairOrderSerializer(order, data={'order_status': 2}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result='delete success'))



class RepairOrderOfMasterView(APIView):
    def get(self, request):
        return


    def put(self, request):
        if 'token' not in request.data:
            return Response(create_response_data(-1, 'token missing'))
        if 'order_number' not in request.data:
            return Response(create_response_data(-1, 'order number missing'))

        try:
            user = UserMasterModel.objects.get(access_token=request.data.get('token'))
            order = RepairOrderModel.objects.get(order_number=request.data.get('order_number'))
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        except RepairOrderModel.DoesNotExist:
            return Response(create_response_data(-1, 'order not found'))

        data = {
            'assignee': user.id,
            'order_status': request.data.get('order_status', 30)
        }
        if 'transaction_amount' in request.data:
            data['transaction_amount'] = request.data.get('transaction_amount')
            if 'transaction_type' not in request.data:
                return Response(create_response_data(-1, 'transaction_type missing'))
            data['transaction_type'] = request.data.get('transaction_type')
            data['order_status'] = 50
        serializer = RepairOrderSerializer(order, data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
            
        return Response(create_response_data(result=serializer.data))



    




