import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const BrandDashboard = () => {
  const [brand, setBrand] = useState(null);
  const [products, setProducts] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [brandRes, productsRes] = await Promise.all([
        api.get('/brands/my-brand'),
        api.get('/brands/my-products'),
      ]);

      setBrand(brandRes.data);
      setProducts(productsRes.data.products);

      // Fetch insights if brand approved
      if (brandRes.data.approved) {
        try {
          const insightsRes = await api.get(`/analytics/brands/${brandRes.data._id}/insights`);
          setInsights(insightsRes.data);
        } catch (error) {
          console.error('Error fetching insights:', error);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      // Set default brand data if API fails
      setBrand({ name: 'Brand Name', approved: false });
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

  if (!brand) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Brand Not Found</h2>
          <p className="text-gray-600">Unable to load brand information.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-orange to-secondary-darkOrange text-white rounded-lg shadow-card p-8 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold mb-2 text-white truncate">
                {brand?.name || 'Brand Name'} 🏢
              </h1>
              <p className="text-white/90">Manage your brand and track performance</p>
            </div>
            <div className="ml-4 flex-shrink-0">
              {brand?.approved ? (
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
        </div>

        {!brand?.approved && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-6 py-4 rounded-lg mb-8">
            <p className="font-semibold mb-1">⏳ Brand Approval Pending</p>
            <p className="text-sm">
              Your brand is currently under review. Once approved, you'll be able to add products and access analytics.
            </p>
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Products</p>
                <p className="text-2xl font-bold text-gray-900">{products.length}</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Sales</p>
                <p className="text-2xl font-bold text-gray-900">
                  ₹{insights?.totalSales?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="text-4xl">💰</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Total Orders</p>
                <p className="text-2xl font-bold text-gray-900">
                  {insights?.totalOrders || 0}
                </p>
              </div>
              <div className="text-4xl">🛍️</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-card p-6">
            <Link to="/brand/products" className="block">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Manage Products</p>
                  <p className="text-primary-orange font-semibold">View All →</p>
                </div>
                <div className="text-4xl">⚙️</div>
              </div>
            </Link>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Products */}
          <div className="bg-white rounded-lg shadow-card">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Your Products</h2>
              <Link
                to="/brand/products"
                className="text-primary-orange hover:underline text-sm font-medium"
              >
                View All
              </Link>
            </div>
            <div className="p-6">
              {products.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-5xl mb-3">📦</div>
                  <p className="text-gray-600 mb-4">No products yet</p>
                  <Link
                    to="/brand/products"
                    className="inline-block bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition"
                  >
                    Add Your First Product
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {products.slice(0, 5).map((product) => (
                    <div key={product._id} className="flex items-center justify-between p-4 bg-neutral-lightGray rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
                          {product.imageUrl ? (
                            <img src={product.imageUrl} alt={product.name} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <span className="text-2xl">🧃</span>
                          )}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-600">{product.volume}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">₹{product.price}</p>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          product.approved 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {product.approved ? 'Active' : 'Pending'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Top Performing Products */}
          <div className="bg-white rounded-lg shadow-card">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Top Products</h2>
              <Link
                to="/brand/analytics"
                className="text-primary-orange hover:underline text-sm font-medium"
              >
                View Analytics
              </Link>
            </div>
            <div className="p-6">
              {insights?.topProducts && insights.topProducts.length > 0 ? (
                <div className="space-y-4">
                  {insights.topProducts.slice(0, 5).map((product, index) => (
                    <div key={product.productId} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                        <div>
                          <p className="font-semibold text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-600">{product.units} units sold</p>
                        </div>
                      </div>
                      <p className="font-bold text-primary-orange">₹{product.revenue.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-5xl mb-3">📊</div>
                  <p className="text-gray-600">No sales data yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrandDashboard;
