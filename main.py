from flask import Flask, render_template, request, redirect, session
import re

app = Flask(__name__)


def dbcheck(phone, password):
    return True
    # check for phone and password in database


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
        account = dbcheck(phone, password)
        if account:  # if account exists is True, else False
            return redirect("dashboard")
        else:
            return render_template("login.html", error="Incorrect username or password<br>")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if name is not None and email is not None and phone is not None and password is not None and password2 is not None:
            if password == password2:
                emailregex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
                if emailregex.match(email) is not None:
                    nameregex = re.compile(r"^[A-Za-z' ,.-]+$")
                    if nameregex.match(name) is not None:
                        phoneregex = re.compile(r"^[0-9]{10}$")
                        if phoneregex.match(phone) is not None:
                            passwordregex = re.compile(r'^[A-Za-z0-9!@#$%_=+.?-]{8,}$')
                            if passwordregex.match(password) is not None:
                                return "Test"
                            else:
                                return render_template("signup.html", error="Your password includes characters not allowed or is not at least 8 characters<br>")
                        else:
                            return render_template("signup.html", error="Your phone includes characters not allowed, type it using only numbers<br>")
                    else:
                        return render_template("signup.html", error="Your name includes characters not allowed<br>")
                else:
                    return render_template("signup.html", error="Your email appears to be invalid<br>")
            else:
                return render_template("signup.html", error="Your passwords don't match<br>")
        else:
            return render_template("signup.html", error="None of your fields can be blank<br>")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == "GET":
        return redirect('login')
    elif request.method == "POST":
        return render_template("dashboard.html")


if __name__ == '__main__':
    app.run()
