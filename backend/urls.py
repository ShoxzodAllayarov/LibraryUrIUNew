from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from . import views  # Ваши собственные представления

urlpatterns = [
    # Стандартные страницы аутентификации
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),  # Регистрация

    path('profile/', views.profile_view, name='profile'),
    path("confirm-borrow/", views.confirm_borrow, name="confirm_borrow"),
    path('books', views.books, name='books'),
    path('ebooks', views.ebooks, name='ebooks'),

    path('employee/', views.employee, name='employee'),
    path('search/students/', views.search_students, name='search_students'),
    path('search/books/', views.search_books, name='search_books'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('return/', views.return_book, name='return_book'),
    path('search/borrowed/', views.search_borrowed_books, name='search_borrowed_books'),


]



# Настройте обработку статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
