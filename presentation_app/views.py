"""
プレゼンテーションアプリのビューモジュール

このモジュールは、プレゼンテーション管理のためのビュー関数を提供します。
Markdownからプレゼンテーションを生成する機能を実装しています。
"""

import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Presentation
from .services import MarpService
from .forms import PresentationForm

@login_required
def index(request):
    """
    インデックスページを表示する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: インデックスページのレンダリング結果
    """
    return redirect('list')  # リストページにリダイレクト

@login_required
def list_presentations(request):
    """
    プレゼンテーション一覧を表示する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: プレゼンテーション一覧ページのレンダリング結果
    """
    presentations = Presentation.objects.filter(author=request.user)
    return render(request, 'presentation_app/list.html', {'presentations': presentations})

@login_required
def create(request):
    """
    Markdownによるプレゼンテーション作成ページを表示・処理する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: フォーム表示または処理結果
    """
    if request.method == 'POST':
        form = PresentationForm(request.POST)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.content_type = 'markdown'
            presentation.author = request.user
            presentation.save()
            
            # PPTXファイルの生成
            pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
            
            if pptx_content:
                # 成功時は詳細ページへリダイレクト
                messages.success(request, 'プレゼンテーションが作成されました')
                return redirect('detail', pk=presentation.pk)
            else:
                # 失敗時はエラーメッセージを表示
                form.add_error(None, "PPTXファイルの生成に失敗しました。Markdownの内容を確認してください。")
    else:
        form = PresentationForm()
    
    return render(request, 'presentation_app/create.html', {'form': form, 'action': 'create', 'sample_content': PresentationForm.SAMPLE_CONTENT})

@login_required
def edit(request, pk):
    """
    プレゼンテーション編集ページを表示・処理する
    
    Args:
        request: HTTPリクエスト
        pk: プレゼンテーションのID
        
    Returns:
        HTTPResponse: フォーム表示または処理結果
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PresentationForm(request.POST, instance=presentation)
        if form.is_valid():
            presentation = form.save()
            
            # PPTXファイルの再生成
            pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
            
            if pptx_content:
                messages.success(request, 'プレゼンテーションが更新されました')
                return redirect('detail', pk=presentation.pk)
            else:
                form.add_error(None, "PPTXファイルの生成に失敗しました。Markdownの内容を確認してください。")
    else:
        form = PresentationForm(instance=presentation)
    
    template = 'presentation_app/create.html'
    context = {'form': form, 'action': 'edit', 'presentation': presentation}
    
    return render(request, template, context)

@login_required
def detail(request, pk):
    """
    プレゼンテーション詳細ページを表示する
    
    Args:
        request: HTTPリクエスト
        pk: プレゼンテーションのID
        
    Returns:
        HTTPResponse: 詳細ページのレンダリング結果
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    return render(request, 'presentation_app/detail.html', {'presentation': presentation})

@login_required
def download(request, pk):
    """
    プレゼンテーションをPPTXファイルとしてダウンロードする
    
    Args:
        request: HTTPリクエスト
        pk: プレゼンテーションのID
        
    Returns:
        HTTPResponse: PPTXファイルのダウンロード
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    # PPTXを生成
    pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
    
    if not pptx_content:
        messages.error(request, "PPTXファイルの生成に失敗しました。内容を確認してください。")
        return redirect('detail', pk=pk)
    
    # ダウンロードレスポンスを作成
    response = HttpResponse(pptx_content, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    response['Content-Disposition'] = f'attachment; filename="{presentation.title}.pptx"'
    return response

@login_required
def delete(request, pk):
    """
    プレゼンテーションを削除する
    
    Args:
        request: HTTPリクエスト
        pk: プレゼンテーションのID
        
    Returns:
        HTTPResponse: 削除処理後のリダイレクト
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    if request.method == 'POST':
        presentation.delete()
        messages.success(request, 'プレゼンテーションが削除されました')
        return redirect('list')
    
    return render(request, 'presentation_app/delete.html', {'presentation': presentation})

@login_required
def template_info(request):
    """
    テンプレート情報のAPIエンドポイント
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        JsonResponse: テンプレート情報のJSON
    """
    template_info = MarpService.get_template_info()
    return JsonResponse(template_info)

@login_required
def edit_template(request):
    """
    テンプレート編集ページを表示・処理する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: フォーム表示または処理結果
    """
    from .forms import TemplateUploadForm
    
    if request.method == 'POST':
        form = TemplateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            template_file = request.FILES['template_file']
            
            # テンプレートファイルを保存
            template_path = os.path.join(settings.BASE_DIR, 'template.pptx')
            
            with open(template_path, 'wb+') as destination:
                for chunk in template_file.chunks():
                    destination.write(chunk)
            
            # テンプレート情報を更新
            MarpService.edit_template_pptx(template_path)
            
            messages.success(request, 'テンプレートが更新されました')
            return redirect('list')
    else:
        form = TemplateUploadForm()
    
    template_info = MarpService.get_template_info()
    context = {
        'form': form,
        'template_info': template_info
    }
    
    return render(request, 'presentation_app/edit_template.html', context)
