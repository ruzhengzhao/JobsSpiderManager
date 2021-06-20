from django.urls import path

from . import views

app_name = 'JobsDB'
urlpatterns = [
    path('', views.index, name='index'),
    path('collect/', views.collect, name='collect'),
    path('delete/', views.delete, name='delete'),
    path('deleteall/', views.delete_all, name='delete_all'),
    path('overview/', views.overview, name="overview"),
    path('analysis/', views.analysis, name="analysis"),
    path('download/', views.download, name="download")
]
