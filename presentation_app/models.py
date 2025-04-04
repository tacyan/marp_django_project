"""
プレゼンテーションアプリのモデル定義

このモジュールは、プレゼンテーション管理のためのモデルクラスを定義します。
プレゼンテーションのメタデータと内容を格納するためのデータベーススキーマを提供します。
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

# Create your models here.

class Presentation(models.Model):
    """
    プレゼンテーションモデル
    
    プレゼンテーションの内容とメタデータを保存します。
    Markdownまたは自然言語のデータからプレゼンテーションを生成するために使用されます。
    """
    
    # コンテンツタイプの選択肢
    CONTENT_TYPE_CHOICES = [
        ('markdown', 'Markdown'),
        ('natural_language', '自然言語'),
    ]
    
    # フォントサイズの選択肢
    FONT_SIZE_CHOICES = [
        ('large', '大きい'),
        ('medium', '中くらい'),
        ('small', '小さい'),
        ('auto', '自動判定'),
    ]
    
    # 基本フィールド
    title = models.CharField(max_length=255, verbose_name='タイトル')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作成者', null=True, blank=True)
    
    # 表示設定フィールド
    theme = models.CharField(max_length=50, default='default', verbose_name='テーマ')
    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPE_CHOICES, 
        default='markdown', 
        verbose_name='コンテンツタイプ'
    )
    use_template = models.BooleanField(default=False, verbose_name='テンプレート使用')
    font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default='auto',
        verbose_name='フォントサイズ'
    )
    max_chars_per_slide = models.IntegerField(
        default=0,  # 0は自動設定を意味する
        verbose_name='1スライドあたりの最大文字数'
    )
    
    def __str__(self):
        """
        モデルの文字列表現
        
        Returns:
            str: プレゼンテーションのタイトル
        """
        return self.title
    
    def get_absolute_url(self):
        """
        このオブジェクトの絶対URL
        
        Returns:
            str: 詳細ページへのURL
        """
        from django.urls import reverse
        return reverse('detail', kwargs={'pk': self.pk})
    
    def get_display_type(self):
        """
        表示用のプレゼンテーションタイプを取得
        
        Returns:
            str: 表示用タイプ名
        """
        if self.content_type == 'markdown':
            return 'Markdown'
        elif self.content_type == 'natural_language':
            if self.use_template:
                return '自然言語（テンプレート使用）'
            else:
                return '自然言語'
        return 'その他'
    
    def get_font_size_setting(self):
        """
        フォントサイズの設定を取得
        
        自動設定の場合は文章の特徴から適切なサイズを決定します。
        
        Returns:
            str: フォントサイズ設定
        """
        # 自動判定の場合
        if self.font_size == 'auto':
            # 文字数から判定
            avg_chars_per_para = len(self.content) / max(self.content.count('\n\n') + 1, 1)
            
            if avg_chars_per_para > 200:
                return 'small'
            elif avg_chars_per_para > 100:
                return 'medium'
            else:
                return 'large'
        
        return self.font_size
    
    def get_chars_per_slide(self):
        """
        1スライドあたりの文字数を取得
        
        フォントサイズまたは設定値に基づいて計算します。
        
        Returns:
            int: 1スライドあたりの文字数
        """
        # 明示的に設定されている場合
        if self.max_chars_per_slide > 0:
            return self.max_chars_per_slide
        
        # フォントサイズに基づく自動設定
        font_size = self.get_font_size_setting()
        
        if font_size == 'large':
            return 100
        elif font_size == 'medium':
            return 200
        elif font_size == 'small':
            return 300
        
        # デフォルト値
        return 200
