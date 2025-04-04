# セットアップと操作手順

## セットアップ手順

1. 必要な環境のインストール

```bash
# Python 3.12.6（推奨）のインストール
# https://www.python.org/downloads/release/python-3126/ からダウンロードしてインストール

# Djangoのインストール
pip install Django

# Marp CLIのインストール
npm install @marp-team/marp-cli
```

2. データベースのマイグレーション

```bash
# マイグレーションファイルの作成
python manage.py makemigrations presentation_app

# マイグレーションの実行
python manage.py migrate
```

3. 管理者ユーザーの作成

```bash
python manage.py createsuperuser
```

画面の指示に従って、ユーザー名、メールアドレス、パスワードを入力してください。

4. 開発サーバーの起動

```bash
python manage.py runserver
```

## 使用方法

1. ブラウザで http://127.0.0.1:8000 にアクセス
2. 管理者ログイン画面が表示されるので、作成した管理者ユーザーでログイン
3. プレゼンテーション一覧画面が表示されます

### 新規プレゼンテーション作成

1. 「新規作成」ボタンをクリック
2. タイトル、テーマを選択し、内容をマークダウン形式で入力
3. 「保存」ボタンをクリック

### プレゼンテーションの編集

1. プレゼンテーション一覧から「編集」ボタンをクリック
2. 編集画面で内容を修正
3. 「保存」ボタンをクリック

### PPTXファイルのダウンロード

1. 編集画面または一覧画面から「PPTXダウンロード」ボタンをクリック
2. 編集可能なPowerPointファイルがダウンロードされます

## トラブルシューティング

### Marp CLIの実行エラー

エラーメッセージ: "PPTX生成に失敗しました"

解決策:

1. Node.jsとnpmが正しくインストールされているか確認
2. Marp CLIのインストール状態を確認: `npx @marp-team/marp-cli --version`
3. package.jsonが正しく設定されているか確認

### ログインできない場合

1. 管理者ユーザーが正しく作成されているか確認
2. パスワードをリセットする場合: `python manage.py changepassword ユーザー名`

### データベースエラー

1. マイグレーションが正しく実行されているか確認: `python manage.py showmigrations`
2. 必要に応じてデータベースをリセット:
   - db.sqlite3ファイルを削除
   - マイグレーションファイルを削除: `presentation_app/migrations/0*.py`
   - マイグレーションを再実行: `python manage.py makemigrations presentation_app && python manage.py migrate`
