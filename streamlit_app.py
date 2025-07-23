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
import traceback
from datetime import datetime

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Mahmoud's Portfolio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ERROR LOGGING =====
def log_error(error_type, details):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("error_log.txt", "a") as f:
            f.write(f"{timestamp} - {error_type}: {details}\n")
    except Exception as e:
        print(f"Failed to log error: {e}")

# ===== SECRETS VALIDATION =====
def validate_secrets():
    required_secrets = [
        "OPENAI_API_KEY",
        "EMAIL_ADDRESS",
        "EMAIL_PASSWORD",
        "SMTP_SERVER",
        "SMTP_PORT",
        "gcp_service_account"
    ]
    
    missing = []
    for key in required_secrets:
        try:
            if key not in st.secrets:
                missing.append(key)
        except:
            missing = required_secrets
            break
    
    if missing:
        st.error(f"Missing configuration: {', '.join(missing)}")
        log_error("ConfigurationError", f"Missing secrets: {missing}")
        return False
    return True

# ===== INITIALIZE SERVICES =====
if not validate_secrets():
    st.stop()

try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("Failed to initialize OpenAI API")
    log_error("OpenAIInitError", str(e))
    st.stop()

# ===== GOOGLE SHEETS SERVICE =====
def init_gsheet():
    try:
        # Create full service account info dict
        sa_info = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
        }
        
        creds = Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sheet = client.open("Portfolio Contact Submissions").sheet1
        return sheet
    except Exception as e:
        log_error("GoogleSheetsError", traceback.format_exc())
        return None

def save_to_gsheet(name, email, message):
    try:
        sheet = init_gsheet()
        if sheet is None:
            return False
            
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            email,
            message
        ])
        return True
    except Exception as e:
        log_error("GoogleSheetsSaveError", traceback.format_exc())
        return False

