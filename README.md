# Local Farmer Market Information System

A web application that connects local farmers directly with customers. Farmers list their produce and set their own prices, customers browse and compare, and everyone can see the current rates in nearby markets.

Built with **Python, Flask and SQLite** as my [semester / final year] project at [College Name].

---

## Why I built this

Small farmers often sell through middlemen and end up with a fraction of the final price, while customers pay more without knowing what a fair rate is. I wanted to build something simple that puts both sides in touch and shows the local market rate in the same place, so a farmer can price fairly and a buyer can check that the price is reasonable.

## What it does

The project has seven modules:

1. **Registration and login**: separate accounts for farmers, customers and the admin. Passwords are stored hashed, never as plain text.
2. **Farmer product management**: a farmer can add products, edit price and stock, hide items, and delete them. Farmers can only change their own listings.
3. **Browse, search and filter**: customers can search by crop name, filter by category and town, and sort by price.
4. **Price comparison**: pick a crop and see every farmer selling it, cheapest first, along with the local market average.
5. **Local market rates**: dated prices per kg from nearby markets, which the admin keeps updated.
6. **Contact and inquiries**: customers can message a farmer from the product page, and the farmer replies from their dashboard. Logged-in users can also see the farmer's phone number and open a WhatsApp chat.
7. **Admin panel**: shows totals, lets the admin post or delete market rates, and deactivate users.

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, Jinja2 templates |
| Security | Werkzeug password hashing, session-based login, role checks |

## Project structure

```
farmer_market/
├── app.py              # routes, database setup and sample data
├── requirements.txt
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── product.html
    ├── compare.html
    ├── prices.html
    ├── login.html
    ├── register.html
    ├── product_form.html
    ├── dashboard_farmer.html
    ├── dashboard_customer.html
    ├── admin.html
    └── error.html
```

## Database

SQLite creates `market.db` automatically on the first run and fills it with sample data.

| Table | Stores |
|---|---|
| `users` | name, phone, location, hashed password, role, active status |
| `products` | farmer, name, category, price, unit, quantity, description, availability |
| `market_prices` | crop, market name, price per kg, date |
| `inquiries` | product, customer, message, farmer's reply |

## How to run it

You need Python 3.10 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/local-farmer-market.git
cd local-farmer-market

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Install Flask
python -m pip install -r requirements.txt

# 4. Start the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

To reset all data, stop the server and delete `market.db`. A fresh one is created next time.

## Demo accounts

| Role | Phone | Password |
|---|---|---|
| Admin | 9999999999 | admin123 |
| Farmer | 9876500001 | farmer123 |
| Farmer | 9876500002 | farmer123 |
| Customer | 9876500004 | customer123 |

## Try it out

1. Open the home page and search for "tomato".
2. Click **Compare prices**, choose Tomato, and see which farmer is cheapest.
3. Log in as the customer and send a message to a farmer.
4. Log in as that farmer and reply from **My dashboard**.
5. Log in as the admin and add a new market rate

## What I would add next

- Product photo uploads
- Kannada and Hindi language support
- Price trend charts for each crop
- CSRF protection and email or OTP verification for signup
- Ratings and reviews for farmers
- Deployment on a free hosting platform

## Author

**Advith Anand**
[B.E / CSBS][Srinivas Institute of Technology]
)
