from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure mail settings for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'industrialcomputervision@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = ''  # Your Gmail password

mail = Mail(app)

@app.route('/')
def index():
    return render_template('mail.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = request.form['subject']
        message_body = request.form['message']

        msg = Message(subject, sender='industrialcomputervision@gmail.com', recipients=[recipient])
        msg.body = message_body

        try:
            mail.send(msg)
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Failed to send email. Error: {str(e)}', 'error')

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
