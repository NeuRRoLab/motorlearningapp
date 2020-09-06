from django.contrib import admin
from .models import Sequence,Subject,Designer,Experiment,Trial,Block

# Register your models here.
admin.site.register(Sequence, admin.ModelAdmin)
admin.site.register(Experiment, admin.ModelAdmin)
admin.site.register(Designer, admin.ModelAdmin)
admin.site.register(Trial, admin.ModelAdmin)
admin.site.register(Block, admin.ModelAdmin)
admin.site.register(Subject, admin.ModelAdmin)

