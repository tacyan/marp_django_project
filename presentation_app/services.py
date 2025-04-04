"""
Marp CLIを操作するサービスモジュール

このモジュールは、Marp CLIを使用してMarkdownをプレゼンテーション形式に変換する機能を提供します。
"""

import os
import subprocess
import tempfile
import platform
import shutil
from django.conf import settings

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