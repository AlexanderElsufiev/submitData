import base64
import os
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SubmitDataSerializer

# Импортируем ваш класс
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from class_fstr import Fstr


class SubmitDataAPIView(APIView):
    """
    REST API endpoint для отправки данных горного перевала
    """

    def post(self, request, *args, **kwargs):
        try:
            # Парсим данные формы
            raw_data = {
                "beautyTitle": request.data.get('beautyTitle', ''),
                "title": request.data.get('title', ''),
                "other_titles": request.data.get('other_titles', ''),
                "connect": request.data.get('connect', ''),
                "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": {
                    "email": request.data.get('user_email', ''),
                    "phone": request.data.get('user_phone', ''),
                    "fam": request.data.get('user_fam', ''),
                    "name": request.data.get('user_name', ''),
                    "otc": request.data.get('user_otc', '')
                },
                "coords": {
                    "latitude": request.data.get('coords_latitude', ''),
                    "longitude": request.data.get('coords_longitude', ''),
                    "height": request.data.get('coords_height', '')
                },
                "level": {
                    "winter": request.data.get('level_winter', ''),
                    "summer": request.data.get('level_summer', ''),
                    "autumn": request.data.get('level_autumn', ''),
                    "spring": request.data.get('level_spring', '')
                }
            }

            # Обрабатываем изображения
            images_data = []
            uploaded_files = request.FILES
            image_titles = []

            # Собираем заголовки изображений
            for key in request.data.keys():
                if key.startswith('image_title_'):
                    index = key.split('_')[-1]
                    image_titles.append({
                        'index': index,
                        'title': request.data[key]
                    })

            # Сортируем по индексу
            image_titles.sort(key=lambda x: int(x['index']))

            # Обрабатываем файлы изображений
            image_index = 1
            for title_info in image_titles:
                file_key = f'image_file_{title_info["index"]}'
                if file_key in uploaded_files:
                    image_file = uploaded_files[file_key]

                    # Читаем содержимое файла и конвертируем в hex
                    image_content = image_file.read()
                    hex_content = image_content.hex()

                    images_data.append({
                        "id": image_index,
                        "title": title_info["title"],
                        "img": hex_content
                    })
                    image_index += 1

            if not images_data:
                return Response(
                    {"error": "Необходимо загрузить хотя бы одно изображение"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            images = {"images": images_data}

            # Создаем экземпляр класса и вызываем метод
            fstr = Fstr()
            result = fstr.my_post(raw_data, images)

            return Response({
                "message": "Данные успешно отправлены",
                "status": "success",
                "data": {
                    "raw_data": raw_data,
                    "images_count": len(images_data)
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": f"Ошибка при обработке данных: {str(e)}",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitFormView(TemplateView):
    """
    Представление для отображения формы тестирования
    """
    template_name = 'api/submit_form.html'



