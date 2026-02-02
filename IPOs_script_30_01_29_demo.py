import requests
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage

# =========================
# CONFIG
# Keys + Passwords hidden
FINNHUB_API_KEY = "xxxxxxxxxxxxxxxxxxxxxx"

EMAIL_ADDRESS = "okanengoni968@gmail.com"
EMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"

# =========================
# FIXED DATE FOR DEMO
# =========================
date_str = "2026-01-29"

# =========================
# FETCH IPO DATA
# =========================
url = "https://finnhub.io/api/v1/calendar/ipo"
params = {
    "from": date_str,
    "to": date_str,
    "token": FINNHUB_API_KEY
}

response = requests.get(url, params=params)
print("HTTP status:", response.status_code)
print("Response snippet:", response.text[:300])

data = response.json()
ipos = data.get("ipoCalendar", [])

# =========================
# FILTER: OFFER > $200M
# =========================
qualified = []

for ipo in ipos:
    price = ipo.get("price")
    shares = ipo.get("numberOfShares")
    ticker = ipo.get("symbol")
    name = ipo.get("name")
    exchange = ipo.get("exchange")

    if price and shares:
        offering_value = float(price) * int(shares)
        if offering_value > 200_000_000:
            qualified.append({
                "ticker": ticker,
                "name": name,
                "exchange": exchange,
                "shares": shares,
                "price": float(price),
                "offering_value": offering_value
            })

# =========================
# EMAIL RESULTS (HTML)
# =========================
if qualified:
    msg = EmailMessage()
    msg["Subject"] = f"[IPO ALERT] US IPOs > $200M – {date_str}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    # Build HTML table
    html = f"""
    <html>
    <body>
        <h2 style="font-family:Arial,sans-serif;color:#1a237e;">US IPOs Exceeding $200M – {date_str}</h2>
        <table style="border-collapse: collapse; width: 100%; font-family:Arial,sans-serif;">
            <thead>
                <tr style="background-color:#1a237e; color:white;">
                    <th style="border:1px solid #ddd; padding:8px;">Ticker</th>
                    <th style="border:1px solid #ddd; padding:8px;">Name</th>
                    <th style="border:1px solid #ddd; padding:8px;">Exchange</th>
                    <th style="border:1px solid #ddd; padding:8px;">Shares</th>
                    <th style="border:1px solid #ddd; padding:8px;">Price ($)</th>
                    <th style="border:1px solid #ddd; padding:8px;">Total Offering ($)</th>
                </tr>
            </thead>
            <tbody>
    """

    # Alternating row colors
    for i, ipo in enumerate(qualified):
        bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
        html += f"""
            <tr style="background-color:{bg};">
                <td style="border:1px solid #ddd; padding:8px;">{ipo['ticker']}</td>
                <td style="border:1px solid #ddd; padding:8px;">{ipo['name']}</td>
                <td style="border:1px solid #ddd; padding:8px;">{ipo['exchange']}</td>
                <td style="border:1px solid #ddd; padding:8px;">{ipo['shares']:,}</td>
                <td style="border:1px solid #ddd; padding:8px;">{ipo['price']:.2f}</td>
                <td style="border:1px solid #ddd; padding:8px;">${ipo['offering_value']:,.0f}</td>
            </tr>
        """

    html += """
            </tbody>
        </table>
        <p style="font-family:Arial,sans-serif; color:#555;">
            Note: Only IPOs with finalized pricing are included.
        </p>
    </body>
    </html>
    """

    # Attach HTML to the email
    msg.add_alternative(html, subtype='html')

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    print("Email sent:", [ipo["ticker"] for ipo in qualified])
else:
    print("No IPOs meet the criteria.")

