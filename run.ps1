Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py