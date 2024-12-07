from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Here you would:
        # 1. Get the customer ID
        customer_id = session.get('customer')
        # 2. Update your database to mark the user as subscribed
        # 3. Store subscription details
        
        print(f"�� Payment successful for customer: {customer_id}")
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        # Here you would:
        # 1. Mark the user's subscription as cancelled in your database
        print(f"❌ Subscription cancelled for customer: {customer_id}")

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=4242) 