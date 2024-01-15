#ใช้ในการกำหนดค่าและการตั้งค่าของแอปพลิเคชัน "users"
from django.apps import AppConfig




class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    #ทดสอบการเชื่อม dropdown
    def ready(self):
        import users.models #นำเข้าsignal
