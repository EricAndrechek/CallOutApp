from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)


@app.route('/')
def landing():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        phone = request.form.get('phone')
        password = request.form.get('password')
        # check for phone in database and it it exists check if password matches
        # account = dbc(phone, password)
        account = False
        if account:  # if account exists is True, else False
            return redirect("dashboard")
        else:
            return render_template("login.html", error="Incorrect username or password<br>")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == "GET":
        return redirect('login')
    elif request.method == "POST":
        return render_template("dashboard.html")


if __name__ == '__main__':
    app.run()
