"""
プレゼンテーションアプリのビューモジュール

このモジュールは、プレゼンテーション管理のためのビュー関数を提供します。
Markdownや自然言語のテキストからプレゼンテーションを生成する機能を実装しています。
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
from .forms import PresentationForm, NaturalLanguageForm

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
    
    return render(request, 'presentation_app/create.html', {'form': form, 'action': 'create'})

@login_required
def natural_language_create(request):
    """
    自然言語によるプレゼンテーション作成ページを表示・処理する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: フォーム表示または処理結果
    """
    # テンプレート情報を取得
    template_info = MarpService.get_template_info()
    
    if request.method == 'POST':
        form = NaturalLanguageForm(request.POST)
        if form.is_valid():
            presentation = form.save(commit=False)
            presentation.content_type = 'natural_language'
            presentation.author = request.user
            
            # テンプレート使用フラグを設定
            use_template = form.cleaned_data.get('use_template', False)
            presentation.use_template = use_template
            
            presentation.save()
            
            # テンプレートパスの設定
            template_path = None
            if use_template:
                template_path = os.path.join(settings.BASE_DIR, 'template.pptx')
                
            # PPTXファイルの生成
            pptx_content = MarpService.natural_language_to_pptx(
                presentation.title, 
                presentation.content,
                template_path
            )
            
            if pptx_content:
                # 成功時は詳細ページへリダイレクト
                messages.success(request, '自然言語プレゼンテーションが作成されました')
                return redirect('detail', pk=presentation.pk)
            else:
                # 失敗時はエラーメッセージを表示
                form.add_error(None, "PPTXファイルの生成に失敗しました。入力内容を確認してください。")
    else:
        form = NaturalLanguageForm()
    
    context = {
        'form': form, 
        'action': 'natural_language_create',
        'template_info': template_info,
        'sample_content': NaturalLanguageForm.SAMPLE_CONTENT
    }
    return render(request, 'presentation_app/create_natural.html', context)

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
    
    # コンテンツタイプに応じたフォームとテンプレートを使用
    if presentation.content_type == 'markdown':
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
    else:  # 'natural_language'
        # テンプレート情報を取得
        template_info = MarpService.get_template_info()
        
        if request.method == 'POST':
            form = NaturalLanguageForm(request.POST, instance=presentation)
            if form.is_valid():
                presentation = form.save(commit=False)
                
                # テンプレート使用フラグを設定
                use_template = form.cleaned_data.get('use_template', False)
                presentation.use_template = use_template
                
                presentation.save()
                
                # テンプレートパスの設定
                template_path = None
                if use_template:
                    template_path = os.path.join(settings.BASE_DIR, 'template.pptx')
                    
                # PPTXファイルの再生成
                pptx_content = MarpService.natural_language_to_pptx(
                    presentation.title, 
                    presentation.content,
                    template_path
                )
                
                if pptx_content:
                    messages.success(request, '自然言語プレゼンテーションが更新されました')
                    return redirect('detail', pk=presentation.pk)
                else:
                    form.add_error(None, "PPTXファイルの生成に失敗しました。入力内容を確認してください。")
        else:
            form = NaturalLanguageForm(instance=presentation)
            
        template = 'presentation_app/create_natural.html'
        context = {
            'form': form, 
            'action': 'edit', 
            'presentation': presentation,
            'template_info': template_info,
            'edit_mode': True
        }
    
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
    
    # コンテンツタイプに応じてPPTXを生成
    if presentation.content_type == 'markdown':
        pptx_content = MarpService.markdown_to_pptx(presentation.content, presentation.theme)
    else:  # 'natural_language'
        # テンプレートパスの設定
        template_path = None
        if presentation.use_template:
            template_path = os.path.join(settings.BASE_DIR, 'template.pptx')
            
        pptx_content = MarpService.natural_language_to_pptx(
            presentation.title, 
            presentation.content,
            template_path
        )
    
    if pptx_content:
        # ファイル名の設定
        filename = f"{presentation.title}.pptx"
        
        # HTTPレスポンスの作成
        response = HttpResponse(pptx_content, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    else:
        # 生成に失敗した場合はエラーページを表示
        messages.error(request, 'プレゼンテーションファイルの生成に失敗しました。')
        
        # コンテンツタイプに応じてリダイレクト先を変える
        if presentation.content_type == 'markdown':
            return redirect('edit', pk=pk)
        else:
            return redirect('edit', pk=pk)

@login_required
def delete(request, pk):
    """
    プレゼンテーションを削除する
    
    Args:
        request: HTTPリクエスト
        pk: プレゼンテーションのID
        
    Returns:
        HTTPResponse: 削除後リダイレクト
    """
    presentation = get_object_or_404(Presentation, pk=pk, author=request.user)
    
    if request.method == 'POST':
        presentation.delete()
        messages.success(request, 'プレゼンテーションが削除されました')
        return redirect('list')
    
    return render(request, 'presentation_app/delete.html', {'presentation': presentation})

@login_required
def preview_natural_language(request):
    """
    自然言語プレゼンテーションのプレビューを提供するAPI
    
    Args:
        request: HTTPリクエスト（POSTメソッド）
        
    Returns:
        JsonResponse: プレビュー情報のJSON
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content', '')
        
        # 自然言語をスライド形式に解析
        slides = MarpService._parse_natural_language_to_slides(content)
        
        return JsonResponse({'slides': slides})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def template_info(request):
    """
    テンプレートPPTXの情報を提供するAPI
    
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
    テンプレートPPTXを編集するページを表示・処理する
    
    Args:
        request: HTTPリクエスト
        
    Returns:
        HTTPResponse: 編集ページのレンダリング結果または処理結果
    """
    # テンプレート情報を取得
    template_info = MarpService.get_template_info()
    
    if request.method == 'POST':
        # 新しいテンプレートファイルのアップロード
        if 'template_file' in request.FILES:
            template_file = request.FILES['template_file']
            
            # 一時ファイルとして保存
            temp_path = os.path.join(settings.BASE_DIR, 'temp_template.pptx')
            with open(temp_path, 'wb+') as destination:
                for chunk in template_file.chunks():
                    destination.write(chunk)
            
            # 既存のテンプレートを置き換え
            target_path = os.path.join(settings.BASE_DIR, 'template.pptx')
            
            # 既存のファイルをバックアップ
            if os.path.exists(target_path):
                backup_path = os.path.join(settings.BASE_DIR, 'template_backup.pptx')
                os.rename(target_path, backup_path)
            
            # 新しいファイルを移動
            os.rename(temp_path, target_path)
            
            # 更新されたテンプレート情報を取得
            template_info = MarpService.get_template_info()
            
            messages.success(request, 'テンプレートを更新しました')
            return render(request, 'presentation_app/edit_template.html', {
                'template_info': template_info,
                'success_message': 'テンプレートを更新しました。'
            })
    
    return render(request, 'presentation_app/edit_template.html', {'template_info': template_info})
