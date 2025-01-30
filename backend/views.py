from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.db.models import Count
from .models import (
        CustomUser, ElectronicBook, PhysicalBook,
        BorrowingRecord, CustomUser, CategoryForElectronicBooks,
        CategoryForPhysicalBooks
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
    
    top_week = get_top_borrowers("week")
    top_month = get_top_borrowers("month")

    # Получаем **ТОП-3 пользователей за всё время**
    top_all_time = (
        BorrowingRecord.objects.values("user")
        .annotate(total_books=Count("book"))
        .order_by("-total_books")[:3]
    )

    top_all_time_users = []
    for borrower in top_all_time:
        try:
            user = CustomUser.objects.get(id=borrower["user"])
            user.total_books = borrower["total_books"]
            top_all_time_users.append(user)
        except CustomUser.DoesNotExist:
            continue


    return render(request, 'index.html', {
        'most_borrowed_books': most_borrowed,
        'top_borrower': top_borrower,
        'top_books': top_books,
        "top_week": top_week,
        "top_month": top_month,
        "top_all_time": top_all_time_users,

    })

def ebooks(request):
    categories = CategoryForElectronicBooks.objects.prefetch_related('electronicbook_set').all()
            
    return render(request, 'ebooks.html', {
        'categories': categories

    })

def books(request):
    categories = CategoryForPhysicalBooks.objects.prefetch_related('physicalbook_set').all()
            
    return render(request, 'books.html', {
        'categories': categories

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


def get_top_borrowers(timeframe):
    """
    Получает **ТОП-3 пользователей**, которые взяли наибольшее количество книг в аренду
    за указанный промежуток времени (timeframe).
    """
    filters = {}
    today = now().date()

    if timeframe == "week":
        start_date = today - timedelta(days=today.weekday())  # Начало недели (понедельник)
        filters["borrow_date__gte"] = start_date

    elif timeframe == "month":
        start_date = today.replace(day=1)  # Начало текущего месяца
        filters["borrow_date__gte"] = start_date

    # Получаем **ТОП-3 пользователей по количеству арендованных книг**
    top_borrowers = (
        BorrowingRecord.objects.filter(**filters)
        .values("user")
        .annotate(total_books=Count("book"))
        .order_by("-total_books")[:3]
    )

    # Добавляем информацию о пользователе
    users = []
    for borrower in top_borrowers:
        try:
            user = CustomUser.objects.get(id=borrower["user"])
            user.total_books = borrower["total_books"]
            users.append(user)
        except CustomUser.DoesNotExist:
            continue

    return users

