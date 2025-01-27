from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from .utils import extract_docx_thumbnail, extract_pdf_thumbnail

import os
from django.conf import settings

class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True, blank=False, null=False, verbose_name="Имя пользователя")
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Полное имя")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    passport_issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи паспорта")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер телефона")
    jshshir_code = models.CharField(max_length=14, blank=True, null=True, verbose_name="Код JSHSHIR")
    course = models.CharField(max_length=10, blank=True, null=True, verbose_name="Курс")
    group = models.CharField(max_length=10, blank=True, null=True, verbose_name="Группа")
    academic_year = models.CharField(max_length=20, blank=True, null=True, verbose_name="Академический год")
    semester = models.CharField(max_length=10, blank=True, null=True, verbose_name="Семестр")
    specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Специализация")
    education_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тип образования")
    education_form = models.CharField(max_length=50, blank=True, null=True, verbose_name="Форма обучения")
    validate_url = models.URLField(blank=True, null=True, verbose_name="Ссылка для проверки")
    is_student = models.BooleanField(null=True, blank=True, verbose_name="Студент")
    is_teacher = models.BooleanField(null=True, blank=True, verbose_name="Преподаватель")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name="Фото профиля")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.full_name if self.full_name else self.username


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя автора")
    biography = models.TextField(blank=True, null=True, verbose_name="Биография")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.name


class CategoryForPhysicalBoosk(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория(Физические)"
        verbose_name_plural = "Категории(Физические)"

    def __str__(self):
        return self.name

class CategoryForElectronicBooks(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория(Электронные)"
        verbose_name_plural = "Категории(Электронные)"

    def __str__(self):
        return self.name

class PhysicalBook(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название книги")
    category = models.ForeignKey(CategoryForPhysicalBoosk, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    publication_date = models.DateField(verbose_name="Дата публикации")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Доступные копии")
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name="Язык")
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="ISBN")
    publisher = models.CharField(max_length=255, blank=True, null=True, verbose_name="Издатель")
    pages = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество страниц")
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Штрихкод")
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True, verbose_name="Изображение обложки")

    class Meta:
        verbose_name = "Физическая книга"
        verbose_name_plural = "Физические книги"

    def __str__(self):
        return self.title


class ElectronicBook(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название книги")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")
    category = models.ForeignKey(CategoryForElectronicBooks, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    file = models.FileField(upload_to='ebooks/', verbose_name="Файл книги")
    thumbnail = models.ImageField(upload_to='ebook_thumbnails/', null=True, blank=True, verbose_name="Обложка книги")

    def save(self, *args, **kwargs):
        # Генерация миниатюры
        if self.file and isinstance(self.file.name, str):
            file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, f'ebook_thumbnails/{self.id}_thumbnail.png')
            
            if self.file.name.endswith('.pdf'):
                thumbnail = extract_pdf_thumbnail(file_path, thumbnail_path)
            elif self.file.name.endswith('.docx'):
                thumbnail = extract_docx_thumbnail(file_path, thumbnail_path)
            else:
                thumbnail = None
            
            if thumbnail:
                self.thumbnail = f'ebook_thumbnails/{self.id}_thumbnail.png'
            else:
                self.thumbnail = 'ebook_thumbnails/default-thumbnail.jpg'
        else:
            self.thumbnail = 'ebook_thumbnails/default-thumbnail.jpg'

        super().save(*args, **kwargs)


    def download_count(self):
        return self.downloads.count()

    class Meta:
        verbose_name = "Электронная книга"
        verbose_name_plural = "Электронные книги"

    def __str__(self):
        return self.title


class BorrowingRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    book = models.ForeignKey(PhysicalBook, on_delete=models.CASCADE, verbose_name="Книга")
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата возврата")
    is_returned = models.BooleanField(default=False, verbose_name="Возвращено")

    class Meta:
        verbose_name = "Запись о выдаче"
        verbose_name_plural = "Записи о выдачах"

    def __str__(self):
        return f"{self.user.full_name} - {self.book.title}"


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    book = models.ForeignKey(PhysicalBook, on_delete=models.CASCADE, verbose_name="Книга")
    content = models.TextField(verbose_name="Содержание отзыва")
    rating = models.PositiveSmallIntegerField(default=0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.user.full_name} - {self.book.title} ({self.rating} stars)"


class LibrarySettings(models.Model):
    max_borrow_days = models.PositiveIntegerField(default=14, verbose_name="Максимальные дни аренды")

    class Meta:
        verbose_name = "Настройки библиотеки"
        verbose_name_plural = "Настройки библиотеки"

    def __str__(self):
        return "Настройки библиотеки"


class DownloadLog(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="downloads"
    )
    ebook = models.ForeignKey(
        ElectronicBook,
        on_delete=models.CASCADE,
        verbose_name="Электронная книга",
        related_name="downloads"
    )
    download_date = models.DateTimeField(default=now, verbose_name="Дата скачивания")
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP-адрес пользователя"
    )
    user_agent = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Данные устройства"
    )

    class Meta:
        verbose_name = "Лог скачивания"
        verbose_name_plural = "Логи скачиваний"
        ordering = ['-download_date']

    def __str__(self):
        return f"{self.user.full_name or self.user.username} скачал {self.ebook.title} ({self.download_date})"
