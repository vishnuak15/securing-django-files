from django.contrib import admin

from api.models import Booking, Package, PackagePermission

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'email_address')

class PackagePermissionInline(admin.TabularInline):
    model = PackagePermission

class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'rating', 'tour_length', 'start')
    inlines = (PackagePermissionInline,)

admin.site.register(Booking, BookingAdmin)
admin.site.register(Package, PackageAdmin)
