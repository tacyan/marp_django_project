from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Presentation(models.Model):
    """
    プレゼンテーションデータモデル
    
    プレゼンテーションのタイトル、内容、テーマ、作成・更新時間、作者情報を管理します。
    
    属性:
        title (CharField): プレゼンテーションのタイトル
        content (TextField): Markdown形式のプレゼンテーション内容
        theme (CharField): Marpのテーマ名
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 最終更新日時
        author (ForeignKey): 作成者（Userモデルへの参照）
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    theme = models.CharField(max_length=50, default='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        """プレゼンテーションのタイトルを文字列表現として返す"""
        return self.title
