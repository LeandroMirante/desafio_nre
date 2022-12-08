from django.contrib import admin
from django.db.models import Q
from .models import Customer, Company

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "is_staff", "is_active", "city", "district", "address")
    list_filter = ("email", "is_staff", "is_active", "city", "district", "address")
    fieldsets = (
        (
            None,
            {"fields": ("email", "name", "password", "city", "district", "address")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_active",
                    "city",
                    "district",
                    "address",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class CompanyAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "is_active", "city", "district", "address")
    list_filter = ("email", "is_active", "city", "district", "address")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "address",
                    "city",
                    "district",
                    "email",
                    "cnpj",
                    "is_active",
                    "password",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "address",
                    "city",
                    "district",
                    "email",
                    "cnpj",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(email=request.user)


class CustomerAdmin(BaseUserAdmin):
    model = User
    list_display = (
        "email",
        "is_active",
        "city",
        "district",
        "address",
        "company_name",
        "documents",
    )
    list_filter = ("email", "is_active", "city", "district", "address", "company_name")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "cpf",
                    "email",
                    "is_active",
                    "company_name",
                    "documents",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "cpf",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "company_name",
                    "documents",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(company_name=request.user) | Q(id=request.user.id))

        # list_display = ('id', 'name', 'embed_pdf')


admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Company, CompanyAdmin)
