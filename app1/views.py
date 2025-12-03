from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from .models import RepairForm
from .serializers import RepairFormSerializer

class RepairFormViewSet(viewsets.ModelViewSet):
    serializer_class = RepairFormSerializer

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
            'form': RepairFormSerializer(form).data
        }, status=status.HTTP_201_CREATED)    

    @action(detail=False, methods=['get'], url_path='by-sponsor')
    def get_by_sponsor(self, request):
        sponsor = request.query_params.get('sponsor')
        if not sponsor:
            return Response({
                'error': '参数缺失：必须提供sponsor参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        forms = RepairForm.objects.filter(sponsor=sponsor)
        if not forms.exists():
            return Response({
                'message': f'未找到发起人为"{sponsor}"的维修单',
                'count': 0,
                'results': []
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(forms, many=True)
        return Response({
            'message': f'找到 {forms.count()} 条记录',
            'count': forms.count(),
            'results': serializer.data
        })

