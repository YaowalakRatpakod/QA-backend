from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import ConsultationRequest
from .models import User



User = get_user_model()
class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'full_name', 'password']
        is_active = serializers.BooleanField(default=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

# สร้างคำขอปรึกษา
class ConsultationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        fields = ['topic_code','topic_title','submission_date','received_date','details','document','status']