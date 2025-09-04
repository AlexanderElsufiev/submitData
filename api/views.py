
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import * #PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs
from .serializers import SubmitDataSerializer




class SubmitDataAPIView(APIView):
    """
    REST API endpoint для отправки данных горного перевала
    Использует Django ORM для записи в PostgreSQL
    """

    def post(self, request, *args, **kwargs):
        try:
            # Создаем или получаем пользователя
            user, created = PerevalUser.objects.get_or_create(
                email=request.data.get('user_email', ''),
                defaults={
                    'phone': request.data.get('user_phone', ''),
                    'fam': request.data.get('user_fam', ''),
                    'name': request.data.get('user_name', ''),
                    'otc': request.data.get('user_otc', '')
                }
            )

            # Создаем координаты
            coords = PerevalCoords.objects.create(
                latitude=request.data.get('coords_latitude', ''),
                longitude=request.data.get('coords_longitude', ''),
                height=request.data.get('coords_height', '')
            )

            # Создаем основную запись перевала
            pereval = PerevalAdded.objects.create(
                beauty_title=request.data.get('beautyTitle', ''),
                title=request.data.get('title', ''),
                other_titles=request.data.get('other_titles', ''),
                connect=request.data.get('connect', ''),
                add_time=datetime.now(),
                winter=request.data.get('level_winter', ''),
                spring=request.data.get('level_spring', ''),
                summer=request.data.get('level_summer', ''),
                autumn=request.data.get('level_autumn', ''),
                user=user,
                coords=coords,
                # level=level
            )

            # Обрабатываем изображения
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

            # Создаем записи изображений
            images_count = 0
            for title_info in image_titles:
                file_key = f'image_file_{title_info["index"]}'
                if file_key in uploaded_files:
                    image_file = uploaded_files[file_key]

                    # Читаем содержимое файла и конвертируем в hex
                    image_content = image_file.read()
                    hex_content = image_content.hex()

                    # Создаем запись изображения в таблице pereval_images_as_is
                    image_as_is = PerevalImageAsIs.objects.create(
                        title=title_info["title"],
                        img=hex_content
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
                # level.delete()
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



class SubmitFormView(TemplateView):
    """
    Представление для отображения формы тестирования
    """
    template_name = 'api/submit_form.html'




