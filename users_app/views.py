from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response


from . import serializers as user_serializers, models as user_models
# Create your views here.



class UsersViewSet(viewsets.ModelViewSet):

    serializer_class = user_serializers.UsersSerializer
    permission_classes = [permissions.AllowAny]
    queryset = user_models.User.objects.all()

    # def get_queryset(self):
    #     return self.queryset.all()