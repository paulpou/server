from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = (
    path('UploadTargetData/', views.uploadTD ,name="uploadTD"),
    path('TreasureHuntData/', views.uploadTHD, name="uploadTHD"),
    path('Search/', views.searchTargetData, name="searchTargetData"),
)