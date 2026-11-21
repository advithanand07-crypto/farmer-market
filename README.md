# Local Farmer Market Information System
Python + Flask + SQLite. Connects local farmers directly with customers.

## Setup (Windows / macOS / Linux)
1. Install Python 3.10+ from python.org (tick "Add Python to PATH" on Windows).
2. Open the `farmer_market` folder in VS Code (File > Open Folder).
3. Open the terminal (Ctrl + `) and run:

   Windows:
       python -m venv venv
       venv\Scripts\activate
       pip install -r requirements.txt
       python app.py

   macOS / Linux:
       python3 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt
       python3 app.py

4. Open http://127.0.0.1:5000 in your browser.

If PowerShell blocks activation, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

The database (`market.db`) is created automatically with sample data on first run.
To reset it, stop the server and delete `market.db`.

## Demo logins (phone / password)
| Role     | Phone      | Password    |
|----------|------------|-------------|
| Admin    | 9999999999 | admin123    |
| Farmer   | 9876500001 | farmer123   |
| Farmer   | 9876500002 | farmer123   |
| Customer | 9876500004 | customer123 |

## The 7 modules
1. Registration and login (farmer / customer / admin, hashed passwords)
2. Farmer product management (add, edit, delete, price and stock updates)
3. Browse, search and filter (name, category, town, sort by price)
4. Price comparison (all farmers for one crop, cheapest highlighted, vs market average)
5. Local market price information (dated rates per market)
6. Contact and inquiry system (message farmer, farmer replies, phone and WhatsApp link)
7. Admin panel (stats, post and delete market rates, deactivate users)

## Files
    app.py              routes, database setup, seed data
    templates/          HTML pages (Jinja2)
    static/style.css    styling
    market.db           created on first run

## Before real deployment
Set a secret key (`SECRET_KEY` environment variable), turn off `debug=True`, and add CSRF protection (Flask-WTF).
