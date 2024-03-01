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

from .models import User, ConsultationRequest, ChatMessage, Appointment
from .serializers import CreateUserSerializer, ConsultationRequestSerializer, ChatMessageSerializer, AppointmentSerializer

import json
from django.views import View
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [IsAuthenticated]  # ต้อง login เพื่อเข้าถึง API

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


class ChatViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get(self, request, *args, **kwargs):
        # ดึงหมายเลขห้องที่เกี่ยวข้องกับรายการคำขอที่เราเลือก
        consultation_request_id = kwargs.get('consultation_request_id')
        consultation_request = get_object_or_404(ConsultationRequest, id=consultation_request_id)
        
        # กรองข้อความตามหมายเลขห้อง
        chats = self.queryset.filter(room=consultation_request.id)
        
        serializer = self.serializer_class(chats, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    

class AppointmentListCreate(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
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

@csrf_exempt
def update_request_status(request, id):
    if request.method == 'PUT':
        try:
            # อ่านข้อมูลจาก Request Body
            data = json.loads(request.body)
            new_status = data.get('new_status', None)

            if new_status is None:
                return JsonResponse({'error': 'Missing new_status field'}, status=400)

            # ค้นหาคำขอโดยใช้ id
            consultation_request = ConsultationRequest.objects.get(id=id)

            # อัปเดตสถานะของคำขอ
            consultation_request.status = new_status
            consultation_request.save()

            return JsonResponse({'success': True, 'message': 'Status updated successfully'}, status=200)
        except ConsultationRequest.DoesNotExist:
            return JsonResponse({'error': 'Consultation request does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_completed_requests(request):
    # ค้นหารายการที่มีสถานะเป็น "เสร็จสิ้น"
    completed_requests = ConsultationRequest.objects.filter(status="Completed")

    # สร้างรายการข้อมูลที่จะส่งกลับในรูปแบบ JSON
    data = [{'id': request.id, 'user': request.user.full_name, 'topic_id': request.topic_id, 'topic_section': request.topic_section, 'submission_date': request.submission_date, 'received_date': request.received_date, 'status': request.status, 'details': request.details} for request in completed_requests]

    # ส่งข้อมูลกลับในรูปแบบ JSON
    return JsonResponse(data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])        
def user_consultation_requests(request):
    consultation_requests = ConsultationRequest.objects.filter(user=request.user)
    serializer = ConsultationRequestSerializer(consultation_requests, many=True)
    # สร้างและบันทึกข้อมูล CompletedConsultation
    # for consultation_request in consultation_requests:
    #     CompletedConsultation.objects.create(
    #         user=request.user,
    #         consultation_request=consultation_request,
    #         # สามารถเพิ่มข้อมูลเพิ่มเติมจาก consultation_request ได้ตามต้องการ
    #     )

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
    data = [{'id': request.id, 'user': request.user.full_name, 'topic_id': request.topic_id, 'topic_section': request.topic_section, 'submission_date': request.submission_date, 'received_date': request.received_date, 'status': request.status, 'details':request.details, 'appointment_date' : request.appointment_date} for request in requests]
    return JsonResponse(data, safe=False)

def get_all_requests_detail(request, request_id):
    request = get_object_or_404(ConsultationRequest, id=request_id)
    
    data = {
        'id': request.id,
        'user': request.user.full_name,
        'user_id':request.user.id,
        'topic_id': request.topic_id,
        'topic_section': request.topic_section,
        'submission_date': request.submission_date,
        'received_date': request.received_date,
        'status': request.status,
        'details': request.details,
        'appointment_date' : request.appointment_date,
    }
    

    # คืนค่าข้อมูลเป็น JSON
    return JsonResponse(data)

# check admin
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_admin(request):
    user = request.user
    if user.is_superuser:
        return Response({'is_admin': True})
    else:
        return Response({'is_admin': False})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_appointments(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_appointments(request, appointment_id):
    user = request.user
    appointments = Appointment.objects.filter(consultation_request_id=appointment_id)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_card(request, user_card_id):
    try:
        user_card = get_object_or_404(ConsultationRequest, id=user_card_id)
        user_card_data = {
            'id': user_card.id,
            'topic_id': user_card.topic_id,
            # เพิ่มข้อมูลอื่น ๆ ตามต้องการ
        }
        return JsonResponse(user_card_data)
    except ConsultationRequest.DoesNotExist:
        return JsonResponse({'error': 'User card not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@receiver(post_save, sender=Appointment)
def update_consultation_request(sender, instance, **kwargs):
    if instance.appointment_date:
        consultation_request = ConsultationRequest.objects.get(id=instance.consultation_request_id)
        consultation_request.appointment_date = instance.appointment_date
        consultation_request.save()