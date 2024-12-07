import streamlit as st
import stripe
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
stripe.api_key = st.secrets['STRIPE_SECRET_KEY']

st.set_page_config(page_title="Subscription Management", page_icon="��")

# Page Header
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>Subscription Management</h1>
    </div>
""", unsafe_allow_html=True)

# Subscription Management
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.session_state.get('is_subscribed', False):
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2>✅ Active Premium Subscription</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Manage Subscription", type="primary"):
            try:
                # Create Stripe Customer Portal session
                portal_session = stripe.billing_portal.Session.create(
                    customer=st.session_state.get('customer_id'),  # This will be set by webhook
                    return_url='http://localhost:8501/account'
                )
                st.markdown(f'''
                    <script>
                        window.location.href = '{portal_session.url}';
                    </script>
                ''', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2>💎 Premium Access</h2>
                <p style="margin: 1rem 0;">Get unlimited access to all WSB trade analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Subscribe - $9.99/month", type="primary"):
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': os.getenv('STRIPE_PRICE_ID'),
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url='http://localhost:8501/account?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url='http://localhost:8501/account'
                )
                
                st.markdown(f'''
                    <script>
                        window.location.href = '{checkout_session.url}';
                    </script>
                ''', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}") 