"""
プレゼンテーション管理のビューモジュール

このモジュールは、プレゼンテーションの作成、編集、一覧表示、ダウンロードなどの
機能を提供するビュー関数を定義します。
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Presentation
from .services import MarpService

@login_required
def presentation_list(request):
    """
    プレゼンテーション一覧を表示
    
    ログインユーザーが作成したプレゼンテーションの一覧を表示します。
    
    Args:
        request: HTTPリクエストオブジェクト
        
    Returns:
        HTTPレスポンス: プレゼンテーション一覧のテンプレートを表示
    """
    presentations = Presentation.objects.filter(author=request.user).order_by('-updated_at')
    return render(request, 'presentation_app/list.html', {'presentations': presentations})

@login_required
def create_presentation(request):
    """
    新規プレゼンテーション作成
    
    新しいプレゼンテーションを作成するフォームを表示し、
    フォーム送信時にプレゼンテーションを保存します。
    
    Args:
        request: HTTPリクエストオブジェクト
        
    Returns:
        HTTPレスポンス: 作成フォームまたはリダイレクト
    """
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        theme = request.POST.get('theme', 'default')
        
        if title and content:
            presentation = Presentation.objects.create(
                title=title,
                content=content,
                theme=theme,
                author=request.user
            )
            return redirect('edit_presentation', pk=presentation.pk)
    
    # テンプレートサンプルを提供
    sample_content = """# マイプレゼンテーション

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
    
    return render(request, 'presentation_app/create.html', {'sample_content': sample_content})

@login_required
def edit_presentation(request, pk):
    """
    プレゼンテーションの編集
    
    指定されたIDのプレゼンテーションを編集するフォームを表示し、
    フォーム送信時にプレゼンテーションを更新します。
    
    Args:
        request: HTTPリクエストオブジェクト
        pk (int): 編集するプレゼンテーションのID
        
    Returns:
        HTTPレスポンス: 編集フォームまたはリダイレクト
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        theme = request.POST.get('theme', 'default')
        
        if title and content:
            presentation.title = title
            presentation.content = content
            presentation.theme = theme
            presentation.save()
            return redirect('presentation_list')
    
    return render(request, 'presentation_app/edit.html', {'presentation': presentation})

@login_required
def download_pptx(request, pk):
    """
    PPTXファイルのダウンロード
    
    指定されたIDのプレゼンテーションをPPTX形式でダウンロードします。
    
    Args:
        request: HTTPリクエストオブジェクト
        pk (int): ダウンロードするプレゼンテーションのID
        
    Returns:
        HTTPレスポンス: PPTXファイルまたはエラーメッセージ
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
    
    if pptx_content:
        response = HttpResponse(
            pptx_content,
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        filename = f"{presentation.title.replace(' ', '_')}.pptx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("PPTX生成に失敗しました", status=500)
