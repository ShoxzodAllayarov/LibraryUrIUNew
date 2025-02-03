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
from .forms import ProfileUpdateForm

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



from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ✅ Добавляем импорт
from .forms import ProfileUpdateForm

def profile_view(request):
    user = request.user
    borrow_records = BorrowingRecord.objects.filter(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профиль успешно обновлен!")  # ✅ Сообщение об успешном обновлении
            return redirect('profile')  # ✅ Перенаправляем на страницу профиля
        else:
            messages.error(request, "Ошибка обновления профиля. Проверьте введенные данные.")  # ✅ Сообщение об ошибке

    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {
        'form': form,
        'user': user,
        'borrow_records': borrow_records
    })
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import BorrowingRecord

def confirm_borrow(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_id = data.get("record_id")
            if not record_id:
                return JsonResponse({"success": False, "error": "Kitobni tanlang!"}, status=400)

            record = get_object_or_404(BorrowingRecord, id=record_id, user=request.user, is_confirmed=False)
            record.is_confirmed = True
            record.save()

            return JsonResponse({"success": True, "message": "Kitob tasdiqlandi!"})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Xato soʻrov!"}, status=400)

    return JsonResponse({"success": False, "error": "Noto‘g‘ri so‘rov turi!"}, status=400)


from django.http import JsonResponse
from django.db.models import Q
from .models import CustomUser, PhysicalBook

from django.shortcuts import render, get_object_or_404
from .models import CustomUser, PhysicalBook, BorrowingRecord
import logging

logger = logging.getLogger(__name__)

def employee(request):
    returned_books = BorrowingRecord.objects.filter(is_returned=True, is_confirmed=True)
    borrowed_books = BorrowingRecord.objects.filter(is_returned=False, is_confirmed=True)
    pending_books = BorrowingRecord.objects.filter(is_returned=False, is_confirmed=False)
    return render(request, 'employee.html', {
        "returned_books": returned_books,
        "borrowed_books": borrowed_books,
        "pending_books": pending_books
    })

def borrow_book(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        book_id = request.POST.get("book_id")

        if not student_id or not book_id:
            return JsonResponse({"success": False, "error": "Выберите студента и книгу!"}, status=400)

        student = get_object_or_404(CustomUser, id=student_id)
        book = get_object_or_404(PhysicalBook, id=book_id)

        # Проверяем, есть ли уже невозвращенная книга
        if BorrowingRecord.objects.filter(user=student, book=book, is_returned=False).exists():
            return JsonResponse({"success": False, "error": "Эта книга уже выдана этому студенту!"}, status=400)

        # Создаем запись о выдаче
        BorrowingRecord.objects.create(user=student, book=book, is_confirmed=False)  # Подтверждаем автоматически

        return JsonResponse({"success": True, "message": f"Книга '{book.title}' выдана студенту {student.full_name}"})

    return JsonResponse({"success": False, "error": "Метод запроса должен быть POST!"}, status=405)

# API для возврата книги
from django.utils.timezone import now

def return_book(request):
    if request.method == "POST":
        borrow_id = request.POST.get("borrow_id")

        if not borrow_id:
            return JsonResponse({"success": False, "error": "Выберите запись!"}, status=400)

        borrow_record = get_object_or_404(BorrowingRecord, id=borrow_id, is_returned=False, is_confirmed=True)

        borrow_record.is_returned = True
        borrow_record.return_date = now()  # Устанавливаем текущую дату и время
        borrow_record.save()

        return JsonResponse({"success": True, "message": f"Книга '{borrow_record.book.title}' возвращена!"})

    return JsonResponse({"success": False, "error": "Неверный запрос!"}, status=400)


# API для поиска книг, которые не возвращены
def search_borrowed_books(request):
    query = request.GET.get('q', '').strip()
    borrow_records = BorrowingRecord.objects.filter(
        is_confirmed=True, is_returned=False
    ).filter(
        Q(user__full_name__icontains=query) |
        Q(book__title__icontains=query) |
        Q(book__isbn__icontains=query)
    )[:10]

    results = [{"id": br.id, "text": f"{br.user.full_name} - {br.book.title} (ISBN: {br.book.isbn})"} for br in borrow_records]

    return JsonResponse({"results": results})

def search_students(request):
    query = request.GET.get('q', '')
    students = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(full_name__icontains=query) |
        Q(id__icontains=query)
    )[:10]  # Ограничиваем до 10 результатов

    results = [{"id": student.id, "text": f"{student.full_name} ({student.username})"} for student in students]
    return JsonResponse({"results": results})

def search_books(request):
    query = request.GET.get('q', '')
    books = PhysicalBook.objects.filter(
        Q(title__icontains=query) |
        Q(author__name__icontains=query) |
        Q(isbn__icontains=query) |
        Q(barcode__icontains=query)
    )[:10]

    results = [{"id": book.id, "text": f"{book.title} - {book.author} (ISBN: {book.isbn})"} for book in books]
    return JsonResponse({"results": results})

