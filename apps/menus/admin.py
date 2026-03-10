from django.contrib import admin

from apps.menus.models import Menu, MenuCategory


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "is_available")
    list_filter = ("is_available", "restaurant")
    search_fields = ("name", "description")


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "menu", "is_available", "created_at")
    list_filter = ("is_available", "menu")
    search_fields = ("name", "description")
