import streamlit as st
import qrcode
from PIL import Image
import io
import base64
import pandas as pd
from datetime import date

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Proxy Portal",
    page_icon="🎓",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background: #0d0f1a !important;
    font-family: 'DM Sans', sans-serif;
    color: #e8e9f0;
}
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.hero {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1528 50%, #12102a 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    padding: 2.4rem 2.8rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 70% 20%, rgba(99,102,241,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.45);
    color: #a5b4fc;
    font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 0.28rem 0.85rem; border-radius: 50px;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.9rem, 4vw, 2.6rem);
    font-weight: 800; line-height: 1.15;
    color: #ffffff; letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
.hero-title span { color: #818cf8; }
.hero-sub { font-size: 0.92rem; color: #94a3b8; font-weight: 300; max-width: 480px; }

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #6366f1; margin-bottom: 0.7rem; margin-top: 0.5rem;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stMetricLabel"] > div { color: #94a3b8 !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] > div { color: #6ee7b7 !important; font-family: 'Syne', sans-serif !important; }

/* QR wrapper */
.qr-wrapper {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 2rem;
    text-align: center; margin-top: 1rem;
}
.qr-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; color: #c7d2fe; margin-bottom: 0.35rem; }
.qr-sub { color: #64748b; font-size: 0.8rem; margin-bottom: 1.4rem; }
.qr-steps { display: flex; gap: 0.6rem; justify-content: center; flex-wrap: wrap; margin-top: 1.4rem; }
.qr-step { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); border-radius: 8px; padding: 0.4rem 0.9rem; font-size: 0.76rem; color: #a5b4fc; }

/* Form inputs */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8e9f0 !important;
}
label { color: #94a3b8 !important; font-size: 0.82rem !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.72rem 2rem !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Checkbox */
.stCheckbox > label { color: #94a3b8 !important; font-size: 0.88rem !important; }

/* Dataframe / table */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────
SUBJECTS = {
    "OS":   {"full": "Operating Systems",              "icon": "🖥️", "cost": 20},
    "DPPL": {"full": "Design Patterns & Prog. Lang.",  "icon": "🧩", "cost": 20},
    "DMGT": {"full": "Data Management",                "icon": "🗄️", "cost": 20},
    "SE":   {"full": "Software Engineering",           "icon": "⚙️", "cost": 20},
    "DAA":  {"full": "Design & Analysis of Algo.",     "icon": "📐", "cost": 20},
}

UPI_ID = "college@upi"   # ← Replace with your real UPI ID
PAYEE  = "College Proxy Fee"

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">🎓 Academic Services Portal</div>
  <div class="hero-title">Student <span>Proxy</span><br>Application</div>
  <div class="hero-sub">Select subjects, pay the fee via QR, and submit your proxy request in minutes.</div>
</div>
""", unsafe_allow_html=True)

# ── Step 1 – Student Info ─────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 1 — Student Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    student_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
with col2:
    roll_no = st.text_input("Roll Number", placeholder="e.g. 2023CS042")

col3, col4 = st.columns(2)
with col3:
    division = st.selectbox("Division", ["A", "B", "C", "D"])
with col4:
    proxy_date = st.date_input("Date of Proxy", value=date.today())

st.markdown("<br>", unsafe_allow_html=True)

# ── Step 2 – Subject Selection ────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 2 — Select Subjects</div>', unsafe_allow_html=True)

selected = []
for code, info in SUBJECTS.items():
    if st.checkbox(f"**{code}** — {info['full']}  •  ₹{info['cost']}", key=f"subj_{code}"):
        selected.append(code)

st.markdown("<br>", unsafe_allow_html=True)

# ── Step 3 – Summary & QR ────────────────────────────────────────────────────
st.markdown('<div class="section-label">Step 3 — Payment Summary</div>', unsafe_allow_html=True)

total = sum(SUBJECTS[c]["cost"] for c in selected)

if selected:
    subject_list = ", ".join(selected)

    # ── Summary table using pandas (avoids raw HTML rendering bug) ──
    table_rows = [
        {
            "Subject": f"{SUBJECTS[c]['icon']} {c}",
            "Description": SUBJECTS[c]["full"],
            "Amount (₹)": SUBJECTS[c]["cost"],
        }
        for c in selected
    ]
    df = pd.DataFrame(table_rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Subject":      st.column_config.TextColumn("Subject", width="small"),
            "Description":  st.column_config.TextColumn("Description"),
            "Amount (₹)":   st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
        },
    )

    # ── Metric row ──
    m1, m2, m3 = st.columns(3)
    m1.metric("Subjects Selected", len(selected))
    m2.metric("Rate per Subject",  "₹20")
    m3.metric("Total Payable",     f"₹{total}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Generate QR code ─────────────────────────────────────────────────────
    upi_url = (
        f"upi://pay?pa={UPI_ID}"
        f"&pn={PAYEE.replace(' ', '%20')}"
        f"&am={total}&cu=INR"
        f"&tn=Proxy:{subject_list.replace(' ', '%20')}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e1b4b", back_color="#ffffff")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    st.markdown(f"""
    <div class="qr-wrapper">
        <div class="qr-title">📲 Scan to Pay ₹{total}</div>
        <div class="qr-sub">Use any UPI app — PhonePe, GPay, Paytm, BHIM</div>
        <img src="data:image/png;base64,{b64}"
             style="width:210px;height:210px;border-radius:12px;
                    box-shadow:0 8px 32px rgba(0,0,0,0.5);" />
        <div class="qr-steps">
            <span class="qr-step">1 · Open UPI App</span>
            <span class="qr-step">2 · Scan QR Code</span>
            <span class="qr-step">3 · Pay ₹{total}</span>
            <span class="qr-step">4 · Submit Below</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 4 – Confirm & Submit ─────────────────────────────────────────────
    st.markdown('<div class="section-label">Step 4 — Confirm & Submit</div>', unsafe_allow_html=True)

    txn_id = st.text_input("UPI Transaction ID", placeholder="Enter 12-digit transaction ID after payment")
    confirm = st.checkbox(f"I confirm that payment of ₹{total} has been made successfully.")

    if st.button("🚀  Submit Proxy Application", use_container_width=True):
        if not student_name.strip():
            st.error("⚠️ Please enter your full name.")
        elif not roll_no.strip():
            st.error("⚠️ Please enter your roll number.")
        elif not txn_id.strip():
            st.error("⚠️ Please enter the UPI Transaction ID.")
        elif not confirm:
            st.error("⚠️ Please confirm payment before submitting.")
        else:
            st.success(
                f"✅ **Proxy application submitted successfully!**\n\n"
                f"**Student:** {student_name}  |  **Roll No:** {roll_no}\n\n"
                f"**Date:** {proxy_date}  |  **Division:** {division}\n\n"
                f"**Subjects:** {subject_list}\n\n"
                f"**Amount Paid:** ₹{total}  |  **Txn ID:** {txn_id}"
            )
            st.balloons()

else:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.1);
                border-radius:14px;padding:2rem;text-align:center;">
        <div style="font-size:2rem;margin-bottom:0.6rem;">📚</div>
        <div style="font-family:'Syne',sans-serif;font-weight:600;color:#64748b;font-size:0.92rem;">
            Select at least one subject above to see the payment summary and QR code.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.75rem;">
    Student Proxy Portal &nbsp;·&nbsp; Academic Services &nbsp;·&nbsp; 2025
</div>
""", unsafe_allow_html=True)