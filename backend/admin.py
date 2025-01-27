from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
        CustomUser, PhysicalBook, ElectronicBook, Author, 
        CategoryForElectronicBooks, BorrowingRecord, Review, 
        LibrarySettings, CategoryForPhysicalBoosk, DownloadLog
    )

@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ebook', 'download_date', 'ip_address')
    search_fields = ('user__username', 'ebook__title', 'ip_address')
    list_filter = ('download_date',)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'full_name', 'is_admin', 'is_active']
    search_fields = ['username', 'full_name']

    # Добавляем поля в форму редактирования пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Персональная информация', {
            'fields': (
                'full_name',
                'date_of_birth',
                'passport_issue_date',
                'jshshir_code',
                'course',
                'group',
                'academic_year',
                'semester',
                'specialization',
                'education_type',
                'education_form',
                'is_student',
                'is_teacher',
                'is_admin',
                'profile_picture',
                'validate_url',
            ),
        }),
    )

    # Добавляем поля в форму создания нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'full_name',
                'date_of_birth',
                'passport_issue_date',
                'jshshir_code',
                'course',
                'group',
                'academic_year',
                'semester',
                'specialization',
                'education_type',
                'education_form',
                'is_student',
                'is_teacher',
                'profile_picture',
            ),
        }),
    )

# Регистрируем админ-панель

class PhysicalBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'available_copies', 'isbn', 'category', 'language', 'publisher')
    search_fields = ('title', 'author__name', 'isbn')
    list_filter = ('category', 'language', 'publication_date')
    ordering = ('-publication_date',)
    list_per_page = 20

class ElectronicBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'file')
    search_fields = ('title', 'author__name', 'category__name')
    list_filter = ('category',)
    ordering = ('-title',)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CategoryForPhysicalBooskAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CategoryForElectronicBooksAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class BorrowingRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'return_date', 'is_returned')
    search_fields = ('user__username', 'book__title')
    list_filter = ('is_returned', 'borrow_date', 'return_date')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'created_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('rating', 'created_at')

class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ('max_borrow_days',)

# Регистрация моделей в админ-панели
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PhysicalBook, PhysicalBookAdmin)
admin.site.register(ElectronicBook, ElectronicBookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(CategoryForElectronicBooks, CategoryForElectronicBooksAdmin)
admin.site.register(CategoryForPhysicalBoosk, CategoryForPhysicalBooskAdmin)
admin.site.register(BorrowingRecord, BorrowingRecordAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(LibrarySettings, LibrarySettingsAdmin)
