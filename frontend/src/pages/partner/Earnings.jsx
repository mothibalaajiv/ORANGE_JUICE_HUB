import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { Line } from 'react-chartjs-2';

const PartnerEarnings = () => {
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEarnings();
  }, []);

  const fetchEarnings = async () => {
    try {
      const response = await api.get('/partners/earnings');
      setEarnings(response.data);
    } catch (error) {
      console.error('Error fetching earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: earnings?.earningsChart?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Daily Earnings (₹)',
        data: earnings?.earningsChart?.map(d => d.amount) || [],
        borderColor: '#32CD32',
        backgroundColor: 'rgba(50, 205, 50, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Earnings Trend (Last 30 Days)',
      },
    },
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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">My Earnings</h1>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Earnings</p>
            <p className="text-4xl font-bold text-primary-orange">
              ₹{earnings?.totalEarnings?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Deliveries</p>
            <p className="text-4xl font-bold text-gray-900">{earnings?.totalDeliveries || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Average Per Delivery</p>
            <p className="text-4xl font-bold text-gray-900">
              ₹{earnings?.totalDeliveries > 0 
                ? (earnings.totalEarnings / earnings.totalDeliveries).toFixed(2) 
                : '0.00'}
            </p>
          </div>
        </div>

        {/* Earnings Chart */}
        <div className="bg-white rounded-lg shadow-card p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Earnings Over Time</h2>
          {earnings?.earningsChart && earnings.earningsChart.length > 0 ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📊</div>
              <p className="text-gray-600">No earnings data available yet</p>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Performance</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Rating</span>
                <span className="text-2xl font-bold text-yellow-500">
                  ★ {earnings?.rating?.toFixed(1) || '0.0'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Completed Deliveries</span>
                <span className="text-lg font-semibold text-gray-900">
                  {earnings?.totalDeliveries || 0}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Payment Info</h2>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p className="text-sm text-orange-800 mb-2">
                <strong>Earnings are deposited weekly</strong>
              </p>
              <p className="text-xs text-orange-700">
                Your earnings will be transferred to your registered bank account every Monday.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartnerEarnings;
