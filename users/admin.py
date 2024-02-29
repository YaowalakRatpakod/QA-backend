from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .form import CustomUserChangeForm, CustomUserCreationForm
from .models import User, ConsultationRequest, ChatMessage
# Register your models here. ใช้สำหรับจัดการผู้ใช้


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    ordering = ['email']
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['full_name', 'tel', 'email', 'is_staff']  # 'is_activate'
    list_display_links = ['email']
    list_filter = ['full_name', 'tel', 'email', 'is_staff']  # 'is_activate'
    search_fields = ['full_name', 'tel', 'email']

    fieldsets = (
        (
            _("Login Credentials"), {
                "fields": ("email", "password",)
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": ('full_name',)
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions",)
            },
        ),
        (
            _("Important Dates"),
            {
                "fields": ("last_login", )
            },
        ),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", 'full_name', "password1", "password2", "is_staff", "is_active",)
        },),
    )

class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['user','topic_id','topic_section', 'submission_date', 'status']
    list_filter = ['user','topic_id','topic_section','submission_date','status']
    search_fields = ['topic_id']

class ChatMessageAdmin(admin.ModelAdmin):
    list_editable = ['is_read']
    list_display = ["sender","receiver","message","is_read"]

admin.site.register(User, UserAdmin)
admin.site.register(ConsultationRequest, ConsultationRequestAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
