from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django import forms

from .models import User, ConsultationRequest, ChatMessage

User = get_user_model()

class CreateUserSerializer(UserCreateSerializer):
    major = serializers.ChoiceField(choices=User.MAJORS.items())

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'full_name', 'password', 'major']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        major = validated_data.pop('major', None)  # ดึงค่า major ออกจาก validated_data
        user = super().create(validated_data)  # สร้าง User จากข้อมูลที่ตรวจสอบแล้ว
        if major:
            user.major = major  # กำหนดค่า major ให้กับ User
            user.save()  # บันทึกข้อมูล
        return user



class UserSerializer(serializers.ModelSerializer):
    major = serializers.CharField(source='get_user_major', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'full_name']

# สร้างคำขอปรึกษา
class ConsultationRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # เพิ่ม UserSerializer เข้าไป

    class Meta:
        model = ConsultationRequest
        fields = '__all__'

    def create(self, validated_data):
    # ลองดึงข้อมูล user จาก validated_data
        user_data = validated_data.get('user', None)
        
        # ตรวจสอบว่า 'status' มีอยู่ใน validated_data หรือไม่
        if 'status' in validated_data:
            status_data = validated_data['status']
        else:
            # ถ้าไม่มีให้ใช้ค่า default หรือให้เกิดข้อผิดพลาดขึ้นอยู่กับการออกแบบของระบบ
            status_data = None
            
        # ตรวจสอบว่ามีข้อมูล user หรือไม่
        if user_data:
            # หา instance ของ User จากข้อมูลที่ดึงมา
            user_instance = self.context['request'].user
            serializer = ConsultationRequestSerializer(data=validated_data, context=self.context)
            # user_instance = User.objects.get(full_name=user_data['full_name'])
            # ใช้ instance ของ User ในการสร้าง ConsultationRequest
            consultation_request = ConsultationRequest.objects.create(
                
                user=self.context['request'].user,
                topic_id=validated_data['topic_id'],
                topic_section=validated_data['topic_section'],
                submission_date=validated_data['submission_date'],
                details=validated_data['details'],
                document=validated_data.get('document', None),
                status=status_data,
                major=user_instance.major
                )
            return consultation_request
        else:
            # ถ้าไม่มีข้อมูล user ให้ทำการ raise exception หรือทำอย่างไรตามที่เหมาะสม
            raise serializers.ValidationError("User data is missing in the request.")

# แชท
class ChatMessageSerializer(serializers.ModelSerializer):
    sender_user = UserSerializer(source='sender', read_only=True)
    receiver_user = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id','sender', 'receiver','sender_user', 'receiver_user', 'message', 'is_read', 'timestamp','room']

    def reply_to_comment(self, instance, validated_data):
        sender = self.context['request'].user
        room = validated_data['room']
        return ChatMessage.objects.create(sender=sender, room=room, **validated_data)
    
# รายการที่เสร็จสิ้น
# class CompletedConsultationSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = CompletedConsultation
#         fields = '__all__'