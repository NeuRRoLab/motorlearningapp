from django.contrib import admin
from .models import Subject, User, Experiment, Trial, Block, Keypress

# Register your models here.
from django.contrib.auth.admin import UserAdmin

# This allows creating objects in the admin view of Django (/admin)

admin.site.register(User, UserAdmin)
admin.site.register(Experiment, admin.ModelAdmin)
admin.site.register(Trial, admin.ModelAdmin)
admin.site.register(Block, admin.ModelAdmin)
admin.site.register(Subject, admin.ModelAdmin)
admin.site.register(Keypress, admin.ModelAdmin)

