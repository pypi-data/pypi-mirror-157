from django.contrib import admin

from findmydevice.models import Location


@admin.register(Location)
class LocationModelAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'create_dt', 'update_dt')
    date_hierarchy = 'create_dt'
    list_filter = ('device_user',)
