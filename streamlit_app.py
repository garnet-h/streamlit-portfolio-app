import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Mahmoud's Portfolio",
    page_icon="🚀",
    layout="wide"
)

# ===== EMAIL CONFIGURATION =====
def send_email(name, email, message):
    """Send email using SMTP"""
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "funky1852@gmail.com"  # Your email
    receiver_email = "funky1852@gmail.com"  # Recipient email
    password = st.secrets["EMAIL_PASSWORD"]  # App password from secrets
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New message from {name}"
    
    body = f"""
    Name: {name}
    Email: {email}
    Message: {message}
    """
    msg.attach(MIMEText(body, 'plain'))
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# ===== SIDEBAR =====
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
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://via.placeholder.com/200", width=150)
    with col2:
        st.markdown("""
        ## Hi, I'm MAHMOUD!
        **Restaurant Manager | AI Developer | Streamlit Expert**
        
        🌐 **Location:** Riyadh, Saudi Arabia  
        ✉️ **Email:** funky1852@gmail.com  
        """)
    
    st.divider()
    
    # Experience & Qualifications
    st.header("📝 Experience & Qualifications")
    with st.expander("Professional Experience", expanded=True):
        st.markdown("""
        - **Restaurant Manager** (2020-Present)  
          - Increased customer satisfaction by 30%  
          - Implemented inventory management systems  
        """)
    
    st.divider()
    
    # Contact Form
    st.header("📩 Contact Me")
    with st.form("contact_form"):
        name = st.text_input("Name", key="name")
        email = st.text_input("Email", key="email")
        message = st.text_area("Message", key="message")
        submitted = st.form_submit_button("Send")
        
        if submitted:
            if send_email(name, email, message):
                st.success("Message sent successfully!")
            else:
                st.error("Failed to send message")

# ===== SALES DASHBOARD =====
elif selected == "📈 Sales Dashboard":
    st.title("Sales Analytics")
    
    # Sample data
    data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar"],
        "Sales": [10000, 15000, 12000]
    })
    
    fig = px.bar(data, x="Month", y="Sales")
    st.plotly_chart(fig)

# ===== CHAT BOT =====
elif selected == "🤖 AI Assistant":
    st.title("AI Assistant")
    st.markdown("""
    ### Hey there! Any questions?
    Check out my YouTube channel:  
    [https://youtube.com/@mahmoudhatem7290](https://youtube.com/@mahmoudhatem7290)
    """)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Say something"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = f"Echo: {prompt}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
