from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from datetime import timedelta
from django.core.files.storage import default_storage
import requests
import json
from .models import *
from .serializers import *
from rest_framework import status
import random
from django.db.models import Q
import os
import uuid
from django.conf import settings


def create_response_data(errcode = 0, errmsg = '', result = {}):
    return {'errcode': errcode, 'errmsg': errmsg, 'result': result}

def parse_http_headers(request):
    if 'Authorization' not in request.headers:
        return create_response_data(-1, 'token missing')
    auth = request.headers.get('Authorization')
    parts = auth.split(' ')
    if len(parts) != 2:
        return create_response_data(-1, 'token format error')
    schema, token = parts
    return create_response_data(result=token)
        

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
    def get(self, request):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        serializer = UserCustomerSerializer(user)
        return Response(create_response_data(result=serializer.data))
        
        
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
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        
        serializer = UserCustomerSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result=serializer.data))


    def delete(self, request):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
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
    def get(self, request):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserMasterModel.objects.get(access_token=parse_response['result'])
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        serializer = UserMasterSerializer(user)
        return Response(create_response_data(result=serializer.data))

    # login
    def post(self, request):
        if 'code' not in request.data:
            return Response(create_response_data(-1, 'code missing'))
        auto_reg = request.data.get('auto_reg', False)

        login_response = login_wechat(request.data.get('code'))
        if login_response['errcode'] != 0:
            return Response(create_response_data(-1, f"failed to login({login_response['errcode']}'): {login_response['errmsg']}"))

        openid = login_response['result']['openid']
        data = {
            'access_token': login_response['result']['session_key'],
            'token_expired': timezone.now() + timedelta(days=7),
        }
        try:
            user = UserMasterModel.objects.get(openid=openid)
            serializer = UserMasterSerializer(user, data=data, partial=True)
        except UserMasterModel.DoesNotExist:
            if not auto_reg:
                return Response(create_response_data(-1, 'user not found'))

            data = {
                'openid': openid,
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
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))
        
        try:
            user = UserMasterModel.objects.get(access_token=parse_response['result'])
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        serializer = UserMasterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result=serializer.data))

    def delete(self, request):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserMasterModel.objects.get(access_token=parse_response['result'])
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        data = { 'account_status': 3 }
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
    def __detail(self, user, pk):
        try:
            order = RepairOrderModel.objects.get(sponsor=user, pk=pk)
        except RepairOrderModel.DoesNotExist:
            return create_response_data(-1, 'order not found: ' + str(pk))
        serializer = RepairOrderSerializer(order)
        return create_response_data(result=serializer.data)

    def __list(self, user, request):
        params = request.query_params
        queryset = RepairOrderModel.objects.filter(sponsor=user)
        if 'status' in params:
            queryset = queryset.filter(order_status=int(params.get('status')))
        if 'recent_date' in params:
            recent_date = params.get('recent_date')
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

        if 'search_keyword' in params:
            search_keyword = params.get('search_keyword', '').strip()
            search_conditions = Q(order_number__icontains=search_keyword)
            search_conditions |= Q(issue_description__icontains=search_keyword)
            search_conditions |= Q(comment__icontains=search_keyword)
            queryset = queryset.filter(search_conditions)

        queryset = queryset.order_by('-create_time')

        paginator = CustomPagination()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound as e:
            return create_response_data(-1, e.detail)
        serializer = RepairOrderSerializer(page, many=True)
        result = paginator.get_paginated_result(serializer.data)
        return create_response_data(result=result)
        
    def get(self, request, pk=None):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        if pk:
            response = self.__detail(user, pk)
        else:
            response = self.__list(user, request)

        if response['errcode'] != 0:
            return Response(create_response_data(-1, response['errmsg']))
        else:
            return Response(create_response_data(result=response['result']))

    def post(self, request):
        print(request.data)
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))
        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
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

        user_data = {}
        if user.phone == '':
            user_data['phone'] = serializer.data.get('contact_phone')
        if user.address == '':
            user_data['address'] = serializer.data.get('location')

        if user_data:
            user_serializer = UserCustomerSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                print('failed to update user profile: ', user_serializer.errors)
        
        return Response(create_response_data(result=serializer.data))
            

    def delete(self, request, pk):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserCustomerModel.objects.get(access_token=parse_response['result'])
            order = RepairOrderModel.objects.get(sponsor=user, pk=pk)
        except UserCustomerModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))
        except RepairOrderModel.DoesNotExist:
            return Response(create_response_data(-1, 'order not found'))
            
        serializer = RepairOrderSerializer(order, data={'order_status': 1}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(create_response_data(-1, json.dumps(serializer.errors)))
        
        return Response(create_response_data(result='delete success'))



class RepairOrderOfMasterView(APIView):
    def __detail(self, user, pk):
        try:
            order = RepairOrderModel.objects.get(pk=pk)
        except RepairOrderModel.DoesNotExist:
            return create_response_data(-1, 'order not found: ' + str(pk))
        serializer = RepairOrderSerializer(order)
        return create_response_data(result=serializer.data)

    def __list(self, user, request):
        params = request.query_params
        show_range = [20, 30, 31, 40, 50, 51, 60, 61]
        queryset = RepairOrderModel.objects.filter(
            Q(assignee=user) | Q(assignee__isnull=True),
            order_status__in=show_range)
        if 'status' in params:
            queryset = queryset.filter(order_status=int(params.get('status')))
        if 'recent_date' in params:
            recent_date = params.get('recent_date')
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

        if 'search_keyword' in params:
            search_keyword = params.get('search_keyword', '').strip()
            search_conditions = Q(order_number__icontains=search_keyword)
            search_conditions |= Q(issue_description__icontains=search_keyword)
            search_conditions |= Q(comment__icontains=search_keyword)
            queryset = queryset.filter(search_conditions)

        queryset = queryset.order_by('-create_time')
        paginator = CustomPagination()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound as e:
            return create_response_data(-1, e.detail)
        serializer = RepairOrderSerializer(page, many=True)
        result = paginator.get_paginated_result(serializer.data)
        return create_response_data(result=result)
        
    def get(self, request, pk=None):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserMasterModel.objects.get(access_token=parse_response['result'])
        except UserMasterModel.DoesNotExist:
            return Response(create_response_data(-1, 'user not found'))

        if pk:
            response = self.__detail(user, pk)
        else:
            response = self.__list(user, request)

        if response['errcode'] != 0:
            return Response(create_response_data(-1, response['errmsg']))
        else:
            return Response(create_response_data(result=response['result']))


    def put(self, request, pk):
        parse_response = parse_http_headers(request)
        if parse_response['errcode'] != 0:
            return Response(create_response_data(-1, parse_response['errmsg']))

        try:
            user = UserMasterModel.objects.get(access_token=parse_response['result'])
            order = RepairOrderModel.objects.get(pk=pk)
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


class UploadImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(create_response_data(-1, serializer.errors))

        image = serializer.validated_data['image']
        try:
            ext = os.path.splitext(image.name)[1].lower()
            if not ext:
                ext = '.jpg'
            
            unique_id = uuid.uuid4().hex
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{unique_id}{ext}"
            
            date_path = timezone.now().strftime('%Y_%m_%d')
            storage_path = f"uploads/{date_path}/{filename}"
            saved_path = default_storage.save(storage_path, image)
            
            if settings.DEBUG:
                url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
            else:
                url = f"https://your-domain.com{settings.MEDIA_URL}{saved_path}"

            data = {
                'url': url,
                'filename': filename,
                'size': image.size
            }
            return Response(create_response_data(result=data))
        except Exception as e:
            return Response(create_response_data(-1, f'上传失败：{str(e)}'))




