from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import RepairOrder, UserProfile
from .serializers import RepairOrderSerializer, UserProfileSerializer
from django.db.models import Q
from django.conf import settings
import requests

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        appid = settings.WECHAT_CONFIG['APPID']
        secret = settings.WECHAT_CONFIG['SECRET']
        params = {
            'appid': appid,
            'secret': secret,
            'js_code': request.data['openid'],
            'grant_type': 'authorization_code'
        }
        wechat_api_url = 'https://api.weixin.qq.com/sns/jscode2session'
        response = requests.get(wechat_api_url, params=params, timeout=10)
        result = response.json()
        print('result', result)
        if 'errcode' in result and result['errcode'] != 0:
            return Response({
                'message': f'微信接口错误: {result.get("errmsg", "未知错误")}',
                'error_code': result.get('errcode')
            }, status.HTTP_400_BAD_REQUEST)

        openid = result['openid']
        existing_user = UserProfile.objects.filter(openid=openid).first()
        if existing_user:
            return Response({
                'message': '用户已存在',
                'results': UserProfileSerializer(existing_user).data,
                'success': True
            }, status=status.HTTP_200_OK)

        data = request.data;
        data['openid'] = result['openid']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        form = serializer.save()
        
        return Response({
            'message': 'user created successfully',
            'results': UserProfileSerializer(form).data
        }, status=status.HTTP_201_CREATED)    

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 30    

class RepairOrderViewSet(viewsets.ModelViewSet):
    serializer_class = RepairOrderSerializer
    pagination_class = StandardResultsSetPagination
    queryset = RepairOrder.objects.all()    

    def get_queryset(self):
        search = self.request.query_params.get('search', '')
        orderStatus = self.request.query_params.get('orderStatus', '')
        ordering = self.request.query_params.get('ordering', '-created_at')

        if search:
            queryset = self.queryset.filter(
                Q(sponsor__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search) |
                Q(receiver__icontains=search)
            )
        
        if orderStatus:
            statusList = [s.strip() for s in orderStatus.split(',') if s.strip()]
            if statusList:
                queryset = self.queryset.filter(order_status__in=statusList)
        
        if ordering:
            queryset = self.queryset.order_by(ordering)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'ok',
            'results': serializer.data
        })

    def retrieve(self, request, pk=None):
        order = get_object_or_404(self.queryset, pk=pk)
        return Response(
            {
                'message': 'ok',
                'results': RepairOrderSerializer(order).data
            }
        )

    def create(self, request, *args, **kwargs):
        userOpenId = request.data.get("userOpenId")
        if not userOpenId:
            return Response(
                {'message': 'missing userOpenId'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = UserProfile.objects.get(openid=userOpenId)
        except UserProfile.DoesNotExist:
            return Response(
                {'message': 'user not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_created = serializer.save(sponsor=user)
        return Response(
            {
                'message': 'ok',
                'results': RepairOrderSerializer(order_created).data
            },
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'message': '用户信息更新成功',
                'results': serializer.data
            })
            
        except Exception as e:
            return Response({
                'message': f'更新失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
