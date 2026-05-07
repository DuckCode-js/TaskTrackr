import threading
import webview
from app import app

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    webview.create_window('TaskTrackr', 'http://127.0.0.1:5000', width=1100, height=750)
    webview.start()
