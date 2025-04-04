"""
プレゼンテーションアプリのフォームモジュール

このモジュールは、プレゼンテーションの作成と編集に使用するフォームクラスを定義します。
MarkdownおよびNLPベースのプレゼンテーション用のフォームを提供します。
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

class NaturalLanguageForm(forms.ModelForm):
    """
    自然言語プレゼンテーション用のフォーム
    
    自然言語でプレゼンテーションを作成・編集するためのフォームです。
    タイトル、内容、テンプレート使用の有無を設定できます。
    """
    
    # 自然言語のサンプルコンテンツ
    SAMPLE_CONTENT = """スライド: はじめに
このプレゼンテーションは自然言語から自動生成されています。
段落ごとに自動的にスライドに変換されます。

スライド: 箇条書きの例
- こんな感じで箇条書きを書くことができます
- 2つ目の項目
- 3つ目の項目

スライド: 文章の例
これは普通の文章です。長い文章は自動的に文ごとに分割されて箇条書きになります。
2つ目の文です。このように自動的に整形されます。

スライド: まとめ
自然言語でプレゼンテーション内容を書くことで、簡単にスライドを作成できます。
"""
    
    # テンプレート使用の選択フィールド
    use_template = forms.BooleanField(
        required=False,
        initial=True,
        label='テンプレートを使用する',
        help_text='チェックすると、デザインテンプレートを使用してプレゼンテーションを生成します'
    )
    
    class Meta:
        model = Presentation
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'nl-editor'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 初期値として、新規作成時のみサンプルを設定
        if not self.instance.pk and not self.initial.get('content'):
            self.initial['content'] = self.SAMPLE_CONTENT
        
        # インスタンスがある場合はテンプレート使用フラグを設定
        if self.instance.pk:
            self.initial['use_template'] = self.instance.use_template
        
        # フィールドの説明
        self.fields['title'].label = 'タイトル'
        self.fields['content'].label = '自然言語内容'
        
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