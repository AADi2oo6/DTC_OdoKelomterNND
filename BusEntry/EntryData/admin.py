from django.contrib import admin
from import_export.admin import ExportMixin  # ✅ import this
from .models import CustomUser, Bus_Data

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id')
    search_fields = ('user_id', 'name')
    ordering = ('user_id',)

@admin.register(Bus_Data)
class BusDataAdmin(ExportMixin, admin.ModelAdmin):  # ✅ add ExportMixin
    list_display = ("id",'date', 'shift', 'bus_no', 'out_kms', 'in_kms', 'diff', 'soc', 'soc_in', 'time_of_submission',"IN_Time",'user_name')
    search_fields = ('bus_no', 'shift',"user_name")
    list_filter = ('date', 'shift', 'bus_no',"user_name")
