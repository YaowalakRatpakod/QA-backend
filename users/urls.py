from django.urls import path
from .views import ConsultationRequestCreateView
from .views import CancelRequestView
from .views import user_consultation_requests, user_consultation_requests_id, get_all_requests, get_all_requests_detail,update_request_status
from .views import check_admin,get_completed_requests
from .views import ChatViews
from .views import AppointmentListCreate, CancelAppointmentView
from .views import get_user_card, get_user_appointments,get_user_completed_requests, get_user_info
from .views import update_user_tel

urlpatterns = [
    path('v1/consultation-request/create/', ConsultationRequestCreateView.as_view(), name='consultation-request-create'),
    path('v1/fullname-dropdown/', get_user_info),
    path('user-consultation-requests/', user_consultation_requests),
    path('user-consultation-requests/<int:id>/updates', update_request_status),
    path('user-consultation-requests/<int:id>/', user_consultation_requests_id),
    path('user-consultation-requests-user-all/', get_user_completed_requests),
    path('cancel-request/<int:pk>/', CancelRequestView.as_view(), name='cancel-request'),
    path('user-consultation-requests-all/', get_all_requests),
    path('user-consultation-requests-all/<int:request_id>/', get_all_requests_detail),
    path('user-consultation-requests-all/success/', get_completed_requests),
    path('user-card/<int:user_card_id>/', get_user_card),
    path('update-user-tel/', update_user_tel),
    path('appointments/<int:consultation_request_id>/cancel/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    # URL pattern สำหรับการส่งข้อความ (POST)
    path('send-messages/', ChatViews.as_view(), name='send_message'),
    path('consultation-requests/<int:consultation_request_id>/chats/', ChatViews.as_view(), name='consultation-request-chats'),
    path('check-admin/', check_admin, name='check_admin'),
    path('appointments/', AppointmentListCreate.as_view(), name='appointment-list-create'),
    path('appointments/<int:appointment_id>/', get_user_appointments, name='get_appointment_detail'),
    # เพิ่ม URL pattern อื่น ๆ ตามที่ต้องการ
]
