
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('submitData/', views.SubmitDataAPIView.as_view(), name='submit_data_api'),
    path('submit/', views.SubmitFormView.as_view(), name='submit_form'),
]

