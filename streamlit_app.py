import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import random
import openai
import gspread
from google.oauth2.service_account import Credentials

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Mahmoud's Portfolio",
    page_icon="🚀",
    layout="wide"
)

# ===== SECRETS =====
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
SMTP_SERVER = st.secrets["SMTP_SERVER"]
SMTP_PORT = st.secrets["SMTP_PORT"]

GOOGLE_SHEETS_CREDENTIALS = st.secrets["gcp_service_account"]
SHEET_NAME = "Portfolio Contact Submissions"

# ===== OPENAI SETUP =====
openai.api_key = OPENAI_API_KEY

# ===== GOOGLE SHEETS SETUP =====
def init_gsheet():
    creds = Credentials.from_service_account_info(
        GOOGLE_SHEETS_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

def save_to_gsheet(name, email, message):
    try:
        sheet = init_gsheet()
        sheet.append_row([name, email, message])
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

# ===== EMAIL FUNCTION =====
def send_email(name, sender_email, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"New message from {name} via Portfolio"
        body = f"Name: {name}\nEmail: {sender_email}\nMessage:\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# ===== AI RESPONSE FUNCTION =====
def generate_response(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't generate a response. Error: {e}"

# ===== SIDEBAR NAVIGATION =====
with st.sidebar:
    st.title("My Portfolio Hub")
    selected = st.radio(
        "Explore:",
        ["👨‍💻 About Me", "📈 Sales Dashboard", "🤖 AI Assistant"],
        index=0
    )

# ===== ABOUT ME PAGE =====
if selected == "👨‍💻 About Me":
    st.title("About Me")

    col1, col2 = st.columns([1,3])
    with col1:
        st.image("https://i.postimg.cc/yN2Hy4jx/Whats-App-Image-2025-07-22-at-18-05-59-0490803f.jpg", width=200)
    with col2:
        st.markdown("""
        ## Hi, I'm MAHMOUD!
        **Restaurant Manager | AI Developer | Streamlit Expert**

        🌐 **Location:** Riyadh, Kingdom of Saudi Arabia  
        ✉️ **Email:** funky1852@gmail.com
        """)

    st.divider()

    st.header("📝 Experience & Qualifications")
    with st.expander("Professional Experience", expanded=True):
        st.markdown("""
        - **Restaurant Manager** at Fine Dining (2020-Present)  
          - Increased customer satisfaction by 30%  
          - Implemented AI-based inventory system  

        - **Data Analyst** at FoodTech Inc. (2018-2020)  
          - Created sales dashboards reducing reporting time by 50%
        """)

    with st.expander("Education"):
        st.markdown("""
        - **BSc in Business Administration** - KSU (2018)  
        - **Hospitality Management Diploma** - SFDA (2016)
        """)

    st.divider()

    st.header("🛠 Hard Skills")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Management**")
        st.write("- Team Leadership\n- Inventory Control\n- Customer Service")
    with cols[1]:
        st.markdown("**Technology**")
        st.write("- Python\n- Streamlit\n- Data Analysis")
    with cols[2]:
        st.markdown("**Languages**")
        st.write("- Arabic (Native)\n- English (Fluent)\n- French (Basic)")

    st.divider()

    # ===== Contact Form with CAPTCHA =====
    st.header("📩 Contact Me")

    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        st.session_state.captcha_num1 = random.randint(1, 10)
        st.session_state.captcha_num2 = random.randint(1, 10)

    with st.form("contact_form"):
        name = st.text_input("Your Name", key="name")
        email = st.text_input("Your Email", key="email")
        message = st.text_area("Your Message", height=150, key="message")

        captcha_answer = st.text_input(
            f"What is {st.session_state.captcha_num1} + {st.session_state.captcha_num2}?",
            key="captcha_answer"
        )

        submitted = st.form_submit_button("Send Message")

        if submitted:
            if not name or not email or not message:
                st.error("Please fill all the fields")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email address")
            elif not captcha_answer.isdigit() or int(captcha_answer) != (st.session_state.captcha_num1 + st.session_state.captcha_num2):
                st.error("CAPTCHA failed. Please try again.")
                st.session_state.captcha_num1 = random.randint(1, 10)
                st.session_state.captcha_num2 = random.randint(1, 10)
            else:
                if send_email(name, email, message):
                    save_to_gsheet(name, email, message)
                    st.success("Message sent successfully! I'll get back to you soon.")
                    st.session_state.name = ""
                    st.session_state.email = ""
                    st.session_state.message = ""
                    st.session_state.captcha_answer = ""
                    st.session_state.captcha_num1 = random.randint(1, 10)
                    st.session_state.captcha_num2 = random.randint(1, 10)
                else:
                    st.error("Failed to send message. Please try again later.")

# ===== SALES DASHBOARD =====
elif selected == "📈 Sales Dashboard":
    st.title("Restaurant Sales Analytics")

    @st.cache_data
    def load_data():
        return pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Revenue (SAR)": [125000, 180000, 210000, 195000, 230000, 280000],
            "Customers": [450, 620, 780, 710, 850, 1030]
        })

    df = load_data()

    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox("View Metric:", ["Revenue (SAR)", "Customers"])
    with col2:
        chart_type = st.radio("Chart Type:", ["Line", "Bar"], horizontal=True)

    if chart_type == "Line":
        fig = px.line(df, x="Month", y=metric, title=f"Monthly {metric} Trend")
    else:
        fig = px.bar(df, x="Month", y=metric, title=f"Monthly {metric}")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Raw Data Explorer"):
        st.dataframe(df, use_container_width=True)

# ===== AI CHAT ASSISTANT =====
elif selected == "🤖 AI Assistant":
    st.title("Your Personal AI Assistant")

    st.markdown("""
    ### Hey there! Any questions?
    Check out my YouTube channel for more content:  
    ▶️ [https://youtube.com/@mahmoudhatem7290?si=LYKD4ubYcEO4J5Cj](https://youtube.com/@mahmoudhatem7290?si=LYKD4ubYcEO4J5Cj)
    """)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = generate_response(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
