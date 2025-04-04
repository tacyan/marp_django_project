"""
Marp CLIを操作するサービスモジュール

このモジュールは、Marp CLIを使用してMarkdownをプレゼンテーション形式に変換する機能を提供します。
"""

import os
import subprocess
import tempfile
import platform
import shutil
import re
import random
import math
from django.conf import settings
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

class MarpService:
    """
    Marp CLI操作のためのサービスクラス
    
    Markdownをプレゼンテーション形式（PPTX）に変換するためのサービスメソッドを提供します。
    """
    
    @staticmethod
    def markdown_to_pptx(markdown_content, theme='default'):
        """
        MarkdownをMarp CLIを使ってPPTXに変換する
        
        Args:
            markdown_content (str): 変換する元のMarkdown内容
            theme (str): 使用するMarpテーマ名（デフォルト: 'default'）
            
        Returns:
            bytes: 生成されたPPTXファイルのバイナリ内容、失敗時はNone
        """
        # 一時ディレクトリを作成
        temp_dir = tempfile.mkdtemp()
        markdown_path = os.path.join(temp_dir, 'presentation.md')
        output_path = os.path.join(temp_dir, 'presentation.pptx')
        
        try:
            # Markdownファイルの先頭にMarpディレクティブを追加
            marp_directives = f"""---
marp: true
theme: {theme}
---

"""
            full_markdown = marp_directives + markdown_content
            
            # Markdownファイルを作成
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(full_markdown)
            
            # Windowsの場合はshellをTrueに設定
            is_windows = platform.system() == 'Windows'
            
            # 3つの方法でMarp CLIの実行を試みる
            pptx_content = None
            
            # 方法1: npxを使用
            if pptx_content is None:
                try:
                    pptx_content = MarpService._try_npx_marp_cli(markdown_path, output_path, is_windows)
                except Exception as e:
                    print(f"npxでのMarp CLI実行に失敗: {e}")
            
            # 方法2: グローバルにインストールされているMarp CLIを使用
            if pptx_content is None:
                try:
                    pptx_content = MarpService._try_global_marp_cli(markdown_path, output_path, is_windows)
                except Exception as e:
                    print(f"グローバルMarp CLI実行に失敗: {e}")
            
            # 方法3: node_modulesから直接実行
            if pptx_content is None:
                try:
                    pptx_content = MarpService._try_local_marp_cli(markdown_path, output_path, is_windows)
                except Exception as e:
                    print(f"ローカルMarp CLI実行に失敗: {e}")
            
            if pptx_content:
                return pptx_content
            else:
                print("すべてのMarp CLI実行方法が失敗しました")
                return None
            
        except Exception as e:
            print(f"予期せぬエラー: {e}")
            return None
        finally:
            # 一時ファイルの削除（clean up）
            try:
                if os.path.exists(markdown_path):
                    os.remove(markdown_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"一時ファイルの削除中にエラーが発生しました: {e}")
                # エラーが発生しても処理を続行する
    
    @staticmethod
    def _try_npx_marp_cli(markdown_path, output_path, is_windows):
        """npxを使用してMarp CLIを実行する"""
        cmd = [
            'npx',
            '@marp-team/marp-cli',
            markdown_path,
            '--output', output_path,
            '--pptx',
            '--pptx-convert-infix', 'false'
        ]
        
        result = subprocess.run(cmd, check=True, shell=is_windows, capture_output=True)
        print(f"npx Marp CLI実行成功: {result.stdout.decode('utf-8', errors='ignore')}")
        
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                return f.read()
        return None
    
    @staticmethod
    def _try_global_marp_cli(markdown_path, output_path, is_windows):
        """グローバルにインストールされているMarp CLIを使用する"""
        cmd = [
            'marp',
            markdown_path,
            '--output', output_path,
            '--pptx',
            '--pptx-convert-infix', 'false'
        ]
        
        result = subprocess.run(cmd, check=True, shell=is_windows, capture_output=True)
        print(f"グローバルMarp CLI実行成功: {result.stdout.decode('utf-8', errors='ignore')}")
        
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                return f.read()
        return None
    
    @staticmethod
    def _try_local_marp_cli(markdown_path, output_path, is_windows):
        """プロジェクトのnode_modulesからMarp CLIを直接実行する"""
        # プロジェクトルートからの相対パス
        marp_cli_path = os.path.join(settings.BASE_DIR, 'node_modules', '.bin', 'marp')
        
        # Windowsの場合は.cmdファイルを使用
        if is_windows and not os.path.exists(marp_cli_path):
            marp_cli_path = f"{marp_cli_path}.cmd"
        
        # パスが存在するか確認
        if not os.path.exists(marp_cli_path):
            print(f"ローカルのMarp CLIが見つかりません: {marp_cli_path}")
            return None
        
        cmd = [
            marp_cli_path,
            markdown_path,
            '--output', output_path,
            '--pptx',
            '--pptx-convert-infix', 'false'
        ]
        
        result = subprocess.run(cmd, check=True, shell=is_windows, capture_output=True)
        print(f"ローカルMarp CLI実行成功: {result.stdout.decode('utf-8', errors='ignore')}")
        
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                return f.read()
        return None
        
    @staticmethod
    def _get_current_date_japanese():
        """現在の日付を日本語形式で取得する"""
        from datetime import datetime
        now = datetime.now()
        return f"{now.year}年{now.month}月{now.day}日"
    
    @staticmethod
    def edit_template_pptx(new_template_path=None):
        """
        テンプレートPPTXファイルを編集する
        
        Args:
            new_template_path (str, optional): 新しいテンプレートファイルのパス
            
        Returns:
            bool: 成功した場合はTrue、失敗した場合はFalse
        """
        try:
            # 新しいテンプレートパスが指定されている場合は、それを使用
            if new_template_path:
                # 既存のテンプレートパス
                target_path = os.path.join(settings.BASE_DIR, 'template.pptx')
                
                # 新しいテンプレートファイルをコピー
                if os.path.exists(new_template_path) and new_template_path != target_path:
                    # バックアップ作成
                    if os.path.exists(target_path):
                        backup_path = os.path.join(settings.BASE_DIR, 'template_backup.pptx')
                        if os.path.exists(backup_path):
                            os.remove(backup_path)
                        shutil.copy2(target_path, backup_path)
                    
                    # 新しいファイルを適用
                    shutil.copy2(new_template_path, target_path)
            
            return True
            
        except Exception as e:
            print(f"テンプレート編集中にエラーが発生しました: {e}")
            return False
    
    @staticmethod
    def get_template_info():
        """
        テンプレートPPTXの情報を取得する
        
        Returns:
            dict: テンプレート情報の辞書
        """
        template_path = os.path.join(settings.BASE_DIR, 'template.pptx')
        
        info = {
            'exists': os.path.exists(template_path),
            'slides': 0,
            'layouts': []
        }
        
        if info['exists']:
            try:
                # ファイルサイズ
                info['size'] = os.path.getsize(template_path) // 1024  # KB単位
                
                # プレゼンテーション情報
                prs = Presentation(template_path)
                info['slides'] = len(prs.slides)
                
                # レイアウト情報
                for i, layout in enumerate(prs.slide_layouts):
                    layout_info = {
                        'id': i,
                        'name': layout.name if hasattr(layout, 'name') and layout.name else f"レイアウト {i+1}"
                    }
                    info['layouts'].append(layout_info)
                
            except Exception as e:
                print(f"テンプレート情報取得中にエラー: {e}")
                info['error'] = str(e)
        
        return info
    
    @staticmethod
    def _create_presentation_with_template(template_path):
        """
        テンプレートからプレゼンテーションオブジェクトを作成する
        
        Args:
            template_path (str, optional): テンプレートファイルのパス
            
        Returns:
            Presentation: python-pptxのプレゼンテーションオブジェクト
        """
        if template_path and os.path.exists(template_path):
            # テンプレートファイルが存在する場合はそれを使用
            return Presentation(template_path)
        else:
            # テンプレートが無い場合は空のプレゼンテーションを作成
            return Presentation()
    
    @staticmethod
    def _analyze_template_layouts(presentation):
        """
        テンプレートのレイアウト情報を分析する
        
        Args:
            presentation (Presentation): プレゼンテーションオブジェクト
            
        Returns:
            dict: レイアウト情報を含む辞書
        """
        layouts = {}
        
        for i, layout in enumerate(presentation.slide_layouts):
            layout_name = layout.name if hasattr(layout, 'name') and layout.name else f"Layout {i}"
            
            # レイアウトタイプを推測
            layout_type = None
            
            # タイトルスライドの特徴を確認
            title_placeholders = 0
            for shape in layout.placeholders:
                if shape.placeholder_format.type == 1:  # 1はタイトル
                    title_placeholders += 1
            
            if "Title" in layout_name or "タイトル" in layout_name:
                layout_type = "title"
            elif title_placeholders == 1 and len(layout.placeholders) <= 3:
                # 通常のコンテンツスライド（タイトルと本文）
                layout_type = "content"
            elif "Picture" in layout_name or "画像" in layout_name:
                layout_type = "picture"
            elif "Comparison" in layout_name or "比較" in layout_name:
                layout_type = "comparison"
            elif "Section" in layout_name or "セクション" in layout_name:
                layout_type = "section"
            else:
                layout_type = "other"
            
            layouts[layout_type if layout_type else i] = {
                'layout': layout,
                'name': layout_name,
                'index': i,
                'placeholders': len(layout.placeholders)
            }
        
        # タイトルレイアウトがない場合は最初のレイアウトを使用
        if 'title' not in layouts and len(presentation.slide_layouts) > 0:
            layouts['title'] = {
                'layout': presentation.slide_layouts[0],
                'name': "First Layout (as Title)",
                'index': 0,
                'placeholders': len(presentation.slide_layouts[0].placeholders)
            }
        
        return layouts 