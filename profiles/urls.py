from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import (home, weather, exam, result_exam, wedding, wedding_photo, secret_santa, result_secret_santa)


urlpatterns = [
    path('', home, name='home'),
    path('weather', weather, name='weather'),
    path('exam/<str:user_name>', exam, name='exam'),
    path('result_exam/<str:user_name>', result_exam, name='result_exam'),
    path('wedding', wedding, name='wedding'),
    path('wedding_photo', wedding_photo, name='wedding_photo'),
    path('secret_santa', secret_santa, name='secret_santa'),
    path('result_secret_santa/<str:group_uuid>', result_secret_santa, name='result_secret_santa'),
]

urlpatterns += staticfiles_urlpatterns()