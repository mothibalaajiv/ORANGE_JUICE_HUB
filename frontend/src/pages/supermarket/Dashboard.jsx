import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const SupermarketDashboard = () => {
  const [supermarket, setSupermarket] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [pickupRequests, setPickupRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [supermarketRes, inventoryRes, pickupRes] = await Promise.all([
        api.get('/supermarkets/my-supermarket'),
        api.get('/supermarkets/inventory'),
        api.get('/supermarkets/pickup-requests'),
      ]);

      setSupermarket(supermarketRes.data);
      setInventory(inventoryRes.data.inventory);
      setPickupRequests(pickupRes.data.pickupRequests);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkReady = async (orderId) => {
    setActionLoading(prev => ({ ...prev, [orderId]: 'ready' }));
    try {
      await api.post(`/supermarkets/pickup-requests/${orderId}/ready`);
      await fetchData(); // Refresh data
    } catch (error) {
      console.error('Error marking ready:', error);
      alert(error.response?.data?.error || 'Failed to mark order as ready');
    } finally {
      setActionLoading(prev => ({ ...prev, [orderId]: null }));
    }
  };

  const handleRejectPickup = async (orderId) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    setActionLoading(prev => ({ ...prev, [orderId]: 'reject' }));
    try {
      await api.post(`/supermarkets/pickup-requests/${orderId}/reject`, { reason });
      await fetchData(); // Refresh data
    } catch (error) {
      console.error('Error rejecting pickup:', error);
      alert(error.response?.data?.error || 'Failed to reject pickup request');
    } finally {
      setActionLoading(prev => ({ ...prev, [orderId]: null }));
    }
  };

  const handleMarkOutForDelivery = async (orderId) => {
    setActionLoading(prev => ({ ...prev, [orderId]: 'out-for-delivery' }));
    try {
      await api.post(`/supermarkets/pickup-requests/${orderId}/mark-out-for-delivery`);
      await fetchData(); // Refresh data
    } catch (error) {
      console.error('Error marking out for delivery:', error);
      alert(error.response?.data?.error || 'Failed to mark order as out for delivery');
    } finally {
      setActionLoading(prev => ({ ...prev, [orderId]: null }));
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
              <h1 className="text-3xl font-bold mb-2">{supermarket?.name} 🏪</h1>
              <p className="text-white/90">Manage your inventory and track pickups</p>
            </div>
            {supermarket?.approved ? (
              <span className="bg-blue-500 px-4 py-2 rounded-full text-sm font-semibold">
                ✓ Approved
              </span>
            ) : (
              <span className="bg-yellow-500 px-4 py-2 rounded-full text-sm font-semibold">
                ⏳ Pending Approval
              </span>
            )}
          </div>
        </div>

        {!supermarket?.approved && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-6 py-4 rounded-lg mb-8">
            <p className="font-semibold mb-1">⏳ Supermarket Approval Pending</p>
            <p className="text-sm">
              Your supermarket is under review. Once approved, you can start managing inventory.
            </p>
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Products</p>
                <p className="text-2xl font-bold text-gray-900">{inventory.length}</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Pickup Requests</p>
                <p className="text-2xl font-bold text-gray-900">{pickupRequests.length}</p>
              </div>
              <div className="text-4xl">🚚</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Low Stock Items</p>
                <p className="text-2xl font-bold text-red-600">
                  {inventory.filter(i => i.quantity < 10).length}
                </p>
              </div>
              <div className="text-4xl">⚠️</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <Link to="/supermarket/inventory" className="block">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Manage Inventory</p>
                  <p className="text-primary-orange font-semibold">Go to Inventory →</p>
                </div>
                <div className="text-4xl">⚙️</div>
              </div>
            </Link>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Pickup Requests */}
          <div className="bg-white rounded-lg shadow-card">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Recent Pickups</h2>
            </div>
            <div className="p-6">
              {pickupRequests.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-5xl mb-3">📦</div>
                  <p className="text-gray-600">No pickup requests yet</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {pickupRequests.slice(0, 5).map((order) => (
                    <div key={order._id} className="p-4 bg-neutral-lightGray rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-900">
                          Order #{order._id.slice(-8).toUpperCase()}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          order.status === 'pickup_requested' 
                            ? 'bg-orange-100 text-orange-800'
                            : order.status === 'ready_for_pickup'
                            ? 'bg-green-100 text-green-800'
                            : order.status === 'picked_up'
                            ? 'bg-blue-100 text-blue-800'
                            : order.status === 'out_for_delivery'
                            ? 'bg-purple-100 text-purple-800'
                            : order.status === 'delivered'
                            ? 'bg-gray-100 text-gray-800'
                            : order.status === 'pickup_rejected'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {order.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {order.items.length} item(s) - ₹{order.totalAmount.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(order.createdAt).toLocaleString()}
                      </p>
                      
                      {/* Action Buttons */}
                      <div className="mt-3 flex space-x-2">
                        {order.status === 'pickup_requested' && (
                          <>
                            <button
                              onClick={() => handleMarkReady(order._id)}
                              disabled={actionLoading[order._id]}
                              className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white text-xs py-2 px-3 rounded font-medium transition"
                            >
                              {actionLoading[order._id] === 'ready' ? 'Processing...' : 'Mark Ready'}
                            </button>
                            <button
                              onClick={() => handleRejectPickup(order._id)}
                              disabled={actionLoading[order._id]}
                              className="flex-1 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white text-xs py-2 px-3 rounded font-medium transition"
                            >
                              {actionLoading[order._id] === 'reject' ? 'Processing...' : 'Reject'}
                            </button>
                          </>
                        )}
                        {order.status === 'picked_up' && (
                          <button
                            onClick={() => handleMarkOutForDelivery(order._id)}
                            disabled={actionLoading[order._id]}
                            className="w-full bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white text-xs py-2 px-3 rounded font-medium transition"
                          >
                            {actionLoading[order._id] === 'out-for-delivery' ? 'Processing...' : 'Mark Out for Delivery'}
                          </button>
                        )}
                        {(order.status === 'ready_for_pickup' || order.status === 'out_for_delivery' || order.status === 'delivered') && (
                          <div className="w-full text-center text-xs text-gray-500 py-2">
                            {order.status === 'ready_for_pickup' && 'Waiting for partner to collect'}
                            {order.status === 'out_for_delivery' && 'Order is out for delivery'}
                            {order.status === 'delivered' && 'Order completed'}
                          </div>
                        )}
                        {order.status === 'pickup_rejected' && (
                          <div className="w-full text-center text-xs text-red-600 py-2">
                            Pickup request rejected
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Low Stock Alert */}
          <div className="bg-white rounded-lg shadow-card">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Low Stock Alert</h2>
              <Link
                to="/supermarket/inventory"
                className="text-primary-orange hover:underline text-sm font-medium"
              >
                View All
              </Link>
            </div>
            <div className="p-6">
              {inventory.filter(i => i.quantity < 10).length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-5xl mb-3">✅</div>
                  <p className="text-gray-600">All products well stocked!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {inventory
                    .filter(i => i.quantity < 10)
                    .slice(0, 5)
                    .map((item) => (
                      <div key={item._id} className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div>
                          <p className="font-semibold text-gray-900">
                            {item.product?.name || 'Product'}
                          </p>
                          <p className="text-sm text-gray-600">
                            {item.product?.brandName || ''}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-red-600 font-bold">{item.quantity} left</p>
                          <p className="text-xs text-gray-500">Restock needed</p>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupermarketDashboard;
