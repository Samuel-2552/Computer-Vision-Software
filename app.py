import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from flask import Flask
from werkzeug.serving import WSGIRequestHandler
import signal

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

class FlaskThread(QThread):
    def run(self):
        # Create Flask app and set the request handler to WSGIRequestHandler
        self.flask_app = Flask(__name__)
        self.flask_app.route("/")(lambda: "Hello from Flask!")
        self.flask_app.run(host='127.0.0.1', port=5000, threaded=True, request_handler=WSGIRequestHandler)

class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Start Flask app in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

        # Set the URL to the Flask app
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))

        # Connect the close event of the main window to the stop_flask method
        self.closing.connect(self.stop_flask)

    # Define a custom signal for closing the Flask app
    closing = pyqtSignal()

    def closeEvent(self, event):
        # Emit the closing signal when the main window is closed
        self.closing.emit()
        super().closeEvent(event)

    def stop_flask(self):
        # Stop the Flask server gracefully using a signal
        os.kill(os.getpid(), signal.SIGINT)
        # Wait for the Flask thread to finish
        self.flask_thread.quit()
        self.flask_thread.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Flask Browser")
    window = Browser()
    window.showMaximized()
    sys.exit(app.exec_())
