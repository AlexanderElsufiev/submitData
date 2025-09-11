
from django.db import models


class PerevalUser(models.Model):
    """Модель пользователя"""
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    fam = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, blank=True)
    otc = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.fam} {self.name} {self.otc}"

    class Meta:
        db_table = 'pereval_users'

class PerevalCoords(models.Model):
    """Модель координат"""
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"Lat: {self.latitude}, Lon: {self.longitude}, H: {self.height}"

    class Meta:
        db_table = 'pereval_coords'


class PerevalAdded(models.Model):
    """Основная модель перевала"""
    beauty_title = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)
    other_titles = models.CharField(max_length=500, blank=True)
    connect = models.CharField(max_length=500, blank=True)
    add_time = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True)

    """Модель уровня сложности"""
    winter = models.CharField(max_length=10, blank=True)
    spring = models.CharField(max_length=10, blank=True)
    summer = models.CharField(max_length=10, blank=True)
    autumn = models.CharField(max_length=10, blank=True)

    """добавки нужного статуса"""
    status = models.CharField(
        max_length=8,
        choices=[('new', 'Новый'),('pending', 'На рассмотрении'),('accepted', 'Принят'),('rejected', 'Отклонен'),],
        default='new'
    )

    """Связи с другими моделями"""
    user = models.ForeignKey(PerevalUser, on_delete=models.CASCADE)  # =1
    coords = models.ForeignKey(PerevalCoords, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.beauty_title} {self.title}"

    class Meta:
        db_table = 'pereval_added'


class PerevalImageAsIs(models.Model):
    """Модель для хранения самих изображений"""
    title = models.CharField(max_length=50)
    img = models.TextField()  # Храним hex данные изображения

    def __str__(self):
        return f"Изображение: {self.title}"

    class Meta:
        db_table = 'pereval_images_as_is'


class PerevalImage(models.Model):
   """Модель связи между перевалами и изображениями"""
   pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name='images')
   image = models.OneToOneField(PerevalImageAsIs, on_delete=models.CASCADE, related_name='pereval_link')

   def __str__(self):
       return f"Перевал {self.pereval.title} - Изображение {self.image.title}"

   class Meta:
       db_table = 'pereval_images'


