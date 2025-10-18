import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
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
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg shadow-card p-8 mb-8">
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard 👑</h1>
          <p className="text-white/90">Manage and monitor the entire platform</p>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Users</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.totalUsers || 0}</p>
              </div>
              <div className="text-4xl">👥</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Orders</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.totalOrders || 0}</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Revenue</p>
                <p className="text-3xl font-bold text-primary-orange">
                  ₹{stats?.totalRevenue?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="text-4xl">💰</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Active Partners</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.activePartners || 0}</p>
              </div>
              <div className="text-4xl">🚴</div>
            </div>
          </div>
        </div>

        {/* Platform Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Brands</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total</span>
                <span className="font-bold text-gray-900">{stats?.totalBrands || 0}</span>
              </div>
              {stats?.pendingApprovals?.brands > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-yellow-600">Pending Approval</span>
                  <span className="font-bold text-yellow-600">
                    {stats.pendingApprovals.brands}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Products</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total</span>
                <span className="font-bold text-gray-900">{stats?.totalProducts || 0}</span>
              </div>
              {stats?.pendingApprovals?.products > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-yellow-600">Pending Approval</span>
                  <span className="font-bold text-yellow-600">
                    {stats.pendingApprovals.products}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Supermarkets</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total</span>
                <span className="font-bold text-gray-900">{stats?.totalSupermarkets || 0}</span>
              </div>
              {stats?.pendingApprovals?.supermarkets > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-yellow-600">Pending Approval</span>
                  <span className="font-bold text-yellow-600">
                    {stats.pendingApprovals.supermarkets}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Link
            to="/admin/approvals"
            className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6 hover:border-yellow-300 transition"
          >
            <div className="flex items-center space-x-4">
              <div className="text-5xl">⏳</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Pending Approvals
                </h3>
                <p className="text-sm text-gray-600">
                  {(stats?.pendingApprovals?.brands || 0) + 
                   (stats?.pendingApprovals?.products || 0) + 
                   (stats?.pendingApprovals?.supermarkets || 0)} items
                </p>
              </div>
            </div>
          </Link>

          <Link
            to="/admin/orders"
            className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 hover:border-blue-300 transition"
          >
            <div className="flex items-center space-x-4">
              <div className="text-5xl">📦</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Manage Orders</h3>
                <p className="text-sm text-gray-600">View and manage all orders</p>
              </div>
            </div>
          </Link>

          <Link
            to="/admin/users"
            className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 hover:border-blue-300 transition"
          >
            <div className="flex items-center space-x-4">
              <div className="text-5xl">👥</div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Manage Users</h3>
                <p className="text-sm text-gray-600">View all platform users</p>
              </div>
            </div>
          </Link>
        </div>

        {/* Recent Orders */}
        <div className="bg-white rounded-lg shadow-card">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Recent Orders</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {stats?.recentOrders && stats.recentOrders.length > 0 ? (
              stats.recentOrders.map((order) => (
                <div key={order._id} className="p-6 hover:bg-gray-50 transition">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">
                        Order #{order._id.slice(-8).toUpperCase()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {order.items.length} items - ₹{order.totalAmount.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(order.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      order.status === 'delivered' 
                        ? 'bg-blue-100 text-blue-800'
                        : order.status === 'cancelled'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center text-gray-600">
                No recent orders
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
