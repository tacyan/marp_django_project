"""
プレゼンテーション管理のビューモジュール

このモジュールは、プレゼンテーションの作成、編集、一覧表示、ダウンロードなどの
機能を提供するビュー関数を定義します。
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
            messages.success(request, 'プレゼンテーションが作成されました')
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
            messages.success(request, 'プレゼンテーションが更新されました')
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
    try:
        presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
        
        # 処理中メッセージをログに出力
        print(f"プレゼンテーション '{presentation.title}' のPPTX変換を開始します...")
        
        # Marp CLIを使用してPPTXを生成
        pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
        
        if pptx_content:
            # 成功時はPPTXファイルを返す
            response = HttpResponse(
                pptx_content,
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            filename = f"{presentation.title.replace(' ', '_')}.pptx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            print(f"プレゼンテーション '{presentation.title}' のPPTX変換に成功しました")
            return response
        else:
            # 変換に失敗した場合
            error_message = "PPTX変換に失敗しました。Marp CLIが正しくインストールされているか確認してください。"
            messages.error(request, error_message)
            print(error_message)
            return redirect('edit_presentation', pk=pk)
            
    except Exception as e:
        # 予期せぬエラーが発生した場合
        error_message = f"PPTX生成中にエラーが発生しました: {str(e)}"
        messages.error(request, error_message)
        print(error_message)
        return redirect('edit_presentation', pk=pk)
