from django.contrib import admin
from .models import Sequence,Subject,User,Experiment,Trial,Block, Keypress

# Register your models here.
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Sequence, admin.ModelAdmin)
admin.site.register(Experiment, admin.ModelAdmin)
admin.site.register(Trial, admin.ModelAdmin)
admin.site.register(Block, admin.ModelAdmin)
admin.site.register(Subject, admin.ModelAdmin)
admin.site.register(Keypress, admin.ModelAdmin)

