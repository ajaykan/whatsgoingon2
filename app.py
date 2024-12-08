import streamlit as st
import pandas as pd
from datetime import datetime
import time
import stripe
import os
from dotenv import load_dotenv
import sqlite3


# Initialize database
def init_db():
    conn = sqlite3.connect('subscriptions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions
        (customer_id TEXT PRIMARY KEY,
         status TEXT,
         subscription_id TEXT,
         created_at TIMESTAMP,
         updated_at TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def check_subscription(customer_id):
    conn = sqlite3.connect('subscriptions.db')
    c = conn.cursor()
    c.execute('SELECT status FROM subscriptions WHERE customer_id = ?', (customer_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Load environment variables from .env file
load_dotenv()

# Initialize Stripe with your secret key
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    print("Stripe API key loaded successfully")
except Exception as e:
    print(f"Failed to load Stripe API key: {e}")

# Use other environment variables as needed
price_id = st.secrets['STRIPE_PRICE_ID']

# Near the top of your file, add a session state to track subscription
if 'is_subscribed' not in st.session_state:
    st.session_state.is_subscribed = False  # Default to not subscribed

st.title("WhatsGoingOn")

st.write("Helping WallStreetBettors lose money even faster")
df = pd.read_json("post_data.json")
sentiments = ['All'] + sorted(df['THESIS'].unique().tolist())
selected_sentiment = st.selectbox('Filter by Sentiment:', sentiments)


def create_post_html(row):

    html = f"""
    <div style="max-width: 1800px; border: 2px solid #374151; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin: 0.5rem 0;">
        <div style="padding: 1.5rem">
            <div style="padding: 1rem 0;">
                <a 
                    href="https://finance.yahoo.com/quote/{row['TICKER']}/" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    style="display: inline-block; background-color: #E5E7EB; border-radius: 9999px; padding: 0.25rem 0.75rem; font-size: 1rem; font-weight: 600; color: #374151; margin-right: 0.75rem; margin-bottom: 0.5rem; text-decoration: none;"
                >
                    {row['TICKER']}
                </a>
                <span style="display: inline-block; background-color: #E5E7EB; border-radius: 9999px; padding: 0.25rem 0.75rem; font-size: 1rem; font-weight: 600; color: #374151; margin-right: 0.75rem; margin-bottom: 0.5rem;">
                    {row['THESIS']}
                </span>
                <a 
                    href="{row['url']}"
                    target="_blank" 
                    rel="noopener noreferrer" 
                    style="display: inline-block; background-color: #E5E7EB; border-radius: 9999px; padding: 0.25rem 0.75rem; font-size: 1rem; font-weight: 600; color: #374151; margin-right: 0.75rem; margin-bottom: 0.5rem; text-decoration: none;"
                >
                    Link
                </a>
            </div>
            <p style="color: #white; font-size: 0.875rem; margin: 0.5rem 0;">
                <b style="font-size: 1rem;">Summary:</b> {row['KEY POINTS']}
            </p>
            <p style="color: #white; font-size: 0.875rem; margin: 0.5rem 0;">
                <b style="font-size: 1rem;">Position:</b> {row['POSITION']}
            </p>
        </div>
    </div>
    """
    return html

# Display posts with paywall
filtered_df = df if selected_sentiment == 'All' else df[df['THESIS'] == selected_sentiment]

for idx, (_, row) in enumerate(filtered_df.iterrows()):
    if idx < 2:  # First two posts are always shown
        html_block = create_post_html(row)
        st.markdown(html_block, unsafe_allow_html=True)
    elif st.session_state.is_subscribed:  # Show remaining posts only if subscribed
        html_block = create_post_html(row)
        st.markdown(html_block, unsafe_allow_html=True)
    elif idx == 2:  # Show paywall message after first two posts
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="width: 95%; border: 2px solid #374151; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin: 0.5rem auto; padding: 2rem; text-align: center;">
                <h2 style="margin-bottom: 1rem;">🔒 Subscribe For All Posts</h2>
                <p style="margin-bottom: 2rem;">LLMs are expensive...</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Subscribe - $5/month", key="subscribe-button", type="primary", use_container_width=True):
                try:
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price': price_id,
                            'quantity': 1,
                        }],
                        mode='subscription',
                        success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url='https://your-domain.com/cancel',
                    )
                    
                    # Instead of JavaScript, use Streamlit's built-in link functionality
                    st.link_button("Click here to complete your subscription", checkout_session.url)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        break

# Remove the subscription section from sidebar
with st.sidebar:
    if st.session_state.is_subscribed:
        st.success("✅ Premium Member")

# CSS
st.markdown("""
    <style>
    .stMarkdown {
        max-width: 1800px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: flex !important;
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Add in your header area
col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    st.write("[Account](account)")