from django.contrib import admin
from .models import Room,Message,CustomUser,Profile
# Register your models here.
admin.site.register(Room)
admin.site.register(Message)

admin.site.register(CustomUser)
admin.site.register(Profile)