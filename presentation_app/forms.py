"""
プレゼンテーションアプリのフォームモジュール

このモジュールは、プレゼンテーションの作成と編集に使用するフォームクラスを定義します。
Markdownベースのプレゼンテーション用のフォームを提供します。
"""

from django import forms
from .models import Presentation

class PresentationForm(forms.ModelForm):
    """
    Markdownプレゼンテーション用のフォーム
    
    Markdownフォーマットでプレゼンテーションを作成・編集するためのフォームです。
    タイトル、内容、テーマを設定できます。
    """
    
    # Markdownのサンプルコンテンツ
    SAMPLE_CONTENT = """# マイプレゼンテーション

## スライド1
最初のスライドの内容

---

## スライド2
- 箇条書き項目1
- 箇条書き項目2

---

## スライド3
![画像](https://example.com/image.jpg)
"""
    
    class Meta:
        model = Presentation
        fields = ['title', 'content', 'theme']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'markdown-editor'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 初期値として、新規作成時のみサンプルを設定
        if not self.instance.pk and not self.initial.get('content'):
            self.initial['content'] = self.SAMPLE_CONTENT
        
        # フィールドの説明
        self.fields['title'].label = 'タイトル'
        self.fields['content'].label = 'マークダウン内容'
        self.fields['theme'].label = 'テーマ'
        
        # フォームのカスタマイズ
        self.fields['theme'].widget = forms.Select(choices=[
            ('default', 'デフォルト'),
            ('gaia', 'Gaia'),
            ('uncover', 'Uncover'),
        ])
        
class TemplateUploadForm(forms.Form):
    """
    テンプレートアップロード用のフォーム
    
    PPTXテンプレートファイルをアップロードするためのフォームです。
    """
    
    template_file = forms.FileField(
        label='テンプレートファイル',
        help_text='PowerPoint (.pptx) ファイルをアップロードしてください',
    )
    
    def clean_template_file(self):
        """
        テンプレートファイルのバリデーション
        
        Args:
            なし
            
        Returns:
            FileField: 検証済みのファイルフィールド
            
        Raises:
            ValidationError: ファイル形式が無効な場合
        """
        template_file = self.cleaned_data.get('template_file')
        
        if template_file:
            # ファイル拡張子の確認
            if not template_file.name.lower().endswith('.pptx'):
                raise forms.ValidationError('PowerPoint (.pptx) ファイルのみアップロードできます')
                
            # ファイルサイズの確認 (10MB以下)
            if template_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('ファイルサイズは10MB以下にしてください')
        
        return template_file 