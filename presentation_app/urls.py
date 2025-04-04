"""
プレゼンテーションアプリのURLルーティング設定

このモジュールは、プレゼンテーションアプリの各ビュー関数へのURLパスを定義します。
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.presentation_list, name='presentation_list'),
    path('create/', views.create_presentation, name='create_presentation'),
    path('edit/<int:pk>/', views.edit_presentation, name='edit_presentation'),
    path('download/<int:pk>/', views.download_pptx, name='download_pptx'),
] 