"""
プレゼンテーションアプリのURLパターン定義

このモジュールは、プレゼンテーション管理アプリケーションのURLパターンを定義します。
各エンドポイントは特定のビュー関数にマッピングされています。
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # 基本ページ
    path('', views.index, name='index'),
    path('list/', views.list_presentations, name='list'),
    
    # プレゼンテーション作成
    path('create/', views.create, name='create'),
    
    # プレゼンテーション操作
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/download/', views.download, name='download'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    
    # テンプレート管理
    path('template/info/', views.template_info, name='template_info'),
    path('template/edit/', views.edit_template, name='edit_template'),
    
    # 認証
    path('logout/', LogoutView.as_view(next_page='index', http_method_names=['get', 'post']), name='logout'),
] 