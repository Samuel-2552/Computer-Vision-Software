import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon 
from flask import Flask, render_template, redirect, request, send_file
from werkzeug.serving import WSGIRequestHandler
import signal
import sqlite3
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
import uuid
import datetime
import wmi
import requests
import mimetypes
import cv2

def encrypt_message(message, key):
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()
    return decrypted_message

def get_system_id():
    try:
        # Connect to Windows Management Instrumentation (WMI)
        c = wmi.WMI()
        # System UUID (Universally Unique Identifier)
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    return system_info

def get_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.endswith(('.mp4', '.avi', '.mkv', '.ts')):
            files.append({'name': file, 'type': 'video'})
        elif file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            files.append({'name': file, 'type': 'image'})
    return files

frame_count = 0
def extract_frames(video_path, output_folder, interval_seconds):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    global frame_count
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get the frames per second (fps) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the number of frames to skip based on the interval_seconds
    frames_to_skip = fps * interval_seconds
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Save the frame every 'frames_to_skip' frames
        if frame_count % frames_to_skip == 0:
            frame_filename = os.path.join(output_folder, f"frame_{frame_count // frames_to_skip:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
        
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Frames extracted and saved from {video_path} to {output_folder}")

def mail_config():
    # Create or connect to SQLite database
    conn = sqlite3.connect('email.db')
    cursor = conn.cursor()

    # Retrieve encrypted credentials from the database
    cursor.execute("SELECT username, password, key, initial FROM email WHERE id = 1")
    result = cursor.fetchone()
    stored_username, stored_password, key, intial_val = result
    
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
        
        @self.flask_app.route('/home', methods=['POST'])
        def initial():
            if request.method == 'POST':
                name = request.form['name']
                email = request.form['email']
                company = request.form['company']
                designation = request.form['designation']
                phone = request.form['phone']
                # Get the current date and time
                current_time = str(datetime.datetime.now())
                sys_id = get_system_id()
                user_data = {'sys_id': sys_id, 'name': name, 'email': email, 'company': company, 'designation': designation, 'phone': phone, 'account_created': current_time}
                web_server_url = 'https://icvs.pythonanywhere.com//receive-user-data'  # Replace with your web server URL
                response = requests.post(web_server_url, json=user_data)
                # Process the response from the web server if needed
                if response.status_code == 200:
                    print("User data sent successfully to the web server")
                    print(response)
                    try:
                        recipient = 'industrialcomputervision@gmail.com'
                        subject = f'New User System Id : {sys_id}'
                        message_body = f'''
                                Name: {name}
                                Email id: {email}
                                Company name: {company}
                                Designation: {designation}
                                Phone No: {phone}
                                Created On: {current_time}
                            '''
                        msg = Message(subject, sender='printease2023@gmail.com', recipients=[recipient])
                        msg.body = message_body
                        mail.send(msg)
                        print('Email sent successfully!', 'success')
                        # Update the 'email' table (to send the details as email during initial setup for back up)
                        with sqlite3.connect('email.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE email
                                            SET initial = 1
                                            WHERE id = 1
                                        ''')
                            conn.commit()
                    except Exception as e:
                        print(f'Failed to send email. Error: {str(e)}', 'error')
                else:
                    print(response)
                    print("Failed to send user data to the web server", 500)   
            return redirect('/')
        
        # Change the route to serve index.html
        @self.flask_app.route("/")
        def index():
            user_data = {'sys_id': get_system_id()}
            web_server_url = 'https://icvs.pythonanywhere.com//check-sys-id'  # Replace with your web server URL
            response = requests.post(web_server_url, json=user_data)
            if response.status_code == 200:
                val=response.json().get('exists')
                if val:
                    # Update the 'email' table (to send the details as email during initial setup for back up)
                    with sqlite3.connect('email.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE email
                                        SET initial = 1
                                        WHERE id = 1
                                    ''')
                        conn.commit()
            # Establish connection to the database
            conn = sqlite3.connect('email.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT initial
                            FROM email
                            WHERE id = 1;
                            ''')
            result = cursor.fetchone()      
            conn.close()  
            # Make sure to import send_file from flask
            return render_template('index.html', result=result[0])
        
        @self.flask_app.route("/select_directory", methods=['GET'])
        def select_directory():
            directory = QFileDialog.getExistingDirectory(None, "Select Project Directory", options=QFileDialog.ShowDirsOnly)
            if directory:
                return f"{directory}"
            return ""
        
        @self.flask_app.route("/new_project")
        def new_project():
            return render_template('new_project.html')
        
        @self.flask_app.route("/existing_project")
        def existing_project():
            sys_id = get_system_id()
            user_data = {'sys_id': sys_id}
            web_server_url = 'https://icvs.pythonanywhere.com/get-project'  # Replace with your web server URL
            response = requests.post(web_server_url, json=user_data)
            if response.status_code == 200:
                val=response.json().get('project')
            else:
                return "Check your Internet Connection"
            return render_template('existing_project.html', project=val, datetime=datetime)
        
        @self.flask_app.route("/productKey")
        def productKey():
            return render_template('productKey.html')
        
        @self.flask_app.route('/projects/<int:project_id>')
        def project_details(project_id):
            sys_id = get_system_id()
            user_data = {'sys_id': sys_id}
            web_server_url = 'https://icvs.pythonanywhere.com/get-project'  # Replace with your web server URL
            response = requests.post(web_server_url, json=user_data)
            if response.status_code == 200:
                val=response.json().get('project')
                details  = val[project_id-1]
                print(details)
                self.folder_path = details[6]  # Replace with your folder path containing video and image files
                video_files = [file for file in get_files(self.folder_path) if file['type'] == 'video']
                image_files = [file for file in get_files(self.folder_path) if file['type'] == 'image']
            else:
                return "Check your Internet Connection!"
            return render_template('start.html', details=details,  videos=video_files, images=image_files)
        
        @self.flask_app.route('/projects/images/<string:file_name>')
        def image_files(file_name):
            image_path = os.path.join(self.folder_path, file_name)
            return send_file(image_path, mimetype='image/jpeg')
        
        @self.flask_app.route('/projects/videos/<string:file_name>')
        def video_files(file_name):
            video_path = os.path.join(self.folder_path, file_name)
            mimetype, _ = mimetypes.guess_type(video_path)
            if not mimetype:
                mimetype = 'application/octet-stream'
            print(mimetype)
            return send_file(video_path, mimetype='video/mp4')
        
        @self.flask_app.route("/process_video", methods=['GET', 'POST'])
        def process_video():
            global frame_count
            frame_count = 0
            if request.method == 'POST':
                #recieve json file
                # no_frames=
                # project_id= 
                # project_directory =
                # dataset_directory =
                video_folder = "dataset_directory"
                output_folder = "project_directory" + "/dataset/images"
                interval_seconds = "no_frames"

                # Create the output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)
                for video_filename in os.listdir(video_folder):
                    if video_filename.endswith(".mkv") or video_filename.endswith(".mp4") or video_filename.endswith(".ts") or video_filename.endswith(".avi"):
                        video_path = os.path.join(video_folder, video_filename)
                        extract_frames(video_path, output_folder, interval_seconds)

            return "as per your requirement"

        @self.flask_app.route("/project", methods=['GET', 'POST'])
        def project():
            if request.method == 'POST':
                project_name = request.form['projectName']
                project_location = request.form['projectLocation']
                project_type = request.form['projectType']
                dataset_location = request.form['videoLocation']
                sys_id = get_system_id()
                user_data = {'sys_id': sys_id}
                web_server_url = 'https://icvs.pythonanywhere.com/check-project-count'  # Replace with your web server URL
                response = requests.post(web_server_url, json=user_data)
                if response.status_code == 200:
                    val=response.json().get('project_count')
                    val +=1
                    project_id = val
                    if project_id==1:
                        license_start = str(datetime.datetime.now())
                        # Calculate three months ahead
                        three_months = datetime.timedelta(days=90)  # Assuming a month has 30 days for simplicity
                        license_end = datetime.datetime.now() + three_months
                        license_end = str(license_end)
                    else:
                        license_start = str(datetime.datetime.now())
                        license_end = license_start
                    project_data = {'sys_id': sys_id, 'project_id': project_id, 'project_name': project_name, 'project_location': project_location, 'project_type': project_type, 'dataset_location': dataset_location, 'license_start': license_start, 'license_end': license_end}
                    web_server_url = 'https://icvs.pythonanywhere.com//project-data'  # Replace with your web server URL
                    project_response = requests.post(web_server_url, json=project_data)
                    # Process the project_response from the web server if needed
                    if project_response.status_code == 200:
                        print("Project data sent successfully to the web server")
                        print(project_response.json())
                        return redirect("/existing_project")
                    else:
                        print("Failed to send Project data to the web server", 500)
                        return "Check your internet connection and Try again"
                else:
                        print("Failed to send Project data to the web server", 500)
                        return "Check your internet connection and Try again"
            return render_template('project.html')
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
        self.browser.loadFinished.connect(self.inject_disable_context_menu)
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
        # # Add a "Select Project Directory" action to the "File" menu
        # selectProjectDirAction = QAction('Select Project Directory', self)
        # selectProjectDirAction.triggered.connect(self.select_project_directory)
        # fileMenu.addAction(selectProjectDirAction)
        # # Add a separator
        # fileMenu.addSeparator()
        # Add a separator
        fileMenu.addSeparator()
        # Add an "Exit" action to the "File" menu
        exitAction = QAction(QIcon('static/img/exit.png'), 'Exit', self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        # Create a "Activate License" menu
        activate = menubar.addMenu('License')
        productKey = QAction(QIcon('static/img/key.png'), 'Product Key', self)
        productKey.triggered.connect(self.product_key)
        activate.addAction(productKey)
        productKey = QAction(QIcon('static/img/price.png'), 'Pricing and Plans', self)
        productKey.triggered.connect(self.pricing)
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

    def pricing(self):
        # Redirect to the Flask route for product key
        self.browser.setUrl(QUrl("http://127.0.0.1:54321/pricing"))

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

    def select_project_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory", options=options)
        
        if directory:
            self.store_directory_in_database(directory)
            QMessageBox.information(self, "Project Directory Selected", f"Directory selected: {directory}")
            print(directory)

    def store_directory_in_database(self, directory):
        try:
            # self.cursor.execute("INSERT INTO ProjectDirectories (directory_path) VALUES (?)", (directory,))
            # self.conn.commit()
            print("hi")
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Industrial Computer Vision Software")
    window = Browser()
    window.showMaximized()
    sys.exit(app.exec_())
