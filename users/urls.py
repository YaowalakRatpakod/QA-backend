from django.urls import path
# from .views import get_user
from .views import ConsultationRequestCreateView
from .views import FullnameDropdownView
from .views import ConsultationRequestListView
# from .views import dropdown_data

urlpatterns = [
    #  path('v1/auth/user/', get_user, name='get_user'),
     path('v1/consultation-request/create/', ConsultationRequestCreateView.as_view(), name='consultation-request-create'),
     path('v1/fullname-dropdown/', FullnameDropdownView.as_view(), name='fullname-dropdown'),
     path('consultation-request/list/', ConsultationRequestListView.as_view(), name='consultation_request_list'),
    #  path('dropdown/', dropdown_data, name='dropdown_data'),


    # เพิ่ม URL pattern อื่น ๆ ตามที่ต้องการ
]
