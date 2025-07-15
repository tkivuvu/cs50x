import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = session["user_id"]
    user_1 = db.execute("SELECT * FROM users WHERE id = ?", user)
    username = user_1[0]["username"]
    stocks_owned = db.execute(
        "SELECT stock_symbol, sum(shares_bought) as shares_bought, sum(shares_sold) as shares_sold, sum(purchase_price) as purchase_price, stock_name from stock_transactions where username = ? group by stock_symbol",
        username
    )
    shares_times_price = 0
    total_stocks_value = 0
    results = []
    for items in stocks_owned:
        stock_symbol = items["stock_symbol"]
        quote_data = lookup(stock_symbol)
        stock_symbol = quote_data["symbol"]
        current_price = quote_data["price"]
        stock_name = items["stock_name"]
        shares_bought = items["shares_bought"]
        shares_sold = items["shares_sold"]
        shares = shares_bought - shares_sold
        shares_times_price = shares * current_price

        total_stocks_value += shares_times_price
        stock_data = {
            "name": stock_name,
            "symbol": stock_symbol,
            "shares": shares,
            "total_value": shares_times_price,
            "current_price": current_price
        }
        if shares > 0:
            results.append(stock_data)

    cash = db.execute("SELECT cash from users WHERE username = ?", username)
    current_balance = cash[0]["cash"]
    total_value = current_balance + total_stocks_value

    return render_template(
        "index.html", stocks=results, current_balance=current_balance, total_value=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        quote_data = lookup(stock_symbol)
        if not stock_symbol:
            return apology("you have not provided a stock name", 400)
        elif quote_data is None:
            return apology("the stock provided does not exist", 400)
        try:
            shares = request.form.get("shares")
            shares = int(shares)
            if shares < 1:
                return apology("must provide a positive number", 400)
        except ValueError:
            return apology("must provide a positive integer", 400)
        user = session["user_id"]
        user_1 = db.execute("SELECT * FROM users WHERE id = ?", user)
        user_cash = user_1[0]["cash"]
        user_name = user_1[0]["username"]
        stock_price = quote_data["price"]
        stock_name = quote_data["name"]
        stock_symbol = quote_data["symbol"]
        total_cost = stock_price * shares
        if total_cost < user_cash:
            user_cash = user_cash - total_cost
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash, user)
            db.execute(
                "INSERT INTO stock_transactions (username, stock_name, stock_symbol, purchase_price, shares_bought, bought_or_sold, date_time) Values (?, ?, ?, ?, ?, ?, datetime('now'))",
                user_name, stock_name, stock_symbol, total_cost, shares, 1)
            return redirect("/")
        else:
            return apology("there must be enough funds in your account", 400)
    else:
        total_cost = None
        return render_template("buy.html", total_cost=total_cost)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_info[0]["username"]
    stock_info = db.execute("SELECT * FROM stock_transactions WHERE username = ?", username)
    result = []
    for items in stock_info:
        bought_sold = items["bought_or_sold"]
        stock_name = items["stock_name"]
        stock_symbol = items["stock_symbol"]
        purchase_price = items["purchase_price"]
        sale_price = items["sale_price"]
        shares_bought = items["shares_bought"]
        shares_sold = items["shares_sold"]
        date_time = items["date_time"]
        if bought_sold == 1:
            bought_sold = "Bought"
        elif bought_sold == 2:
            bought_sold = "Sold"

        stock_data = {
            "bought_sold": bought_sold,
            "name": stock_name,
            "symbol": stock_symbol,
            "purchase_price": purchase_price,
            "sale_price": sale_price,
            "shares_bought": shares_bought,
            "shares_sold": shares_sold,
            "date_time": date_time
        }
        result.append(stock_data)
    return render_template("history.html", result=result)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        quote_data = lookup(stock_symbol)
        if not stock_symbol:
            return apology("must include stock symbol", 400)
        elif quote_data is None:
            return apology("stock symbol provided does not exist", 400)
        elif quote_data:
            return render_template("quoted.html", quote_data=quote_data)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        username1 = db.execute("SELECT username FROM users WHERE username = ?", username)
        if not username:
            return apology("must provide username", 400)
        for row in username1:
            if row["username"] == username:
                return apology("username already exists", 400)
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must provide confirmation of password", 400)
        elif password != confirmation:
            return apology("password and confirmation do not match", 400)
        password_h = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) Values (?, ?)", username, password_h)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        user_id = session["user_id"]
        user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        username = user_info[0]["username"]
        stock_info = db.execute(
            "SELECT stock_symbol, sum(shares_bought) as shares from stock_transactions WHERE username = ? GROUP BY stock_symbol HAVING sum(shares_bought) - sum(shares_sold) > 0",
            username)
        stock_symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        shares = int(shares)
        for items in stock_info:
            stock_s = items["stock_symbol"]
            stock_shares = items["shares"]
            if not stock_symbol:
                return apology("you have to select a stock in the menu options", 400)
            elif stock_symbol is None:
                return apology("you do not own any shares of this stock", 400)
            elif shares > stock_shares:
                return apology("you are trying to sell more shares of this stock than you own", 400)
            elif stock_symbol == stock_s:
                user_cash = user_info[0]["cash"]
                stock_data = lookup(stock_symbol)
                sold_stock_price = stock_data["price"]
                stock_name = stock_data["name"]
                stock_symbol1 = stock_data["symbol"]
                updated_user_cash = (sold_stock_price * shares) + user_cash
                sale_price_with_shares = sold_stock_price * shares
                db.execute(
                    "UPDATE users SET cash = ? WHERE username = ?", updated_user_cash, username
                )
                db.execute(
                    "INSERT INTO stock_transactions (username, stock_name, stock_symbol, sale_price, shares_sold, bought_or_sold, date_time) Values (?, ?, ?, ?, ?, ?, datetime('now'))",
                    username, stock_name, stock_symbol1, sale_price_with_shares, shares, 2)
                return redirect("/")
    else:
        user_id = session["user_id"]
        user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        username = user_info[0]["username"]
        stock_info = db.execute(
            "SELECT stock_symbol from stock_transactions WHERE username = ? GROUP BY stock_symbol HAVING sum(shares_bought) - sum(shares_sold) > 0",
            username)
        for items in stock_info:
            pass
        return render_template("sell.html", stock_info=stock_info)


@app.route("/cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        try:
            new_cash = request.form.get("cash")
            new_cash = float(new_cash)
            user_id = session["user_id"]
            user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            username = user_info[0]["username"]
            user_cash = user_info[0]["cash"]
            new_cash = new_cash + user_cash
            if new_cash <= 0:
                return apology("must add more than zero", 403)
        except ValueError:
            return apology("must provide a positive number", 403)

        db.execute(
            "UPDATE users SET cash = ? WHERE username = ?",
            new_cash, username
        )
        return redirect("/")
    return render_template("cash.html")
