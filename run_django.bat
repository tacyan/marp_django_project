@echo off
echo Django開発サーバーを起動します...
call .\env\Scripts\activate.bat
pip install python-pptx
python manage.py runserver
pause 