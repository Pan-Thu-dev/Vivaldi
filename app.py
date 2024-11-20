from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
import os
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import send_email, login_required, convert_currency, get_currency_symbol, init_helpers

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)
app.jinja_env.globals.update(get_currency_symbol=get_currency_symbol)
app.jinja_env.globals.update(convert_currency=convert_currency)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'panthu252004@gmail.com'
app.config['MAIL_PASSWORD'] = 'tbtk aqsa gvga wurt '
app.config['MAIL_DEFAULT_SENDER'] = 'panthu252004@gmail.com'

db = SQLAlchemy(app)

# Initialize Flask-Mail
init_helpers(app)


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    confirmation_code = db.Column(db.String(10), nullable=True)
    password_reset_code = db.Column(db.String(10), nullable=True)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=db.func.current_timestamp())


# routes
@app.route("/")
@login_required
def index():
    """Display homepage"""
    user = User.query.get(session["user_id"])

    # Calculate total deposits and withdrawals for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query for deposits and withdrawals for the current month
    total_deposits = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'deposit',
        db.extract('month', Transaction.date) == current_month,
        db.extract('year', Transaction.date) == current_year
    ).scalar() or 0

    total_withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'withdrawal',
        db.extract('month', Transaction.date) == current_month,
        db.extract('year', Transaction.date) == current_year
    ).scalar() or 0  # Default to 0 if no results

    # Calculate the interest rate
    base_rate = 1.3  # Base interest rate of 1.3%
    balance_factor = 0.0001  # 0.0001% for each $10000 in balance
    withdraw_penalty_factor = 0.0002  # 0.0002% for each $5000 withdraw
    deposit_bonus_factor = 0.0003  # 0.0003% for each 10000 deposit

    # Balance Contribution
    balance_contribution = (user.balance / 10000) * balance_factor

    # Penalty for Withdrawals
    withdraw_penalty = (total_withdrawals / 5000) * withdraw_penalty_factor

    # Deposit Bonus
    deposit_bonus = (total_deposits / 10000) * deposit_bonus_factor

    # Total interest rate
    interest_rate = base_rate + balance_contribution - withdraw_penalty + deposit_bonus

    # calulated interest
    interest = (user.balance * interest_rate) / 100

    return render_template(
        "index.html",
        user=user,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        interest=interest,
        session_start_time=session.get("start_time"),
        session_lifetime=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(
        )
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.is_active and check_password_hash(user.password, password):
            session.permanent = True
            session["user_id"] = user.id
            session["start_time"] = datetime.now(timezone.utc).isoformat()
            flash("Logged in successfully.")
            return redirect(url_for("index"))
        elif user and not user.is_active:
            flash("Your account is not activated. Please activate your account.")
            return redirect(url_for("login"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    session.pop("user_id", None)
    session.pop("start_time", None)
    if request.args.get("expired") == "true":
        flash("Your session has expired. Please log in again.")
    else:
        flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not email or not username or not password:
            flash("All fields are required.")
            return redirect(url_for("signup"))
        if not re.match(email_regex, email):
            flash("Invalid email format.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        if User.query.filter_by(email=email).first():
            flash("Email is already registered. Please Log in.")
            return redirect(url_for("login"))
        if User.query.filter_by(username=username).first():
            flash("Username is already used.")
            return redirect(url_for("signup"))

        # Generate a confirmation code
        confirmation_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=6))

        # Create new user (inactive by default)
        new_user = User(
            email=email, username=username, password=hashed_password,
            is_active=False, confirmation_code=confirmation_code
        )
        db.session.add(new_user)
        db.session.commit()

        # Send confirmation code to email
        send_email(
            email,
            "Account Confirmation",
            f"Your confirmation code is: {confirmation_code}"
        )

        flash("A confirmation code has been sent to your email.")
        return redirect(url_for("activate_account"))

    else:
        return render_template("signup.html")


@app.route("/activate", methods=["GET", "POST"])
def activate_account():
    if request.method == "POST":
        email = request.form.get("email")
        confirmation_code = request.form.get("confirmation_code")

        user = User.query.filter_by(email=email).first()

        if user and user.confirmation_code == confirmation_code:
            user.is_active = True
            user.confirmation_code = None
            db.session.commit()
            flash("Your account has been activated.")
            return redirect(url_for("login"))
        else:
            flash("Invalid email or confirmation code.")

    else:
        return render_template("activate.html")


@app.route("/request-reset", methods=["GET", "POST"])
def request_reset():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            reset_code = ''.join(random.choices(
                string.ascii_letters + string.digits, k=6))
            user.password_reset_code = reset_code
            db.session.commit()

            send_email(
                email,
                "Password Reset Request",
                f"Your password reset code is: {reset_code}"
            )
            flash("A password reset code has been sent to your email.")
            return redirect(url_for("reset_password"))
        else:
            flash("Email not found.")

    else:
        return render_template("request_reset.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        code = request.form.get("code")
        new_password = generate_password_hash(request.form.get("password"))

        user = User.query.filter_by(
            email=email, password_reset_code=code).first()

        if user:
            user.password = new_password
            user.password_reset_code = None
            db.session.commit()
            session.pop("user_id", None)
            flash("Your password has been updated. You can now log in.")
            return redirect(url_for("login"))
        else:
            flash("Invalid email or reset code.")
            return redirect(url_for("login"))

    else:
        return render_template("reset_password.html")


@app.route("/close_account", methods=["GET", "POST"])
@login_required
def close_account():
    """Close the user's account with a password confirmation step"""
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        password = request.form.get("password")

        if check_password_hash(user.password_hash, password):
            # Delete all transactions associated with the user
            Transaction.query.filter_by(user_id=user.id).delete()

            # Delete the user account
            db.session.delete(user)
            db.session.commit()

            flash("Your account has been successfully closed.", "success")
            return redirect(url_for("logout"))
        else:
            flash("Incorrect password. Account closure canceled.", "danger")
            return redirect(url_for("close_account"))

    return render_template("close_account.html")


@app.route("/transaction")
@login_required
def transaction():
    """Display perform transaction page"""
    return render_template(
        "transaction.html",
        user=User.query.get(session["user_id"]),
        session_start_time=session.get("start_time"),
        session_lifetime=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(
        )
    )


@app.route("/transaction/deposit", methods=["POST"])
@login_required
def deposit():
    """Handle deposit transactions"""
    amount = float(request.form.get("amount"))
    if amount <= 0:
        flash("Please enter a valid deposit amount.")
        return redirect(url_for("deposit"))

    user = User.query.get(session["user_id"])
    converted_amount = convert_currency(amount, user.currency, "USD")
    user.balance += converted_amount
    new_transaction = Transaction(
        user_id=user.id, amount=converted_amount, transaction_type="deposit"
    )
    db.session.add(new_transaction)
    db.session.commit()

    flash(f"{get_currency_symbol(user.currency)}{
          amount:.2f} deposited successfully.")
    return redirect(url_for("index"))


@app.route("/transaction/withdraw", methods=["POST"])
@login_required
def withdraw():
    """Handle withdrawal transactions"""
    amount = float(request.form.get("amount"))
    user = User.query.get(session["user_id"])
    if amount <= 0:
        flash("Please enter a valid withdrawal amount.")
        return redirect(url_for("withdraw"))
    if amount > user.balance:
        flash("Insufficient balance.")
        return redirect(url_for("withdraw"))

    converted_amount = convert_currency(amount, user.currency, "USD")
    user.balance -= converted_amount
    new_transaction = Transaction(
        user_id=user.id, amount=converted_amount, transaction_type="withdrawal"
    )
    db.session.add(new_transaction)
    db.session.commit()

    flash(f"{get_currency_symbol(user.currency)}{
          amount:.2f} withdrawn successfully.")
    return redirect(url_for("index"))


@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    """Transfer money to another user"""
    if request.method == "POST":
        sender = User.query.get(session["user_id"])
        recipient_username = request.form.get("recipient_username").lower()
        amount = float(request.form.get("amount"))
        converted_amount = convert_currency(amount, sender.currency, "USD")
        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            flash("Recipient does not exist.")
            return redirect(url_for("transfer"))

        if sender.balance < converted_amount:
            flash("Insufficient balance.")
            return redirect(url_for("transfer"))

        if converted_amount is None:
            flash("Currency conversion failed. Please try again later.")
            return redirect(url_for("transfer"))

        # Perform the transfer
        sender.balance -= converted_amount
        recipient.balance += converted_amount

        # Record the transactions
        sender_transaction = Transaction(
            user_id=sender.id, amount=converted_amount, transaction_type="transfer_out"
        )
        recipient_transaction = Transaction(
            user_id=recipient.id, amount=converted_amount, transaction_type="transfer_in"
        )
        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)

        db.session.commit()
        flash(f"Successfully transferred {get_currency_symbol(
            sender.currency)}{amount:.2f} to {recipient_username}.")
        return redirect(url_for("index"))

    else:
        return render_template(
            "transfer.html",
            user=User.query.get(session["user_id"]),
            session_start_time=session.get("start_time"),
            session_lifetime=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(
            )
        )


@app.route("/loan", methods=["GET", "POST"])
@login_required
def loan():
    """Apply for a loan"""
    user = User.query.get(session["user_id"])
    # 20% of the user's balance
    max_loan_amount = user.balance * 0.2
    converted_max_loan_amount = convert_currency(
        max_loan_amount, "USD", user.currency)

    if request.method == "POST":
        loan_amount = float(request.form.get("loan_amount"))

        converted_loan_amount = convert_currency(
            loan_amount, user.currency, "USD")

        if converted_loan_amount > max_loan_amount:
            flash(f"Loan amount exceeds the maximum allowable limit of {get_currency_symbol(user.currency)}{
                  converted_max_loan_amount:.2f}.")
            return redirect(url_for("loan"))

        # Add the loan amount to the user's balance
        user.balance += converted_loan_amount

        # Record the transaction
        loan_transaction = Transaction(
            user_id=user.id, amount=converted_loan_amount, transaction_type="loan"
        )
        db.session.add(loan_transaction)

        db.session.commit()
        flash(f"Loan of {get_currency_symbol(user.currency)}{
              loan_amount:.2f} has been successfully approved and added to your balance.")
        return redirect(url_for("index"))

    else:
        return render_template(
            "loan.html",
            user=User.query.get(session["user_id"]),
            max_loan_amount=converted_max_loan_amount,
            session_start_time=session.get("start_time"),
            session_lifetime=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(
            )
        )


@app.route("/history")
@login_required
def history():
    """Display transaction history"""
    user = User.query.get(session["user_id"])

    # Get sorting parameters from query string (Default: date in descending order)
    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")

    # Map sortable fields to database columns
    valid_sort_columns = {
        "date": Transaction.date,
        "amount": Transaction.amount,
        "type": Transaction.transaction_type
    }

    # Validate sorting column and order
    sort_column = valid_sort_columns.get(sort_by, Transaction.date)
    if order == "asc":
        sort_order = sort_column.asc()
    else:
        sort_order = sort_column.desc()

    # Query transactions
    transactions = (
        Transaction.query.filter_by(user_id=user.id)
        .order_by(sort_order)
        .all()
    )

    return render_template(
        "history.html",
        user=user,
        transactions=transactions,
        sort_by=sort_by,
        order=order,
        session_start_time=session.get("start_time"),
        session_lifetime=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(
        )
    )


@app.route("/change_currency", methods=["POST"])
@login_required
def change_currency():
    """Update user's preferred currency and convert their balance and transactions"""
    user = User.query.get(session["user_id"])

    new_currency = request.form.get("currency")
    if new_currency == user.currency:
        flash("You have already selected this currency.")
        return redirect(request.referrer)

    # Convert balance to new currency
    converted_balance = convert_currency(
        user.balance, user.currency, new_currency)
    if converted_balance is not None:
        user.currency = new_currency

        db.session.commit()
        flash(f"Currency updated to {
              new_currency}.")
    else:
        flash("Failed to fetch exchange rate. Please try again later.")

    return redirect(request.referrer)


# Initialize the database
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
