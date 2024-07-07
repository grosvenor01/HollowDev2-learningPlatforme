from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(profile)
admin.site.register(course)
admin.site.register(course_enrolled)
admin.site.register(quize)
admin.site.register(lesson)