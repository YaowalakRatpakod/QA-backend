# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed

from .models import User
from .models import ConsultationRequest
from .serializers import CreateUserSerializer
from .serializers import ConsultationRequestSerializer
from .serializers import UserSerializer

import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [IsAuthenticated]  # ต้อง login เพื่อเข้าถึง API

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def get_object(self):
        return self.request.user
    

# ค่า Fullname แบบ dropdown ไม่จำเป็น
class FullnameDropdownView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.values('full_name')
        # serializers = UserSerializer(users, many=True)
        return JsonResponse(list(users), safe=False)


class ConsultationRequestCreateView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []

    def get_serializer_class(self):
        return ConsultationRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = ConsultationRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#API ENDPOINT ของการ์ดคำถาม
class ConsultationRequestListView(View):
    def get(self,request):
        data = ConsultationRequest.objects.values()
        return JsonResponse({'data':list(data)}, safe=False)
    

#API_ENDPOINT -V'DKI lOGIN
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Login successful'})
        else:
            return JsonResponse({'success': False, 'message': 'Login failed'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def user_data(request):
    if request.method == 'GET':
        user = request.user
        return JsonResponse({'full_name': user.full_name, 'tel': user.tel, 'email': user.email})
    else:
        return HttpResponseNotAllowed(['GET'])