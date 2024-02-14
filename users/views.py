# views.py
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import TokenAuthentication

from .models import User, ConsultationRequest, ChatMessage, CompletedConsultation
from .serializers import CreateUserSerializer, ConsultationRequestSerializer , CompletedConsultationSerializer, ChatMessageSerializer

import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
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
    

# ค่า Fullname แบบ dropdown ไม่จำเป็นลบได้
class FullnameDropdownView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.values('full_name')
        # serializers = UserSerializer(users, many=True)
        return JsonResponse(list(users), safe=False)


class ConsultationRequestCreateView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # ดึงข้อมูลผู้ใช้ที่ล็อกอิน
        # user = request.user
        request.data['submission_date'] = request.data.get('submission_date', None)
        #สร้าง serializer และกำหนดค่าให้กับ full_name
        serializer = ConsultationRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # ใช้ request.user เพื่อกำหนดผู้ใช้ที่สร้างคำขอ
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#API ENDPOINT ของการ์ดคำถาม
class ConsultationRequestListView(View):
    def get(self,request):
        data = ConsultationRequest.objects.values()
        return JsonResponse({'data':list(data)}, safe=False)


class CompletedConsultationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ดึงข้อมูลรายการที่เสร็จสิ้นแล้วของผู้ใช้ที่เข้าสู่ระบบ
        completed_consultations = CompletedConsultation.objects.filter(user=request.user, status='Completed')
        serializer = CompletedConsultationSerializer(completed_consultations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChatViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get(self, request, *args, **kwargs):
        chats = self.get_queryset()
        serializer = self.get_serializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk, format=None):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# @csrf_exempt
# def send_messages(request):
#     if request.method == 'POST':
#         # รับข้อมูลจากคำขอ POST
#         sender_id = request.POST.get('sender_id')
#         receiver_id = request.POST.get('receiver_id')
#         message = request.POST.get('message')

#         # ดึงข้อมูลผู้ส่งและผู้รับ
#         sender = get_object_or_404(User, id=sender_id)
#         receiver = get_object_or_404(User, id=receiver_id)

#         # สร้างข้อความแชทและบันทึกลงในฐานข้อมูล
#         chat_message = ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
#         return JsonResponse({'status': 'success'})
#     else:
#         # ถ้าไม่ใช่คำขอ POST ให้ส่งข้อความข้อผิดพลาดกลับ
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
# def get_messages(request, sender_id, receiver_id):
#     # ดึงข้อมูลผู้ส่งและผู้รับ
#     sender = get_object_or_404(User, id=sender_id)
#     receiver = get_object_or_404(User, id=receiver_id)

#     # ค้นหาข้อความแชทระหว่างผู้ส่งและผู้รับ และเรียงลำดับตามเวลา
#     messages = ChatMessage.objects.filter(sender=sender, receiver=receiver).order_by('timestamp')
    
#     # สร้างข้อมูลข้อความที่จะส่งกลับไปให้ React
#     message_data = [{'sender': msg.sender.full_name, 'message': msg.message, 'timestamp': msg.timestamp} for msg in messages]
    
#     # ส่งข้อมูลข้อความกลับเป็น JSON
#     return JsonResponse({'messages': message_data})



#API ENDPOINT ของสถิติ
# def statistics_view(request):
#     #ดึงข้อมูลสถิติ
#     completed_count = CompletedConsultation.objects.count()

#     # ส่งข้อมูลสถิติกลับเป็น JSON
#     data = {
#         'completed_count': completed_count,
#     }

#     return JsonResponse(data)


#API_ENDPOINT
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
    
def user_consultation_requests(request):
    if request.user.is_authenticated:
        user = request.user
        # ดึงข้อมูลรายการขอคำปรึกษาของผู้ใช้
        consultation_requests = ConsultationRequest.objects.filter(user=user)
        return JsonResponse({'consultation_requests': list(consultation_requests)})
    else:
        return JsonResponse({'error': 'User is not authenticated'})
    
#test ตัว create ของรายการใหม่อีกรอบ
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_consultation_request(request):
    # สร้าง instance ใหม่ของ serializer ด้วยข้อมูลจาก request.data
    serializer = ConsultationRequestSerializer(data=request.data)
    if serializer.is_valid():
        # ใช้ save() เพื่อสร้าง instance ใหม่ของ ConsultationRequest
        # โดยกำหนดผู้ใช้ (user) โดยใช้ request.user
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])        
def user_consultation_requests(request):
    consultation_requests = ConsultationRequest.objects.filter(user=request.user)
    serializer = ConsultationRequestSerializer(consultation_requests, many=True)
    # สร้างและบันทึกข้อมูล CompletedConsultation
    for consultation_request in consultation_requests:
        CompletedConsultation.objects.create(
            user=request.user,
            consultation_request=consultation_request,
            # สามารถเพิ่มข้อมูลเพิ่มเติมจาก consultation_request ได้ตามต้องการ
        )

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def user_consultation_requests_id(request,id):
    try:
        consultation_request = ConsultationRequest.objects.get(id=id)
        # ตรวจสอบว่าผู้ใช้ที่เข้าถึงรายการคำขอเป็นเจ้าของหรือไม่
        if consultation_request.user != request.user:
            return Response({'error': 'You do not have permission to access this consultation request'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ConsultationRequestSerializer(consultation_request)
        return Response(serializer.data, status=status.HTTP_200_OK)  # แก้ไขเพิ่มเติม: เพิ่ม status ให้กับ Response
    except ConsultationRequest.DoesNotExist:
        return Response({'error': 'Consultation request does not exist'}, status=status.HTTP_404_NOT_FOUND)

# get all request
def get_all_requests(request):
    requests = ConsultationRequest.objects.all()
    data = [{'id': request.id, 'user': request.user.full_name, 'topic_id': request.topic_id, 'topic_section': request.topic_section, 'submission_date': request.submission_date, 'received_date': request.received_date, 'status': request.status} for request in requests]
    return JsonResponse(data, safe=False)

def get_all_requests_detail(request, request_id):
    request = get_object_or_404(ConsultationRequest, id=request_id)
    
    data = {
        'id': request.id,
        'user': request.user.full_name,
        'topic_id': request.topic_id,
        'topic_section': request.topic_section,
        'submission_date': request.submission_date,
        'received_date': request.received_date,
        'status': request.status
    }
    
    return JsonResponse(data)