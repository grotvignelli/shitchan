from django.urls import path, include

from rest_framework.routers import DefaultRouter

from shitchan import views


router = DefaultRouter()
router.register('boards', views.ManageBoardViewSet)


app_name = 'shitchan'
urlpatterns = [
    path('', include(router.urls)),
]
