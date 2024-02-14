from django.urls import path
from .views import ConsultationRequestCreateView
from .views import FullnameDropdownView
from .views import user_consultation_requests, user_consultation_requests_id, get_all_requests, get_all_requests_detail
from .views import CompletedConsultationListAPIView

from .views import ChatViews

urlpatterns = [
    path('v1/consultation-request/create/', ConsultationRequestCreateView.as_view(), name='consultation-request-create'),
    path('v1/fullname-dropdown/', FullnameDropdownView.as_view(), name='fullname-dropdown'),
    path('user-consultation-requests/', user_consultation_requests),
    path('user-consultation-requests/<int:id>/', user_consultation_requests_id),
    path('user-consultation-requests-all/', get_all_requests),
    path('user-consultation-requests-all/<int:request_id>/', get_all_requests_detail),
    path('user-consultation-completed/', CompletedConsultationListAPIView.as_view()),
    # URL pattern สำหรับการส่งข้อความ (POST)
    path('send-messages/', ChatViews.as_view(), name='send_message'),
    # URL pattern สำหรับการรับข้อความ (GET)
    # path('get-messages/<int:sender_id>/<int:receiver_id>/', get_messages, name='get_messages'),

    # เพิ่ม URL pattern อื่น ๆ ตามที่ต้องการ
]
