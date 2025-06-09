from flask_mail import Mail, Message

# Existing code setup above this...
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail.init_app(app)

def send_confirmation_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)



from flask_mail import Mail, Message
mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    msg = Message("Thank You for Your Donation!",
                  recipients=[data['email']])
    msg.html = render_template("email_receipt.html", name=data['name'], amount=data['amount'], method=data['method'])
    mail.send(msg)
    return jsonify({"status": "sent"})