# ===== EMAIL SERVICE =====
def send_email(name, sender_email, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = st.secrets["EMAIL_ADDRESS"]
        msg['To'] = st.secrets["EMAIL_ADDRESS"]
        msg['Subject'] = f"New Portfolio Message: {name[:30]}"
        
        body = f"""
        New Contact Form Submission:
        
        Name: {name}
        Email: {sender_email}
        Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        Message:
        {message}
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(st.secrets["SMTP_SERVER"], st.secrets["SMTP_PORT"]) as server:
            server.ehlo()
            server.starttls()
            server.login(st.secrets["EMAIL_ADDRESS"], st.secrets["EMAIL_PASSWORD"])
            server.sendmail(
                st.secrets["EMAIL_ADDRESS"], 
                st.secrets["EMAIL_ADDRESS"], 
                msg.as_string()
            )
        return True
    except smtplib.SMTPAuthenticationError:
        log_error("EmailAuthError", "SMTP Authentication failed")
        return False
    except Exception as e:
        log_error("EmailError", traceback.format_exc())
        return False

# ===== AI SERVICE =====
def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log_error("AIError", f"Prompt: {prompt[:100]}... | Error: {str(e)}")
        return "I'm having trouble responding right now. Please try again later."

# ===== SIDEBAR NAVIGATION =====
with st.sidebar:
    st.title("My Portfolio Hub")
    selected = st.radio(
        "Explore:",
        ["👨‍💻 About Me", "📈 Sales Dashboard", "🤖 AI Assistant"],
        index=0,
        key="nav_radio"
    )
    
    st.markdown("---")
    st.markdown("""
    **Connect with me:**
    - [LinkedIn](#)
    - [GitHub](#)
    - [YouTube](#)
    """)

# ===== ABOUT ME PAGE =====
if selected == "👨‍💻 About Me":
    st.title("About Me")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://i.postimg.cc/yN2Hy4jx/Whats-App-Image-2025-07-22-at-18-05-59-0490803f.jpg", 
                width=200, caption="Mahmoud Hatem")
    with col2:
        st.markdown("""
        ## Hi, I'm MAHMOUD!
        **Restaurant Manager | AI Developer | Streamlit Expert**

        🌐 **Location:** Riyadh, Kingdom of Saudi Arabia  
        ✉️ **Email:** funky1852@gmail.com  
        🔗 **Portfolio:** [mahmoudhatem.com](#)
        """)

    st.divider()

    # Experience Section
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        with st.expander("📝 Professional Experience", expanded=True):
            st.markdown("""
            - **Restaurant Manager** at Fine Dining (2020-Present)  
              - Increased customer satisfaction by 30%  
              - Implemented AI-based inventory system  
              - Managed team of 25+ staff members
            
            - **Data Analyst** at FoodTech Inc. (2018-2020)  
              - Created sales dashboards reducing reporting time by 50%
              - Developed predictive models for inventory
            """)
    
    with exp_col2:
        with st.expander("🎓 Education"):
            st.markdown("""
            - **BSc in Business Administration**  
              King Saud University (2018)
            
            - **Hospitality Management Diploma**  
              Saudi Food and Drug Authority (2016)
            """)

    st.divider()

    # Skills Section
    st.header("🛠 Skills & Competencies")
    skills_col1, skills_col2, skills_col3 = st.columns(3)
    
    with skills_col1:
        st.markdown("**🍽️ Management**")
        st.write("""
        - Team Leadership
        - Inventory Control
        - Customer Service
        - Operations
        """)
    
    with skills_col2:
        st.markdown("**💻 Technology**")
        st.write("""
        - Python (Streamlit, Pandas)
        - Data Analysis
        - AI Integration
        - Automation
        """)
    
    with skills_col3:
        st.markdown("**🗣️ Languages**")
        st.write("""
        - Arabic (Native)
        - English (Fluent)
        - French (Basic)
        """)

    st.divider()

    # Contact Form
    st.header("📩 Contact Me")
    
    if "captcha_num1" not in st.session_state:
        st.session_state.captcha_num1 = random.randint(1, 10)
        st.session_state.captcha_num2 = random.randint(1, 10)

    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Your Name*", key="name")
        email = st.text_input("Your Email*", key="email")
        message = st.text_area("Your Message*", height=150, key="message",
                             placeholder="Your project details or questions...")

        captcha_answer = st.text_input(
            f"What is {st.session_state.captcha_num1} + {st.session_state.captcha_num2}?*",
            key="captcha_answer"
        )

        submitted = st.form_submit_button("Send Message")
        
        if submitted:
            # Validation
            errors = []
            if not name.strip():
                errors.append("Name is required")
            if not email.strip() or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Valid email is required")
            if not message.strip():
                errors.append("Message is required")
            try:
                if int(captcha_answer) != st.session_state.captcha_num1 + st.session_state.captcha_num2:
                    errors.append("CAPTCHA verification failed")
            except:
                errors.append("CAPTCHA must be a number")
            
            if errors:
                for error in errors:
                    st.error(error)
                st.session_state.captcha_num1 = random.randint(1, 10)
                st.session_state.captcha_num2 = random.randint(1, 10)
            else:
                # Process submission
                with st.spinner("Sending your message..."):
                    email_sent = send_email(name, email, message)
                    sheet_saved = save_to_gsheet(name, email, message)
                
                if email_sent or sheet_saved:
                    if email_sent and sheet_saved:
                        st.success("✅ Message sent successfully! I'll respond within 24 hours.")
                    elif email_sent:
                        st.success("📧 Message emailed! (Google Sheets save failed)")
                    else:
                        st.success("📊 Message saved! (Email send failed)")
                    
                    # Reset form
                    st.session_state.captcha_num1 = random.randint(1, 10)
                    st.session_state.captcha_num2 = random.randint(1, 10)
                    st.rerun()  # This will clear the form
                else:
                    st.error("❌ Both email and Google Sheets failed. Please contact me directly at funky1852@gmail.com")

# ===== SALES DASHBOARD =====
elif selected == "📈 Sales Dashboard":
    st.title("📊 Restaurant Sales Analytics")
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_data():
        return pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
            "Revenue (SAR)": [125000, 180000, 210000, 195000, 230000, 280000, 310000, 295000],
            "Customers": [450, 620, 780, 710, 850, 1030, 1150, 1100],
            "Avg. Spend": [278, 290, 269, 275, 271, 272, 270, 268]
        })
    
    df = load_data()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        metric = st.selectbox("Select Metric", 
                            ["Revenue (SAR)", "Customers", "Avg. Spend"])
    with col2:
        chart_type = st.selectbox("Chart Type", 
                                ["Line", "Bar", "Area"])
    with col3:
        show_table = st.checkbox("Show Data Table", True)
    
    # Visualization
    fig = None
    if chart_type == "Line":
        fig = px.line(df, x="Month", y=metric, 
                     title=f"Monthly {metric} Trend",
                     template="plotly_white")
    elif chart_type == "Bar":
        fig = px.bar(df, x="Month", y=metric,
                    title=f"Monthly {metric}",
                    color="Month",
                    template="plotly_white")
    else:
        fig = px.area(df, x="Month", y=metric,
                     title=f"Monthly {metric}",
                     template="plotly_white")
    
    if fig:
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Month",
            yaxis_title=metric
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data Table
    if show_table:
        with st.expander("📋 Raw Data", expanded=True):
            st.dataframe(df.style.format({
                "Revenue (SAR)": "{:,.0f}",
                "Avg. Spend": "{:.1f}"
            }), use_container_width=True)
    
    # Metrics Summary
    st.subheader("Performance Summary")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Revenue (SAR)", 
                f"{df['Revenue (SAR)'].sum():,.0f}")
    with m2:
        st.metric("Total Customers", 
                f"{df['Customers'].sum():,.0f}")
    with m3:
        st.metric("Average Spend", 
                f"{df['Avg. Spend'].mean():.1f} SAR")

# ===== AI CHAT ASSISTANT =====
elif selected == "🤖 AI Assistant":
    st.title("💬 AI Assistant")
    
    st.markdown("""
    Ask me anything about my work, technology, or restaurant management!
    *Note: I may occasionally make mistakes. Verify important information.*
    """)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Mahmoud's AI assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = generate_response(prompt)
                    st.markdown(response)
                except Exception as e:
                    error_msg = "I'm having trouble responding right now. Please try again later."
                    st.error(error_msg)
                    log_error("ChatError", f"Prompt: {prompt} | Error: {str(e)}")
                    response = error_msg
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        