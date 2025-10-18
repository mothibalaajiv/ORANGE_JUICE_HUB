import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../services/api';
import io from 'socket.io-client';

const OrderTracking = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrder();
    
    // Setup socket connection for real-time updates
    const socket = io(process.env.REACT_APP_API_URL.replace('/api', ''));
    
    socket.on(`order_update_${orderId}`, (data) => {
      console.log('Order update received:', data);
      fetchOrder(); // Refresh order data
    });

    socket.on(`partner_location_${orderId}`, (data) => {
      console.log('Partner location update:', data);
      // Update partner location on map (if implemented)
    });

    return () => {
      socket.disconnect();
    };
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      const response = await api.get(`/orders/${orderId}`);
      setOrder(response.data);
    } catch (error) {
      console.error('Error fetching order:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusSteps = () => {
    return [
      { key: 'awaiting_partner_assignment', label: 'Order Placed', icon: '📦' },
      { key: 'partner_assigned', label: 'Partner Assigned', icon: '🚴' },
      { key: 'preparing', label: 'Preparing Order', icon: '⏳' }, // Groups partner_accepted, pickup_requested, ready_for_pickup
      { key: 'picked_up', label: 'Picked Up', icon: '✅' },
      { key: 'out_for_delivery', label: 'Out for Delivery', icon: '🚚' },
      { key: 'delivered', label: 'Delivered', icon: '🎉' },
    ];
  };

  const getCurrentStepIndex = () => {
    if (!order) return 0;
    const orderStatus = order.status;
    
    // Map internal statuses to customer-facing steps
    if (['awaiting_partner_assignment'].includes(orderStatus)) return 0;
    if (['partner_assigned'].includes(orderStatus)) return 1;
    if (['partner_accepted', 'pickup_requested', 'ready_for_pickup', 'pickup_rejected'].includes(orderStatus)) return 2;
    if (['picked_up'].includes(orderStatus)) return 3;
    if (['out_for_delivery'].includes(orderStatus)) return 4;
    if (['delivered'].includes(orderStatus)) return 5;
    
    return 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-orange"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😕</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Order not found</h2>
          <Link to="/user" className="text-primary-orange hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const currentStep = getCurrentStepIndex();
  const steps = getStatusSteps();

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <Link to="/user" className="text-primary-orange hover:underline text-sm mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Track Your Order</h1>
          <p className="text-gray-600">Order #{order._id.slice(-8).toUpperCase()}</p>
        </div>

        {/* Status Timeline */}
        <div className="bg-white rounded-lg shadow-card p-8 mb-6">
          <div className="relative">
            {/* Progress Line */}
            <div className="absolute top-8 left-0 right-0 h-1 bg-gray-200">
              <div
                className="h-full bg-primary-orange transition-all duration-500"
                style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
              ></div>
            </div>

            {/* Status Steps */}
            <div className="relative flex justify-between">
              {steps.map((step, index) => (
                <div key={step.key} className="flex flex-col items-center" style={{ width: '16.66%' }}>
                  <div
                    className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl mb-3 transition-all ${
                      index <= currentStep
                        ? 'bg-primary-orange text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    {step.icon}
                  </div>
                  <p className={`text-xs text-center font-medium ${
                    index <= currentStep ? 'text-gray-900' : 'text-gray-400'
                  }`}>
                    {step.label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Order Details */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Details</h2>
            
            <div className="space-y-4">
              {order.items.map((item, index) => (
                <div key={index} className="flex justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-sm text-gray-600">Qty: {item.qty}</p>
                  </div>
                  <p className="font-semibold text-gray-900">
                    ₹{(item.unitPrice * item.qty).toFixed(2)}
                  </p>
                </div>
              ))}
              
              <div className="border-t border-gray-200 pt-4 space-y-2">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>₹{order.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Delivery Fee</span>
                  <span>₹{order.deliveryFee.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>₹{order.tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold text-gray-900 pt-2 border-t border-gray-200">
                  <span>Total</span>
                  <span>₹{order.totalAmount.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Delivery Info */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Delivery Address</h2>
              <p className="text-gray-700">{order.deliveryAddress}</p>
            </div>

            {order.partner && (
              <div className="bg-white rounded-lg shadow-card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Delivery Partner</h2>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-primary-orange rounded-full flex items-center justify-center text-white text-xl font-bold">
                    {order.partner.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{order.partner.name}</p>
                    <p className="text-sm text-gray-600">{order.partner.vehicleType}</p>
                    <p className="text-sm text-gray-600">{order.partner.phone}</p>
                    <div className="flex items-center mt-1">
                      <span className="text-yellow-500">★</span>
                      <span className="text-sm text-gray-600 ml-1">
                        {order.partner.rating.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {order.supermarket && (
              <div className="bg-white rounded-lg shadow-card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Pickup Location</h2>
                <div>
                  <p className="font-semibold text-gray-900">{order.supermarket.name}</p>
                  <p className="text-sm text-gray-600">{order.supermarket.address}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Order Timeline/Logs */}
        {order.logs && order.logs.length > 0 && (
          <div className="bg-white rounded-lg shadow-card p-6 mt-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Timeline</h2>
            <div className="space-y-4">
              {order.logs.slice().reverse().map((log, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 bg-primary-orange rounded-full mt-2"></div>
                  <div className="flex-grow">
                    <p className="font-medium text-gray-900">{log.note}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(log.timestamp).toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTracking;
