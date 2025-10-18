"""
Assignment Service - Handles delivery partner assignment with 5-minute timeout
"""
from app import get_db, socketio
from app.utils.geo import find_nearest_partners
from app.models.order import Order
from bson import ObjectId
from datetime import datetime
import threading


assignment_timers = {}  # Store active timers: {order_id: timer}


def start_partner_assignment(order_id):
    """
    Start the partner assignment flow for an order
    This function initiates the sequential assignment process
    """
    try:
        db = get_db()
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        
        if not order:
            print(f"Order {order_id} not found")
            return
        
        # Get order delivery location
        delivery_location = order.get('deliveryLocation', {}).get('coordinates', [0, 0])
        
        # If delivery location is default [0,0], find all available partners
        # Otherwise, find nearest available partners (within 100km for broader coverage)
        if delivery_location == [0, 0]:
            print(f"Using default coordinates, finding all available partners")
            partners = list(db.delivery_partners.find({'status': 'available'}).limit(20))
        else:
            # Try with 100km radius first, then fallback to all available partners
            partners = find_nearest_partners(db, delivery_location, radius=100000, limit=20)
            if not partners:
                print(f"No partners found within 100km, finding all available partners")
                partners = list(db.delivery_partners.find({'status': 'available'}).limit(20))
        
        if not partners:
            print(f"No available partners found for order {order_id}")
            # Update order with error status
            db.orders.update_one(
                {'_id': ObjectId(order_id)},
                {'$set': {'status': 'no_partner_available', 'updatedAt': datetime.utcnow()}}
            )
            Order.add_log(order_id, db, 'no_partner_available', 'No delivery partners available')
            return
        
        # Create assignment log
        assignment_log = {
            'orderId': ObjectId(order_id),
            'attempts': [],
            'finalAssignedPartnerId': None,
            'createdAt': datetime.utcnow()
        }
        result = db.assignment_logs.insert_one(assignment_log)
        assignment_log_id = result.inserted_id
        
        # Start sequential assignment with first partner
        _attempt_assignment(order_id, partners, 0, assignment_log_id)
        
    except Exception as e:
        print(f"Error starting partner assignment: {str(e)}")


def _attempt_assignment(order_id, partners_list, current_index, assignment_log_id):
    """
    Attempt to assign order to a partner
    If timeout or rejection, try next partner
    """
    try:
        db = get_db()
        
        # Check if we've exhausted all partners
        if current_index >= len(partners_list):
            print(f"All partners exhausted for order {order_id}")
            db.orders.update_one(
                {'_id': ObjectId(order_id)},
                {'$set': {'status': 'no_partner_available', 'updatedAt': datetime.utcnow()}}
            )
            Order.add_log(order_id, db, 'no_partner_available', 'All delivery partners rejected or timed out')
            return
        
        partner = partners_list[current_index]
        partner_id = partner['_id']
        
        print(f"Attempting to assign order {order_id} to partner {partner_id}")
        
        # Update order with partner assignment
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'assignedPartnerId': partner_id,
                    'partnerAssignedAt': datetime.utcnow(),
                    'partnerAccepted': False,
                    'status': Order.STATUS_PARTNER_ASSIGNED,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Update partner status to busy (tentatively) and set current order
        db.delivery_partners.update_one(
            {'_id': partner_id},
            {'$set': {'status': 'busy', 'currentOrderId': ObjectId(order_id)}}
        )
        
        # Log attempt
        attempt_record = {
            'partnerId': partner_id,
            'assignedAt': datetime.utcnow(),
            'expiredAt': None,
            'accepted': None
        }
        db.assignment_logs.update_one(
            {'_id': assignment_log_id},
            {'$push': {'attempts': attempt_record}}
        )
        
        Order.add_log(order_id, db, Order.STATUS_PARTNER_ASSIGNED, f'Assigned to partner (5-minute acceptance window)')
        
        # Send notification to partner via WebSocket
        _notify_partner_assignment(partner_id, order_id)
        
        # Start 5-minute timer
        timer = threading.Timer(300.0, _handle_assignment_timeout, args=[order_id, partner_id, partners_list, current_index, assignment_log_id])
        timer.start()
        assignment_timers[str(order_id)] = timer
        
    except Exception as e:
        print(f"Error in assignment attempt: {str(e)}")


