import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const BrandAnalytics = () => {
  const [brand, setBrand] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const brandRes = await api.get('/brands/my-brand');
      setBrand(brandRes.data);

      if (brandRes.data.approved) {
        const insightsRes = await api.get(
          `/analytics/brands/${brandRes.data._id}/insights?start=${dateRange.start}&end=${dateRange.end}`
        );
        setInsights(insightsRes.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await api.get(
        `/analytics/brands/${brand._id}/insights/export?format=${format}&start=${dateRange.start}&end=${dateRange.end}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${brand.name}_insights_${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  const chartData = {
    labels: insights?.salesByDate?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Sales (₹)',
        data: insights?.salesByDate?.map(d => d.sales) || [],
        borderColor: '#FFA500',
        backgroundColor: 'rgba(255, 165, 0, 0.1)',
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
        text: 'Sales Over Time',
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

  if (!brand?.approved) {
    return (
      <div className="min-h-screen bg-neutral-lightGray py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-card p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Analytics Not Available</h2>
            <p className="text-gray-600">
              Your brand needs to be approved before you can access analytics.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
            <p className="text-gray-600 mt-1">Track your brand performance</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handleExport('csv')}
              className="bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition text-sm"
            >
              Export CSV
            </button>
            <button
              onClick={() => handleExport('xlsx')}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 transition text-sm"
            >
              Export Excel
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition text-sm"
            >
              Export PDF
            </button>
          </div>
        </div>

        {/* Date Range Filter */}
        <div className="bg-white rounded-lg shadow-card p-6 mb-6">
          <div className="grid md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
              />
            </div>
            <button
              onClick={fetchData}
              className="bg-primary-orange text-white px-6 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition"
            >
              Apply Filter
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Sales</p>
            <p className="text-3xl font-bold text-primary-orange">
              ₹{insights?.totalSales?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Total Orders</p>
            <p className="text-3xl font-bold text-gray-900">{insights?.totalOrders || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Units Sold</p>
            <p className="text-3xl font-bold text-gray-900">{insights?.totalUnits || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <p className="text-gray-600 text-sm mb-1">Avg Order Value</p>
            <p className="text-3xl font-bold text-gray-900">
              ₹{insights?.averageOrderValue?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        {/* Sales Chart */}
        <div className="bg-white rounded-lg shadow-card p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Sales Trend</h2>
          {insights?.salesByDate && insights.salesByDate.length > 0 ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">No sales data available for this period</p>
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Top Products */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top Performing Products</h2>
            {insights?.topProducts && insights.topProducts.length > 0 ? (
              <div className="space-y-4">
                {insights.topProducts.map((product, index) => (
                  <div key={product.productId} className="flex items-center justify-between p-4 bg-neutral-lightGray rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                      <div>
                        <p className="font-semibold text-gray-900">{product.name}</p>
                        <p className="text-sm text-gray-600">{product.units} units</p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-primary-orange">
                      ₹{product.revenue.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">No product data available</p>
            )}
          </div>

          {/* Top Supermarkets */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top Supermarkets</h2>
            {insights?.topSupermarkets && insights.topSupermarkets.length > 0 ? (
              <div className="space-y-4">
                {insights.topSupermarkets.map((supermarket, index) => (
                  <div key={supermarket.supermarketId} className="flex items-center justify-between p-4 bg-neutral-lightGray rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                      <div>
                        <p className="font-semibold text-gray-900">{supermarket.name}</p>
                        <p className="text-sm text-gray-600">{supermarket.orders} orders</p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-primary-orange">
                      ₹{supermarket.revenue.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">No supermarket data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrandAnalytics;
