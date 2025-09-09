
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import * #PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs

from .serializers import *  #SubmitDataSerializer, PerevalDetailSerializer, PerevalUpdateSerializer, PerevalListSerializer

class SubmitDataAPIView(APIView):
    """
    REST API endpoint для отправки данных горного перевала
    Использует Django ORM для записи в PostgreSQL

    POST /submitData/ — создать новую запись
    GET /submitData/?user__email=<email> — список записей пользователя
    """

    # ИЗ 1 СПРИНТА ЗАПИСЬ
    def post(self, request, *args, **kwargs):
        try:
            # Получаем вложенные данные пользователя
            user_data = request.data.get('user', {})

            # Создаем или получаем пользователя
            user, created = PerevalUser.objects.get_or_create(
                email=user_data.get('email', ''),
                defaults={
                    'phone': user_data.get('phone', ''),
                    'fam': user_data.get('fam', ''),
                    'name': user_data.get('name', ''),
                    'otc': user_data.get('otc', '')
                }
            )

            # Получаем вложенные данные координат
            coords_data = request.data.get('coords', {})

            # Создаем координаты
            coords = PerevalCoords.objects.create(
                latitude=coords_data.get('latitude', ''),
                longitude=coords_data.get('longitude', ''),
                height=coords_data.get('height', '')
                # latitude = request.data.get('coords_latitude', ''),
                # longitude = request.data.get('coords_longitude', ''),
                # height = request.data.get('coords_height', '')

            )

            # Получаем вложенные данные уровней сложности
            level_data = request.data.get('level', {})

            # Создаем основную запись перевала
            pereval = PerevalAdded.objects.create(
                beauty_title=request.data.get('beautyTitle', ''),
                title=request.data.get('title', ''),
                other_titles=request.data.get('other_titles', ''),
                connect=request.data.get('connect', ''),
                add_time=datetime.now(),
                winter=level_data.get('winter', ''),
                spring=level_data.get('spring', ''),
                summer=level_data.get('summer', ''),
                autumn=level_data.get('autumn', ''),
                user=user,
                coords=coords,
                # level=level
            )

            # Обрабатываем изображения из массива images
            images_data = request.data.get('images', [])
            images_count = 0

            for image_data in images_data:
                if 'title' in image_data and 'data' in image_data:
                    # Создаем запись изображения в таблице pereval_images_as_is
                    image_as_is = PerevalImageAsIs.objects.create(
                        title=image_data['title'],
                        img=image_data['data']  # Предполагаем, что данные уже в hex формате
                    )

                    # Создаем связь между перевалом и изображением
                    PerevalImage.objects.create(
                        pereval=pereval,
                        image=image_as_is
                    )
                    images_count += 1

            if images_count == 0:
                # Если нет изображений, удаляем созданные записи
                pereval.delete()
                coords.delete()
                if created:  # Удаляем пользователя только если он был создан
                    user.delete()

                return Response(
                    {"error": "Необходимо загрузить хотя бы одно изображение"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "message": "Данные успешно отправлены",
                "status": "success",
                "data": {
                    "id": pereval.id,
                    "title": f"{pereval.beauty_title} {pereval.title}",
                    "user": f"{user.fam} {user.name} {user.otc}",
                    "coords": f"Lat: {coords.latitude}, Lon: {coords.longitude}",
                    "images_count": images_count,
                    "date_added": pereval.date_added.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": f"Ошибка при обработке данных: {str(e)}",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ДЛЯ 2 СПРИНТА GET
    def get(self, request, *args, **kwargs):
        """GET /submitData/?user__email=<email> — список данных обо всех объектах пользователя"""
        try:
            email = request.query_params.get('user__email')

            if not email:
                return Response(
                    {"message": "Параметр user__email обязателен"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ищем пользователя
            try:
                user = PerevalUser.objects.get(email=email)
            except PerevalUser.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)

            # Получаем все перевалы пользователя
            perevals = PerevalAdded.objects.filter(user=user).select_related('coords').order_by('-date_added')

            # Формируем данные для ответа
            data = []
            for pereval in perevals:
                pereval_data = {
                    'id': pereval.id,
                    'beauty_title': pereval.beauty_title,
                    'title': pereval.title,
                    'other_titles': pereval.other_titles,
                    'connect': pereval.connect,
                    'add_time': pereval.add_time,
                    'coords': {
                        'latitude': pereval.coords.latitude,
                        'longitude': pereval.coords.longitude,
                        'height': pereval.coords.height
                    },
                    'level': {
                        'winter': pereval.winter,
                        'spring': pereval.spring,
                        'summer': pereval.summer,
                        'autumn': pereval.autumn
                    },
                    'status': pereval.status,
                    'date_added': pereval.date_added
                }
                data.append(pereval_data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": f"Ошибка при получении списка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class SubmitFormView(TemplateView):
    """
    Представление для отображения формы тестирования
    """
    template_name = 'api/submit_form.html'

