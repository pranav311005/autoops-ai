from flask import Flask, render_template
import pandas as pd
import re
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# -----------------------------
# Load leads
# -----------------------------
def load_leads(file):
    return pd.read_csv(file)

# -----------------------------
# Email validation
# -----------------------------
def validate_email(email):
    pattern = r'^\S+@\S+\.\S+$'
    return "Valid" if re.match(pattern, str(email)) else "Invalid"

# -----------------------------
# Fraud detection
# -----------------------------
def detect_fraud(row):
    if row["attempts"] > 3 or row["status"] == "Invalid":
        return "Fraud"
    return "Safe"

# -----------------------------
# AI Lead Scoring
# -----------------------------
def lead_score(row):
    score = 50

    if row["status"] == "Valid":
        score += 20
    else:
        score -= 30

    if row["attempts"] <= 2:
        score += 20
    else:
        score -= 20

    if "gmail.com" in row["email"]:
        score += 10
    else:
        score += 5

    return score

# -----------------------------
# AI Category
# -----------------------------
def categorize_lead(score):
    if score >= 80:
        return "High Value"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"

# -----------------------------
# Invoice Generator
# -----------------------------
def generate_invoice(name):
    file_name = f"{name}_invoice.pdf"
    c = canvas.Canvas(file_name)

    c.drawString(100, 750, "INVOICE")
    c.drawString(100, 700, f"Customer Name: {name}")
    c.drawString(100, 650, "Service: Business Automation")
    c.drawString(100, 630, "Amount: ₹500")

    c.save()
    print(f"Invoice generated for {name}")

# -----------------------------
# Home Route (MAIN LOGIC)
# -----------------------------
@app.route("/")
def home():
    leads = load_leads("leads.csv")

    # Step 1: Validation
    leads["status"] = leads["email"].apply(validate_email)

    # Step 2: Fraud detection
    leads["fraud_status"] = leads.apply(detect_fraud, axis=1)

    # Step 3: AI scoring
    leads["score"] = leads.apply(lead_score, axis=1)
    leads["category"] = leads["score"].apply(categorize_lead)

    # Rename for UI clarity (optional)
    leads.rename(columns={"score": "AI Score"}, inplace=True)

    # Step 4: Filter safe leads
    safe_leads = leads[leads["fraud_status"] == "Safe"]

    # Step 5: Generate invoices
    for _, row in safe_leads.iterrows():
        generate_invoice(row["name"])

    # -----------------------------
    # Create Chart
    # -----------------------------
    category_counts = leads["category"].value_counts()

    plt.figure()
    category_counts.plot(kind='bar')
    plt.title("Lead Category Distribution")
    plt.xlabel("Category")
    plt.ylabel("Count")

    chart_path = "static/chart.png"
    plt.savefig(chart_path)
    plt.close()

    # -----------------------------
    # Render UI
    # -----------------------------
    return render_template(
        "index.html",
        tables=[leads.to_html(classes='data', index=False)],
        titles=leads.columns.values
    )

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
