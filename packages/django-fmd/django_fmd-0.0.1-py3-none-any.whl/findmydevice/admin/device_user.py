from django.contrib import admin

from findmydevice.models import DeviceUser


@admin.register(DeviceUser)
class DeviceUserModelAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'create_dt', 'update_dt')
    date_hierarchy = 'create_dt'
