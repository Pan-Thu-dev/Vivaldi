# Vivaldi

#### Video Demo: https://youtu.be/qSJ7m-odqsY

#### Description:

**An Banking App**

This web application is a **banking platform** that allows users to manage their finances with essential features such as account creation, secure login, deposits, withdrawals, money transfers, and loan applications. Designed with a user-friendly interface and robust functionality, the app simplifies financial transactions while ensuring data security and accessibility.

Key functionalities include:

- **User Authentication**: Secure login and signup processes with password recovery via email.
- **Banking Operations**: Users can perform deposits, withdrawals, and transfers while tracking their financial history in detail.
- **Loan Management**: A feature that lets users apply for loans based on eligibility criteria such as account balance and transaction activity.
- **Transaction History**: Provides an organized view of past transactions with filtering and sorting options.
- **Account Activation**: Ensures account security with an email-based activation system.

The backend is powered by **Flask**, with **SQLite** serving as the database for reliable and lightweight data storage. The application uses Flask-SQLAlchemy for ORM, simplifying database interactions. On the frontend, clean HTML templates and a shared stylesheet enhance usability and maintain consistent design.

With its modular structure, the app supports scalability and ease of maintenance. It is ideal for individuals looking for a simple yet effective way to handle their banking needs digitally.

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# helpers.py

This file contains utility functions for various tasks in the Flask application.

The init_helpers(app) function initializes the Flask-Mail extension, enabling email functionality. It should be called at the start of the application to set up email services.

The send_email(to, subject, body) function sends emails using Flask-Mail. If Flask-Mail is not initialized, it raises an error. It requires the recipient's email, subject, and body content.

The login_required(f) function is a decorator that ensures a user is logged in to access certain routes. If not logged in, the user is redirected to the login page.

The convert_currency(amount, from_currency, to_currency) function converts an amount from one currency to another using live exchange rates from the ExchangeRate-API service. It returns the converted amount or None if the conversion fails.

The get_currency_symbol(currency_code) function returns the symbol for a given currency code (e.g., $ for USD, € for EUR). If the code is not found, it returns an empty string.

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# app.py

/ (index): This route displays the homepage for the logged-in user, including their current balance, total deposits, and withdrawals for the current month. It calculates the user’s interest rate based on various factors such as their balance, deposits, and withdrawals, and displays the calculated interest. The session duration is also shown.

/login: This route handles both GET and POST requests for the user login page. If the user submits their credentials via POST, it checks if the email and password match any existing active user. If successful, the user is logged in and redirected to the homepage; otherwise, appropriate error messages are displayed.

/logout: This route logs the user out by removing their session data. If the session has expired, a specific message is shown; otherwise, a general logout message is displayed.

/signup: The signup route processes user registration. It ensures the email, username, and password are provided and valid, then creates a new user with an inactive status. A confirmation code is generated and sent to the user's email, prompting them to activate their account.

/activate: This route allows the user to activate their account by entering the confirmation code sent to their email. Upon successful validation of the code, the user’s account is marked as active, and they can log in.

/request-reset: This route lets users request a password reset. If the user provides a registered email, a reset code is generated and sent to them. The user is then redirected to the password reset page.

/reset-password: After receiving the password reset code, the user can enter the new password on this route. The password is updated in the database if the code matches, and the user is logged out, with instructions to log in with the new password.

/close_account: This route allows users to close their account. The user must enter their password to confirm the closure. If the password is correct, all transactions and the user account are deleted, and they are logged out.

/transaction: This route displays the transaction page where users can deposit or withdraw funds. It also manages session data and provides access to the user’s account balance.

/transaction/deposit: This route handles deposit transactions. Users can deposit money into their account, which is first converted to USD using a currency conversion function. The amount is then added to the user’s balance, and the transaction is recorded.

/transaction/withdraw: This route handles withdrawal transactions. Users can withdraw funds from their account, provided they have enough balance. The withdrawal amount is converted to USD, subtracted from the user’s balance, and recorded in the transaction history.

/transfer: This route allows users to transfer money to another user. The sender provides the recipient’s username and the transfer amount. The transaction is processed, ensuring the sender has enough balance, and both the sender and recipient’s transactions are recorded.

/loan: This route enables users to apply for a loan. The maximum loan amount is based on 20% of their balance. If the requested loan amount does not exceed the limit, it is added to the user’s balance, and the transaction is recorded.

/history: This route shows the transaction history for the logged-in user. The history can be filtered and sorted according to different criteria, providing the user with an overview of all their financial activity.

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Directories and Files

    instance directory:
        banking.db: This is the SQLite database file that stores all the application data, including user information, transactions, and account details.

    static directory:
        styles.css: This CSS file contains the styling rules for the application’s frontend, ensuring a consistent and visually appealing design across all pages.

    templates directory:
        activate.html: The HTML template for the account activation page, where users enter their confirmation code to activate their account.
        history.html: The template displaying a user's transaction history, including filters and sorting options for easier navigation.
        index.html: The homepage template that displays the user’s balance, deposits, withdrawals, and interest details after login.
        layout.html: The base template used for consistent structure across all pages, typically containing common elements like headers, footers, and navigation.
        loan.html: The page template for loan applications, allowing users to view and apply for loans based on their account balance.
        login.html: The login page template where users enter their credentials to access the application.
        request_reset.html: The template for requesting a password reset, where users provide their registered email to receive a reset code.
        reset_password.html: The page template for setting a new password after receiving a reset code.
        signup.html: The registration page template for new users to create an account by providing their details.
        transaction.html: The template for managing deposits and withdrawals, showing the user’s balance and enabling transaction inputs.
        transfer.html: The page template for money transfers, where users specify the recipient’s username and the transfer amount.

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Prerequisites

To run the application locally:

    - Set up a virtual environment to ensure isolated dependency management.
    - Install the required dependencies listed in the requirements.txt file.

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
