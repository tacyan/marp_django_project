# Marp Django プレゼンテーション作成ツール

Djangoフレームワークを使用して、Marp CLIベースのプレゼンテーション作成・管理システムを実装したWebアプリケーションです。

## 機能

- マークダウン形式でプレゼンテーションを作成
- 複数のMarpテーマから選択可能
- リアルタイムプレビュー機能
- 編集可能なPowerPointファイル（PPTX）の出力
- ユーザー認証によるプレゼンテーション管理

## インストール方法

### 前提条件

- Python 3.12.6（推奨）
- Node.js 14.0以上
- npm 6.0以上

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/marp-django-project.git
cd marp-django-project
```

2. Python依存関係のインストール

```bash
pip install -r requirements.txt
```

3. Node.js依存関係のインストール

```bash
npm install
```

4. データベースマイグレーション

```bash
python manage.py migrate
```

5. 管理者ユーザーの作成

```bash
python manage.py createsuperuser
```

6. 開発サーバーの起動

```bash
python manage.py runserver
```

その後、ブラウザで http://127.0.0.1:8000 にアクセスし、作成した管理者ユーザーでログインしてください。

## 使用方法

1. ログイン後、「新規作成」ボタンをクリックしてプレゼンテーションを作成
2. マークダウン形式でスライドを記述（新しいスライドは`---`で区切ります）
3. テーマを選択して保存
4. 「PPTXをダウンロード」ボタンをクリックして編集可能なPowerPointファイルを取得

## Marpディレクティブ

プレゼンテーションのマークダウン内で、以下のようなMarpディレクティブを使用できます：

```markdown
---
marp: true
theme: default
paginate: true
---

# タイトルスライド

---

## 2枚目のスライド
```

## 技術スタック

- Django: Webフレームワーク
- Marp CLI: マークダウンからプレゼンテーションファイルへの変換
- Bootstrap: UIフレームワーク
- marked.js: ブラウザ上でのマークダウンプレビュー

## ライセンス

MITライセンス 