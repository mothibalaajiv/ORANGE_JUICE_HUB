import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import io from 'socket.io-client';

const PartnerDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [currentOrder, setCurrentOrder] = useState(null);
  const [pendingAssignment, setPendingAssignment] = useState(null);
  const [supermarkets, setSupermarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pickupLoading, setPickupLoading] = useState(false);
  const [pickupMessage, setPickupMessage] = useState('');

  useEffect(() => {
    fetchProfile();

    // Setup socket for real-time assignments
    const socket = io(process.env.REACT_APP_API_URL.replace('/api', ''));
    
    socket.on('connect', () => {
      console.log('Socket connected for partner');
    });

    // Listen for new assignments
    if (profile) {
      socket.on(`new_assignment_${profile._id}`, async (data) => {
        console.log('New assignment received:', data);
        setPendingAssignment(data);
        // Fetch order details
        try {
          const response = await api.get(`/orders/${data.orderId}`);
          setCurrentOrder(response.data);
        } catch (error) {
          console.error('Error fetching order:', error);
        }
      });
    }

    return () => {
      socket.disconnect();
    };
  }, [profile?._id]);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/partners/profile');
      setProfile(response.data);

      // If partner has active order, fetch it
      if (response.data.currentOrderId) {
        const orderRes = await api.get(`/orders/${response.data.currentOrderId}`);
        setCurrentOrder(orderRes.data);
        
        // Fetch nearby supermarkets for assigned or accepted orders
        if (orderRes.data.status === 'partner_assigned' || orderRes.data.status === 'partner_accepted') {
          fetchNearbySupermarkets();
        }
      } else {
        // Fallback: Check if there are any assigned orders even if currentOrderId is not set
        try {
          const assignedOrdersRes = await api.get('/partners/assigned-orders');
          if (assignedOrdersRes.data.length > 0) {
            const latestOrder = assignedOrdersRes.data[0]; // Get the most recent one
            setCurrentOrder(latestOrder);
            if (latestOrder.status === 'partner_assigned' || latestOrder.status === 'partner_accepted') {
              fetchNearbySupermarkets();
            }
          }
        } catch (error) {
          console.log('No assigned orders found');
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNearbySupermarkets = async () => {
    try {
      const response = await api.get('/partners/nearby-supermarkets');
      setSupermarkets(response.data.supermarkets);
    } catch (error) {
      console.error('Error fetching supermarkets:', error);
    }
  };

  const handleStatusChange = async (status) => {
    try {
      await api.put('/partners/status', { status });
      fetchProfile();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleAcceptAssignment = async (orderId) => {
    try {
      await api.post(`/partners/assignment/${orderId}/accept`);
      setPendingAssignment(null);
      
      // Fetch updated profile and order details
      await fetchProfile();
      
      // Fetch nearby supermarkets after accepting
      setTimeout(() => {
        fetchNearbySupermarkets();
      }, 1000); // Small delay to ensure order status is updated
      
    } catch (error) {
      console.error('Error accepting assignment:', error);
      alert(error.response?.data?.error || 'Failed to accept assignment');
    }
  };

  const handleRejectAssignment = async (orderId) => {
    try {
      await api.post(`/partners/assignment/${orderId}/reject`);
      setPendingAssignment(null);
      setCurrentOrder(null);
    } catch (error) {
      console.error('Error rejecting assignment:', error);
    }
  };

  const handlePickup = async (supermarketId) => {
    if (pickupLoading) return; // Prevent multiple clicks
    
    setPickupLoading(true);
    setPickupMessage('');
    
    try {
      const response = await api.post(`/orders/${currentOrder._id}/picked-up`, { supermarketId });
      
      // Show success message
      setPickupMessage('Pickup requested from supermarket! Waiting for store confirmation.');
      
      // Refresh profile and order details
      await fetchProfile();
      
      // Clear message after 3 seconds
      setTimeout(() => setPickupMessage(''), 3000);
      
    } catch (error) {
      console.error('Error marking pickup:', error);
      setPickupMessage(error.response?.data?.error || 'Failed to mark order as picked up');
      
      // Clear error message after 5 seconds
      setTimeout(() => setPickupMessage(''), 5000);
    } finally {
      setPickupLoading(false);
    }
  };

  const handleCollected = async () => {
    try {
      await api.post(`/orders/${currentOrder._id}/collected`);
      setPickupMessage('Order collected successfully! Store will mark it out for delivery.');
      setTimeout(() => setPickupMessage(''), 3000);
      fetchProfile();
    } catch (error) {
      console.error('Error marking collected:', error);
      setPickupMessage('Failed to mark order as collected');
      setTimeout(() => setPickupMessage(''), 5000);
    }
  };

  const handleOutForDelivery = async () => {
    try {
      await api.post(`/orders/${currentOrder._id}/out-for-delivery`);
      fetchProfile();
    } catch (error) {
      console.error('Error marking out for delivery:', error);
    }
  };

  const handleDelivered = async () => {
    try {
      await api.post(`/orders/${currentOrder._id}/delivered`);
      setCurrentOrder(null);
      setSupermarkets([]);
      fetchProfile();
    } catch (error) {
      console.error('Error marking delivered:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-orange"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-orange to-secondary-darkOrange text-white rounded-lg shadow-card p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Delivery Partner Dashboard 🚴</h1>
              <p className="text-white/90">Manage deliveries and track earnings</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={profile?.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                disabled={profile?.currentOrderId}
                className="px-4 py-2 rounded-lg font-semibold text-gray-900 disabled:opacity-50"
              >
                <option value="available">Available</option>
                <option value="offline">Offline</option>
              </select>
            </div>
          </div>
        </div>

        {/* Pending Assignment Modal */}
        {(pendingAssignment || (currentOrder && currentOrder.status === 'partner_assigned' && !currentOrder.partnerAccepted)) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6 animate-slide-in">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">🚨 New Delivery Request!</h2>
              <p className="text-gray-600 mb-4">
                You have been assigned a new delivery. You have <strong>5 minutes</strong> to accept.
              </p>
              {currentOrder && (
                <div className="bg-neutral-lightGray rounded-lg p-4 mb-6">
                  <p className="text-sm text-gray-600 mb-2">Order Details:</p>
                  <p className="font-semibold text-gray-900">
                    {currentOrder.items.length} item(s) - ₹{currentOrder.totalAmount}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Delivery to: {currentOrder.deliveryAddress}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Order ID: #{currentOrder._id.slice(-8).toUpperCase()}
                  </p>
                </div>
              )}
              <div className="flex space-x-3">
                <button
                  onClick={() => handleAcceptAssignment(currentOrder._id)}
                  className="flex-1 bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
                >
                  Accept
                </button>
                <button
                  onClick={() => handleRejectAssignment(currentOrder._id)}
                  className="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold hover:bg-red-600 transition"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Deliveries</p>
            <p className="text-3xl font-bold text-gray-900">{profile?.totalDeliveries || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Earnings</p>
            <p className="text-3xl font-bold text-primary-orange">₹{profile?.totalEarnings?.toFixed(2) || '0.00'}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Rating</p>
            <p className="text-3xl font-bold text-gray-900">★ {profile?.rating?.toFixed(1) || '0.0'}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Status</p>
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
              profile?.status === 'available' 
                ? 'bg-blue-100 text-blue-800' 
                : profile?.status === 'busy'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {profile?.status}
            </span>
          </div>
        </div>

        {/* Pickup Message */}
        {pickupMessage && (
          <div className={`mb-4 p-4 rounded-lg ${
            pickupMessage.includes('successfully') 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {pickupMessage}
          </div>
        )}

        {/* Current Order */}
        {currentOrder ? (
          <div className="bg-white rounded-lg shadow-card p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Current Delivery</h2>
            
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Order Details</h3>
                <div className="space-y-2">
                  <p className="text-gray-600">Order ID: #{currentOrder._id.slice(-8).toUpperCase()}</p>
                  <p className="text-gray-600">Items: {currentOrder.items.length}</p>
                  <p className="text-gray-600">Amount: ₹{currentOrder.totalAmount}</p>
                  <p className="text-gray-600">Status: {currentOrder.status}</p>
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Delivery Address</h3>
                <p className="text-gray-700">{currentOrder.deliveryAddress}</p>
                {currentOrder.customerNotes && (
                  <p className="text-sm text-gray-600 mt-2">Note: {currentOrder.customerNotes}</p>
                )}
              </div>
            </div>

            {/* Nearby Supermarkets */}
            {(currentOrder.status === 'partner_assigned' || currentOrder.status === 'partner_accepted') && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">📍 Nearby Supermarkets</h3>
                {supermarkets.length > 0 ? (
                  <div className="grid md:grid-cols-2 gap-4">
                    {supermarkets.map((supermarket) => (
                    <div key={supermarket._id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-semibold text-gray-900">{supermarket.name}</p>
                          <p className="text-sm text-gray-600">{supermarket.address}</p>
                          <p className="text-sm text-primary-orange font-medium mt-1">
                            {supermarket.distance}m away
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {supermarket.inventoryItems || 0} items available
                          </p>
                        </div>
                      </div>
                      
                      {/* Show order items that are available at this supermarket */}
                      <div className="mt-3 mb-3">
                        <p className="text-xs text-gray-600 mb-2">Available Products:</p>
                        <div className="space-y-1">
                          {currentOrder.items.map((item, index) => (
                            <div key={index} className="flex justify-between text-xs">
                              <span className="text-gray-700">{item.qty}x {item.name || 'Product'}</span>
                              <span className="text-green-600">✓ In Stock</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <button
                        onClick={() => handlePickup(supermarket._id)}
                        disabled={pickupLoading}
                        className={`w-full py-2 rounded-lg font-medium transition ${
                          pickupLoading 
                            ? 'bg-gray-400 cursor-not-allowed' 
                            : 'bg-primary-orange hover:bg-secondary-darkOrange'
                        } text-white`}
                      >
                        {pickupLoading ? 'Processing...' : 'Pick from here'}
                      </button>
                    </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <div className="text-yellow-600 mr-3">⚠️</div>
                      <div>
                        <p className="text-yellow-800 font-medium">No supermarkets found</p>
                        <p className="text-yellow-700 text-sm">No nearby supermarkets have all the required products in stock.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4">
              {currentOrder.status === 'ready_for_pickup' && (
                <button
                  onClick={handleCollected}
                  className="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition"
                >
                  Mark as Collected
                </button>
              )}
              {currentOrder.status === 'picked_up' && (
                <div className="flex-1 bg-yellow-100 text-yellow-800 py-3 rounded-lg font-semibold text-center">
                  Waiting for store to mark as "Out for Delivery"
                </div>
              )}
              {currentOrder.status === 'out_for_delivery' && (
                <button
                  onClick={handleDelivered}
                  className="flex-1 bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
                >
                  Mark as Delivered
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-card p-12 text-center">
            <div className="text-6xl mb-4">🚴</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Active Delivery</h3>
            <p className="text-gray-600">
              {profile?.status === 'available' 
                ? 'Waiting for new delivery assignments...' 
                : 'Set your status to Available to receive orders'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PartnerDashboard;
