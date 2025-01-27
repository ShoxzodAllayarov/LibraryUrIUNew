from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.db.models import Count
from .models import (
        CustomUser, ElectronicBook, PhysicalBook,
        BorrowingRecord, CustomUser
)


def get_top_borrower_current_week():
    # Получаем текущую неделю
    start_of_week = now().date() - timedelta(days=now().date().weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Считаем количество записей о заимствовании для каждого пользователя
    top_borrower = (
        BorrowingRecord.objects.filter(borrow_date__range=(start_of_week, end_of_week))
        .values('user')
        .annotate(total_books=Count('book'))
        .order_by('-total_books')
        .first()
    )
    if top_borrower:
        user = CustomUser.objects.get(id=top_borrower['user'])
        user.total_books = top_borrower['total_books']
        return user
    return None


def index(request):
    top_books = ElectronicBook.objects.annotate(
        download_count=Count('downloads')
    ).order_by('-download_count')[:3]
    
    most_borrowed = PhysicalBook.objects.annotate(
        borrow_count=Count('borrowingrecord')
    ).order_by('-borrow_count')[:5]

    top_borrower = get_top_borrower_current_week()

    if top_borrower and not top_borrower.profile_picture:
        top_borrower.profile_picture = None  # Если нет файла, задаем None
            
    return render(request, 'index.html', {
        'most_borrowed_books': most_borrowed,
        'top_borrower': top_borrower,
        'top_books': top_books,

    })





def register(request):
    if request.user.is_authenticated:
        return redirect('index')  # Перенаправление, если пользователь уже авторизован

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('index')  # Перенаправление на главную страницу
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})