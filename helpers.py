from flask_mail import Mail, Message
from flask import redirect, session
from functools import wraps
import requests

mail = None

def init_helpers(app):
    """
    Initialize helpers with the Flask app.
    This function sets up Flask-Mail with the app context.
    """
    global mail
    mail = Mail(app)


def send_email(to, subject, body):
    """
    Send an email using Flask-Mail.
    Raises RuntimeError if Flask-Mail is not initialized.
    """
    if not mail:
        raise RuntimeError(
            "Flask-Mail is not initialized. Call init_helpers(app) first."
        )
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)


def login_required(f):
    """
    Decorate routes to require login.

    Redirects to /login if no user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def convert_currency(amount, from_currency, to_currency):
    """
    Convert currency from one type to another using live exchange rates.

    Args:
        amount (float): The amount to convert.
        from_currency (str): The currency to convert from (e.g., 'USD').
        to_currency (str): The currency to convert to (e.g., 'EUR').

    Returns:
        float: Converted amount or None if the conversion fails.
    """
    api_key = '07f8500c0cff149494b6e785'  # Replace with your actual API key
    url = f'https://v6.exchangerate-api.com/v6/{
        api_key}/latest/{from_currency}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['result'] == 'success':
            # Fetch the exchange rate from the response
            exchange_rate = data['conversion_rates'].get(to_currency)
            if exchange_rate:
                return round(amount * exchange_rate, 2)
        return None
    except requests.RequestException as e:
        print(f"Error fetching currency conversion data: {e}")
        return None


def get_currency_symbol(currency_code):
    """
    Returns the symbol for a given currency code.

    Args:
        currency_code (str): The currency code (e.g., 'USD', 'EUR', 'GBP').

    Returns:
        str: The corresponding currency symbol.
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    # Default to empty string if not found
    return currency_symbols.get(currency_code, '')
