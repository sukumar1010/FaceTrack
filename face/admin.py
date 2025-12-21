from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Attendance,FaceProfile


@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    model = Users

    list_display = ("email", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {
            "fields": ("is_staff", "is_active", "groups", "user_permissions")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    # 🔑 FIX: SAFE DELETE (single delete)
    def delete_model(self, request, obj):
        obj.attendances.all().delete()

        if hasattr(obj, "face_profile"):
            obj.face_profile.delete()

        obj.delete()

    # 🔑 FIX: SAFE DELETE (bulk delete)
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.attendances.all().delete()
            if hasattr(obj, "face_profile"):
                obj.face_profile.delete()
            obj.delete()


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date_time", "is_present")

@admin.register(FaceProfile)
class FaceProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