def _handle_assignment_timeout(order_id, partner_id, partners_list, current_index, assignment_log_id):
    """
    Handle timeout when partner doesn't accept within 5 minutes
    """
    try:
        db = get_db()
        
        # Check if partner has accepted
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if order and order.get('partnerAccepted'):
            print(f"Partner {partner_id} has already accepted order {order_id}")
            return
        
        print(f"Assignment timeout for order {order_id}, partner {partner_id}")
        
        # Update assignment log
        db.assignment_logs.update_one(
            {'_id': assignment_log_id, 'attempts.partnerId': partner_id},
            {
                '$set': {
                    'attempts.$.expiredAt': datetime.utcnow(),
                    'attempts.$.accepted': False
                }
            }
        )
        
        # Free up the partner
        db.delivery_partners.update_one(
            {'_id': partner_id},
            {'$set': {'status': 'available'}}
        )
        
        Order.add_log(order_id, db, 'partner_timeout', f'Partner did not accept within 5 minutes')
        
        # Try next partner
        _attempt_assignment(order_id, partners_list, current_index + 1, assignment_log_id)
        
    except Exception as e:
        print(f"Error handling timeout: {str(e)}")


def accept_partner_assignment(order_id, partner_id):
    """
    Partner accepts the assignment
    Returns True if successful, False otherwise
    """
    try:
        db = get_db()
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return False, "Order not found"
        
        # Verify partner is assigned
        if str(order.get('assignedPartnerId')) != str(partner_id):
            return False, "Not assigned to this order"
        
        # Check if already accepted
        if order.get('partnerAccepted'):
            return False, "Order already accepted"
        
        # Accept the assignment
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'partnerAccepted': True,
                    'partnerAcceptedAt': datetime.utcnow(),
                    'status': Order.STATUS_PARTNER_ACCEPTED,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Update partner
        db.delivery_partners.update_one(
            {'_id': ObjectId(partner_id)},
            {'$set': {'currentOrderId': ObjectId(order_id), 'status': 'busy'}}
        )
        
        # Cancel timer
        timer_key = str(order_id)
        if timer_key in assignment_timers:
            assignment_timers[timer_key].cancel()
            del assignment_timers[timer_key]
        
        # Update assignment log
        assignment_log = db.assignment_logs.find_one({'orderId': ObjectId(order_id)})
        if assignment_log:
            db.assignment_logs.update_one(
                {'_id': assignment_log['_id'], 'attempts.partnerId': ObjectId(partner_id)},
                {
                    '$set': {
                        'attempts.$.accepted': True,
                        'finalAssignedPartnerId': ObjectId(partner_id)
                    }
                }
            )
        
        Order.add_log(order_id, db, 'partner_accepted', 'Delivery partner accepted the order')
        
        # Notify user via WebSocket
        socketio.emit(f'order_update_{order_id}', {
            'status': 'partner_accepted',
            'message': 'Delivery partner has been assigned'
        })
        
        print(f"Partner {partner_id} accepted order {order_id}")
        return True, "Assignment accepted"
        
    except Exception as e:
        print(f"Error accepting assignment: {str(e)}")
        return False, str(e)


def reject_partner_assignment(order_id, partner_id):
    """
    Partner rejects the assignment
    """
    try:
        db = get_db()
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return False, "Order not found"
        
        # Verify partner is assigned
        if str(order.get('assignedPartnerId')) != str(partner_id):
            return False, "Not assigned to this order"
        
        # Get assignment log
        assignment_log = db.assignment_logs.find_one({'orderId': ObjectId(order_id)})
        if not assignment_log:
            return False, "Assignment log not found"
        
        # Update assignment log
        db.assignment_logs.update_one(
            {'_id': assignment_log['_id'], 'attempts.partnerId': ObjectId(partner_id)},
            {'$set': {'attempts.$.accepted': False, 'attempts.$.expiredAt': datetime.utcnow()}}
        )
        
        # Free up the partner
        db.delivery_partners.update_one(
            {'_id': ObjectId(partner_id)},
            {'$set': {'status': 'available'}}
        )
        
        Order.add_log(order_id, db, 'partner_rejected', 'Partner rejected the order')
        
        # Cancel timer
        timer_key = str(order_id)
        if timer_key in assignment_timers:
            assignment_timers[timer_key].cancel()
            del assignment_timers[timer_key]
        
        # Get partners list and find current index
        delivery_location = order.get('deliveryLocation', {}).get('coordinates', [0, 0])
        partners = find_nearest_partners(db, delivery_location, radius=10000, limit=20)
        
        # Find current partner index
        current_index = 0
        for i, p in enumerate(partners):
            if str(p['_id']) == str(partner_id):
                current_index = i
                break
        
        # Try next partner
        _attempt_assignment(order_id, partners, current_index + 1, assignment_log['_id'])
        
        return True, "Assignment rejected, trying next partner"
        
    except Exception as e:
        print(f"Error rejecting assignment: {str(e)}")
        return False, str(e)


def _notify_partner_assignment(partner_id, order_id):
    """
    Send notification to partner about new assignment
    """
    try:
        # Emit WebSocket event to specific partner
        socketio.emit(f'new_assignment_{partner_id}', {
            'orderId': str(order_id),
            'message': 'New delivery assignment',
            'expiresIn': 300  # 5 minutes
        })
        print(f"Sent assignment notification to partner {partner_id}")
    except Exception as e:
        print(f"Error sending partner notification: {str(e)}")
