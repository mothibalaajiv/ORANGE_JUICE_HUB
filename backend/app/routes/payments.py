from flask import Blueprint, request, jsonify
import razorpay
from app import get_db
from app.utils.auth import token_required, get_current_user_id
from app.services.assignment_service import start_partner_assignment
from bson import ObjectId
from datetime import datetime
import hmac
import hashlib
import os

payments_bp = Blueprint('payments', __name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.getenv('RAZORPAY_KEY_ID', 'rzp_test_key'),
    os.getenv('RAZORPAY_KEY_SECRET', 'secret')
))


@payments_bp.route('/razorpay/create-order', methods=['POST'])
@token_required
def create_razorpay_order():
    """Create a Razorpay order"""
    try:
        db = get_db()
        data = request.get_json()
        
        order_id = data.get('orderId')
        if not order_id:
            return jsonify({'error': 'orderId is required'}), 400
        
        # Get order from database
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify ownership
        user_id = get_current_user_id()
        if str(order['userId']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Create Razorpay order
        amount_in_paise = int(order['totalAmount'] * 100)  # Convert to paise
        
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': str(order_id),
            'payment_capture': 1  # Auto capture
        })
        
        # Save payment record
        payment_data = {
            'orderId': ObjectId(order_id),
            'razorpayOrderId': razorpay_order['id'],
            'razorpayPaymentId': None,
            'status': 'pending',
            'amount': order['totalAmount'],
            'currency': 'INR',
            'createdAt': datetime.utcnow()
        }
        db.payments.insert_one(payment_data)
        
        return jsonify({
            'razorpayOrderId': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key': os.getenv('RAZORPAY_KEY_ID')
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/razorpay/verify', methods=['POST'])
@token_required
def verify_razorpay_payment():
    """Verify Razorpay payment signature"""
    try:
        db = get_db()
        data = request.get_json()
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'error': 'Missing payment verification data'}), 400
        
        # Verify signature
        secret = os.getenv('RAZORPAY_KEY_SECRET', 'secret')
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Update payment record
        payment = db.payments.find_one({'razorpayOrderId': razorpay_order_id})
        if not payment:
            return jsonify({'error': 'Payment record not found'}), 404
        
        db.payments.update_one(
            {'_id': payment['_id']},
            {
                '$set': {
                    'razorpayPaymentId': razorpay_payment_id,
                    'razorpaySignature': razorpay_signature,
                    'status': 'paid',
                    'paidAt': datetime.utcnow()
                }
            }
        )
        
        # Update order payment status
        order_id = payment['orderId']
        db.orders.update_one(
            {'_id': order_id},
            {
                '$set': {
                    'paymentStatus': 'paid',
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        from app.models.order import Order
        Order.add_log(order_id, db, 'payment_completed', 'Payment completed successfully')
        
        # Trigger partner assignment
        start_partner_assignment(str(order_id))
        
        return jsonify({
            'message': 'Payment verified successfully',
            'status': 'paid'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/razorpay/webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    try:
        db = get_db()
        data = request.get_json()
        
        # Verify webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
        
        if webhook_secret:
            # Verify signature
            body = request.get_data()
            expected_signature = hmac.new(
                webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if webhook_signature != expected_signature:
                return jsonify({'error': 'Invalid webhook signature'}), 400
        
        # Process webhook event
        event = data.get('event')
        payload = data.get('payload', {})
        
        if event == 'payment.captured':
            # Payment successful
            payment_entity = payload.get('payment', {}).get('entity', {})
            razorpay_order_id = payment_entity.get('order_id')
            razorpay_payment_id = payment_entity.get('id')
            
            if razorpay_order_id:
                # Update payment and order
                payment = db.payments.find_one({'razorpayOrderId': razorpay_order_id})
                if payment:
                    db.payments.update_one(
                        {'_id': payment['_id']},
                        {'$set': {'razorpayPaymentId': razorpay_payment_id, 'status': 'paid'}}
                    )
                    
                    db.orders.update_one(
                        {'_id': payment['orderId']},
                        {'$set': {'paymentStatus': 'paid'}}
                    )
                    
                    # Trigger partner assignment
                    start_partner_assignment(str(payment['orderId']))
        
        elif event == 'payment.failed':
            # Payment failed
            payment_entity = payload.get('payment', {}).get('entity', {})
            razorpay_order_id = payment_entity.get('order_id')
            
            if razorpay_order_id:
                payment = db.payments.find_one({'razorpayOrderId': razorpay_order_id})
                if payment:
                    db.payments.update_one(
                        {'_id': payment['_id']},
                        {'$set': {'status': 'failed'}}
                    )
                    
                    db.orders.update_one(
                        {'_id': payment['orderId']},
                        {'$set': {'paymentStatus': 'failed'}}
                    )
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500
