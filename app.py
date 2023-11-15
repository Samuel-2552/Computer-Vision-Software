import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon  # Import QIcon for adding an icon
from flask import Flask, render_template, redirect
from werkzeug.serving import WSGIRequestHandler
import signal
import sqlite3
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
import uuid

def initial_setup():
    
    conn = sqlite3.connect('email.db')
    cursor = conn.cursor()
    # Create a table to store UUIDs
    cursor.execute('''CREATE TABLE IF NOT EXISTS uuid_table (
                        id INTEGER PRIMARY KEY,
                        uuid_user TEXT NOT NULL,
                        uuid_key TEXT NOT NULL
                    )''')
    # Generate a UUID
    new_uuid = uuid.uuid4()
    product_key = str(new_uuid)  # Convert UUID to string
    new_uuid = uuid.uuid1()
    user_id = str(new_uuid)

    # Insert the UUID into the database
    cursor.execute('''INSERT INTO uuid_table (uuid_user, uuid_key) VALUES (?,?)''', (user_id, product_key,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


    

    return user_id, product_key

    


def decrypt_message(encrypted_message, key):
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()
    return decrypted_message

def mail_config():
    # Create or connect to SQLite database
    conn = sqlite3.connect('email.db')
    cursor = conn.cursor()

    # Retrieve encrypted credentials from the database
    cursor.execute("SELECT username, password, key FROM email WHERE id = 1")
    result = cursor.fetchone()
    stored_username, stored_password, key = result
    
    # Decrypt retrieved credentials
    decrypted_username = decrypt_message(stored_username, key)
    decrypted_password = decrypt_message(stored_password, key)
    conn.close()
        
    return decrypted_username, decrypted_password

    


class FlaskThread(QThread):
    def run(self):
        # Create Flask app and set the request handler to WSGIRequestHandler
        self.flask_app = Flask(__name__)


        # Configure mail settings for Gmail
        
        self.flask_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.flask_app.config['MAIL_PORT'] = 587
        self.flask_app.config['MAIL_USE_TLS'] = True
        self.flask_app.config['MAIL_USE_SSL'] = False

        self.flask_app.config['MAIL_USERNAME'], self.flask_app.config['MAIL_PASSWORD'] = mail_config()

        mail = Mail(self.flask_app)

        @self.flask_app.route('/send_email')
        def send_mail():
            try:
                recipient = '201501043@rajalakshmi.edu.in'
                subject = 'User_Id and Product Key Generated'
                user_id, product_key = initial_setup()
                message_body = f'''
                        User Id: {user_id}
                        Product Key: {product_key}
                    '''

                msg = Message(subject, sender='industrialcomputervision@gmail.com', recipients=[recipient])
                msg.body = message_body
                mail.send(msg)
                print('Email sent successfully!', 'success')
            except Exception as e:
                print(f'Failed to send email. Error: {str(e)}', 'error')
            
            return redirect('/')

        
        
        # Change the route to serve index.html
        @self.flask_app.route("/")
        def index():
            return render_template('index.html')  # Make sure to import send_file from flask
        
        @self.flask_app.route("/try")
        def Try():
            return render_template('try.html')
        
        @self.flask_app.route("/new_project")
        def new_project():
            return render_template('new_project.html')
        
        @self.flask_app.route("/existing_project")
        def existing_project():
            return render_template('existing_project.html')
        
        @self.flask_app.route("/productKey")
        def productKey():
            return render_template('productKey.html')
            
        self.flask_app.run(host='127.0.0.1', port=54321, threaded=True, request_handler=WSGIRequestHandler)

class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()

        # Set the application icon
        self.setWindowIcon(QIcon('static\img\logo.png'))  # Replace 'path_to_your_icon.png' with the actual path to your icon

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Start Flask app in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

        # Set the URL to the Flask app
        self.browser.setUrl(QUrl("http://127.0.0.1:54321"))

        # Connect the close event of the main window to the stop_flask method
        self.closing.connect(self.stop_flask)

        # Connect the loadFinished signal to inject JavaScript after the page is loaded
        # self.browser.loadFinished.connect(self.inject_disable_context_menu)

        # Create a menu bar
        menubar = self.menuBar()
        
        # Create a "File" menu
        fileMenu = menubar.addMenu('File')

        # Add an "New Project" action to the "File" menu
        newProjectAction = QAction(QIcon('static/img/new.png'), 'New Project', self)
        newProjectAction.triggered.connect(self.open_new_project)
        fileMenu.addAction(newProjectAction)

        # Add an "Existing Project" action to the "File" menu
        existingProjectAction = QAction(QIcon('static/img/exist.png'), 'Existing Project', self)
        existingProjectAction.triggered.connect(self.open_existing_project)
        fileMenu.addAction(existingProjectAction)

        # Add a separator
        fileMenu.addSeparator()
        
        # Add an "Exit" action to the "File" menu
        exitAction = QAction(QIcon('static/img/exit.png'), 'Exit', self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)


        # Create a "Activate License" menu
        activate = menubar.addMenu('Activate License')

        productKey = QAction(QIcon('static/img/key.png'), 'Product Key', self)
        productKey.triggered.connect(self.product_key)
        activate.addAction(productKey)

    # Define a custom signal for closing the Flask app
    closing = pyqtSignal()

    def open_new_project(self):
        # Redirect to the Flask route for new project
        self.browser.setUrl(QUrl("http://127.0.0.1:54321/new_project"))

    def open_existing_project(self):
        # Redirect to the Flask route for existing project
        self.browser.setUrl(QUrl("http://127.0.0.1:54321/existing_project"))

    def product_key(self):
        # Redirect to the Flask route for product key
        self.browser.setUrl(QUrl("http://127.0.0.1:54321/productKey"))

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

    def inject_disable_context_menu(self, ok):
        if ok:
            # Inject JavaScript to disable the context menu when the webpage is loaded
            script = """
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
            });
            """
            self.browser.page().runJavaScript(script)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Industrial Computer Vision Software")
    window = Browser()
    window.showMaximized()
    sys.exit(app.exec_())
