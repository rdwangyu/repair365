from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def destroy(self, request, pk=None, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        
        return Response({
            'message': 'user deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'user created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)    
