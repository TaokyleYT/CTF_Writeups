from flask import Flask, request, session
app = Flask(__name__)
app.secret_key = "4DB19C59E8999B612CBF57CBE0E841AB"

@app.get("/")
def login():
    session["user"] = "OwO"
    return request.cookies.get("session"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)