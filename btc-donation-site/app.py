from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ipn", methods=["POST"])
def ipn():
    data = request.json
    print("?? IPN Received:", data)
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
