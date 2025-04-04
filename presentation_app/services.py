"""
Marp CLIを操作するサービスモジュール

このモジュールは、Marp CLIを使用してMarkdownをプレゼンテーション形式に変換する機能を提供します。
"""

import os
import subprocess
import tempfile
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
        
        # Marp CLIを実行してPPTXを生成
        # Marp CLI v4.1.0以降で--pptx-convert-infix falseオプションを使用して編集可能なPPTXを生成
        cmd = [
            'npx', '@marp-team/marp-cli',
            markdown_path,
            '--output', output_path,
            '--pptx',
            '--pptx-convert-infix', 'false'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            
            # 生成されたPPTXファイルを読み込む
            with open(output_path, 'rb') as f:
                pptx_content = f.read()
                
            # 一時ファイルを削除
            os.remove(markdown_path)
            os.remove(output_path)
            os.rmdir(temp_dir)
            
            return pptx_content
        except subprocess.CalledProcessError as e:
            # エラーハンドリング
            print(f"Marp CLI実行エラー: {e}")
            return None
        except Exception as e:
            print(f"予期せぬエラー: {e}")
            return None 