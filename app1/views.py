from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import RepairForm, UserProfile
from .serializers import RepairFormSerializer, UserProfileSerializer
from django.db.models import Q

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        form = serializer.save()
        
        return Response({
            'message': 'user created successfully',
            'form': UserProfileSerializer(form).data
        }, status=status.HTTP_201_CREATED)    

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 30    

class RepairFormViewSet(viewsets.ModelViewSet):
    queryset = RepairForm.objects.all()
    serializer_class = RepairFormSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = RepairForm.objects.all()
        
        search = self.request.query_params.get('search', '')
        order_status = self.request.query_params.get('order_status', '')
        ordering = self.request.query_params.get('ordering', '-created_at')
        
        if search:
            queryset = queryset.filter(
                Q(sponsor__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search) |
                Q(receiver__icontains=search)
            )
        
        if order_status:
            status_list = [s.strip() for s in order_status.split(',') if s.strip()]
            if status_list:
                queryset = queryset.filter(order_status__in=status_list)
        
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        form = get_object_or_404(RepairForm, pk=pk)
        form.delete()
        
        return Response({
            'message': 'form deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        form = serializer.save()
        
        return Response({
            'message': 'form created successfully',
            'results': RepairFormSerializer(form).data
        }, status=status.HTTP_201_CREATED)    

    @action(detail=False, methods=['get'], url_path='by-id')
    def get_by_id(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({
                'error': '参数缺失：必须提供id参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        forms = RepairForm.objects.filter(id=id)
        if not forms.exists():
            return Response({
                'message': f'未找到orderid为"{id}"的维修单',
                'count': 0,
                'results': []
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(forms, many=True)
        return Response({
            'message': f'找到 {forms.count()} 条记录',
            'count': forms.count(),
            'results': serializer.data
        })

