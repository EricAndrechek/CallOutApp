from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def landing():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == "GET":
        return redirect('login')
    elif request.method == "POST":
        return render_template("dashboard.html")


if __name__ == '__main__':
    app.run()
