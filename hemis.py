import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrIU.settings')  # Убедитесь, что 'UrIU.settings' корректный путь
if not settings.configured:
    django.setup()

import requests
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from datetime import datetime
from backend.models import CustomUser

# API настройки
url = "https://student.uriu.uz/rest/v1/data/student-list/"
headers = {
    'Authorization': 'Bearer gKrw-bP3VUhA7p-2bFnT3ar9PEMVORWv',
    'Content-Type': 'application/json'
}

# Функция для скачивания и сохранения изображения
def download_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return ContentFile(response.content)  # Возвращаем контент файла
        else:
            print(f"Не удалось скачать изображение: {image_url}")
            return None
    except Exception as e:
        print(f"Ошибка при скачивании изображения {image_url}: {e}")
        return None

# Функция для добавления студента в базу данных
def process_student(student):
    try:
        student_id = student.get("student_id_number")
        full_name = student.get("full_name")
        date_of_birth = student.get("birth_date")
        course = student.get("level", {}).get("name")
        group = student.get("group", {}).get("name")
        academic_year = student.get("educationYear", {}).get("name")
        semester = student.get("semester", {}).get("name")
        specialization = student.get("specialty", {}).get("name")
        education_type = student.get("educationType", {}).get("name")
        education_form = student.get("educationForm", {}).get("name")
        validate_url = student.get("validateUrl")
        profile_picture_url = student.get("image")  # URL фотографии

        # Преобразуем дату рождения из timestamp
        if date_of_birth:
            date_of_birth = datetime.fromtimestamp(date_of_birth / 1000).date()

        # Проверка на существование студента
        if CustomUser.objects.filter(username=student_id).exists():
            print(f"Студент с ID {student_id} уже существует.")
            return

        # Скачиваем изображение, если оно доступно
        profile_picture = None
        if profile_picture_url:
            profile_picture = download_image(profile_picture_url)

        # Создаем объект CustomUser
        user = CustomUser(
            username=student_id,
            full_name=full_name,
            date_of_birth=date_of_birth,
            course=course,
            group=group,
            academic_year=academic_year,
            semester=semester,
            specialization=specialization,
            education_type=education_type,
            education_form=education_form,
            validate_url=validate_url,
            is_student=True,
            password=make_password(student_id),  # Устанавливаем пароль как student_id
        )

        # Если изображение скачано, добавляем его в профиль
        if profile_picture:
            user.profile_picture.save(f"{student_id}.jpg", profile_picture, save=False)

        user.save()
        print(f"Студент {full_name} добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении студента {student.get('full_name')}: {e}")

# Функция для обработки студентов из API
def fetch_students_from_api():
    page = 1
    limit = 100
    while True:
        params = {
            'page': page,
            'limit': limit,
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                students = data['data']['items']
                if not students:  # Если нет студентов, выходим из цикла
                    print("Все данные получены.")
                    break
                for student in students:
                    process_student(student)
                page += 1
            else:
                print(f"Ошибка в данных API: {data['error']}")
                break
        else:
            print(f"Ошибка запроса: Код {response.status_code}, {response.text}")
            break

# Запуск процесса
if __name__ == "__main__":
    fetch_students_from_api()
