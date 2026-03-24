 from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# -------------------------------
# 📧 EMAIL FUNCTION
# -------------------------------
def send_email(to_email, name):
    sender_email = "yourgmail@gmail.com"
    sender_password = "your_app_password"

    subject = "Invoice Generated"
    body = f"Hello {name},\n\nYour invoice has been generated successfully.\n\nThank you!"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {name}")
    except Exception as e:
        print("Email Error:", e)


# -------------------------------
# 🧠 FRAUD DETECTION
# -------------------------------
def detect_fraud(row):
    if "@" not in row['email'] or row['attempts'] > 3:
        return "Fraud"
    return "Safe"


# -------------------------------
# 🤖 AI SCORE CALCULATION
# -------------------------------
def calculate_score(row):
    score = 0

    if "@" not in row['email']:
        score += 0.5
    if row['attempts'] > 3:
        score += 0.5

    return round(score, 2)


# -------------------------------
# 📊 PROCESS DATA
# -------------------------------
def process_data():
    df = pd.read_csv("leads.csv")

    # Basic checks
    df['status'] = df['email'].apply(lambda x: "Valid" if "@" in x else "Invalid")
    df['fraud_status'] = df.apply(detect_fraud, axis=1)

    # AI Score + Prediction
    df['ai_score'] = df.apply(calculate_score, axis=1)
    df['prediction'] = df['ai_score'].apply(
        lambda x: "High Risk" if x > 0.5 else "Low Risk"
    )

    safe_leads = df[df['fraud_status'] == "Safe"]

    # -------------------------------
    # 📊 Chart
    # -------------------------------
    counts = df['fraud_status'].value_counts()

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    counts.plot(kind='bar')
    plt.title("Fraud vs Safe Leads")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.savefig("static/chart.png")
    plt.close()

    return df, safe_leads


# -------------------------------
# 🌐 HOME ROUTE
# -------------------------------
@app.route('/')
def index():
    df, safe_leads = process_data()

    return render_template(
        "index.html",
        tables=[df.to_html(classes='data', index=False)],
        safe_tables=[safe_leads.to_html(classes='data', index=False)]
    )


# -------------------------------
# 📊 GRAPH ROUTE
# -------------------------------
@app.route('/graph')
def graph():
    process_data()
    return send_file("static/chart.png", mimetype='image/png')


# -------------------------------
# 📧 SEND EMAIL
# -------------------------------
@app.route('/send', methods=['POST'])
def send():
    df, safe_leads = process_data()

    for _, row in safe_leads.iterrows():
        send_email(row['email'], row['name'])

    return "✅ Emails Sent Successfully!"


# -------------------------------
# ▶️ RUN APP (RENDER FIX)
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
