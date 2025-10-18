import React, { useEffect, useState } from 'react';
import api from '../../services/api';

const AdminApprovals = () => {
  const [pendingBrands, setPendingBrands] = useState([]);
  const [pendingProducts, setPendingProducts] = useState([]);
  const [pendingSupermarkets, setPendingSupermarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('brands');

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    setLoading(true);
    try {
      const [brandsRes, productsRes, supermarketsRes] = await Promise.all([
        api.get('/admin/brands/pending'),
        api.get('/admin/products/pending'),
        api.get('/admin/supermarkets/pending'),
      ]);

      setPendingBrands(brandsRes.data.brands);
      setPendingProducts(productsRes.data.products);
      setPendingSupermarkets(supermarketsRes.data.supermarkets);
    } catch (error) {
      console.error('Error fetching pending approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveBrand = async (brandId) => {
    try {
      await api.post(`/admin/brands/${brandId}/approve`);
      fetchPendingApprovals();
    } catch (error) {
      console.error('Error approving brand:', error);
    }
  };

  const handleRejectBrand = async (brandId) => {
    if (window.confirm('Are you sure you want to reject this brand?')) {
      try {
        await api.post(`/admin/brands/${brandId}/reject`);
        fetchPendingApprovals();
      } catch (error) {
        console.error('Error rejecting brand:', error);
      }
    }
  };

  const handleApproveProduct = async (productId) => {
    try {
      await api.post(`/admin/products/${productId}/approve`);
      fetchPendingApprovals();
    } catch (error) {
      console.error('Error approving product:', error);
    }
  };

  const handleApproveSupermarket = async (supermarketId) => {
    try {
      await api.post(`/admin/supermarkets/${supermarketId}/approve`);
      fetchPendingApprovals();
    } catch (error) {
      console.error('Error approving supermarket:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-orange"></div>
      </div>
    );
  }

  const totalPending = pendingBrands.length + pendingProducts.length + pendingSupermarkets.length;

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Pending Approvals</h1>
          <p className="text-gray-600 mt-1">
            {totalPending} item{totalPending !== 1 ? 's' : ''} waiting for approval
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-card mb-6">
          <div className="border-b border-gray-200">
            <div className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('brands')}
                className={`py-4 border-b-2 font-medium text-sm transition ${
                  activeTab === 'brands'
                    ? 'border-primary-orange text-primary-orange'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Brands ({pendingBrands.length})
              </button>
              <button
                onClick={() => setActiveTab('products')}
                className={`py-4 border-b-2 font-medium text-sm transition ${
                  activeTab === 'products'
                    ? 'border-primary-orange text-primary-orange'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Products ({pendingProducts.length})
              </button>
              <button
                onClick={() => setActiveTab('supermarkets')}
                className={`py-4 border-b-2 font-medium text-sm transition ${
                  activeTab === 'supermarkets'
                    ? 'border-primary-orange text-primary-orange'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Supermarkets ({pendingSupermarkets.length})
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Brands Tab */}
            {activeTab === 'brands' && (
              <div className="space-y-4">
                {pendingBrands.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-gray-600">No pending brand approvals</p>
                  </div>
                ) : (
                  pendingBrands.map((brand) => (
                    <div key={brand._id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-grow">
                          <h3 className="text-lg font-bold text-gray-900 mb-2">{brand.name}</h3>
                          {brand.description && (
                            <p className="text-gray-600 mb-3">{brand.description}</p>
                          )}
                          <div className="grid md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">Contact Email</p>
                              <p className="font-medium text-gray-900">{brand.contactEmail}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Contact Phone</p>
                              <p className="font-medium text-gray-900">{brand.contactPhone}</p>
                            </div>
                            {brand.website && (
                              <div>
                                <p className="text-gray-600">Website</p>
                                <a
                                  href={brand.website}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary-orange hover:underline"
                                >
                                  {brand.website}
                                </a>
                              </div>
                            )}
                            <div>
                              <p className="text-gray-600">Registered On</p>
                              <p className="font-medium text-gray-900">
                                {new Date(brand.createdAt).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col space-y-2 ml-6">
                          <button
                            onClick={() => handleApproveBrand(brand._id)}
                            className="bg-primary-orange text-white px-6 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleRejectBrand(brand._id)}
                            className="bg-red-500 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-600 transition"
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Products Tab */}
            {activeTab === 'products' && (
              <div className="space-y-4">
                {pendingProducts.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-gray-600">No pending product approvals</p>
                  </div>
                ) : (
                  pendingProducts.map((product) => (
                    <div key={product._id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-grow">
                          <div className="w-24 h-24 bg-neutral-lightGray rounded-lg flex items-center justify-center flex-shrink-0">
                            {product.imageUrl ? (
                              <img
                                src={product.imageUrl}
                                alt={product.name}
                                className="w-full h-full object-cover rounded-lg"
                              />
                            ) : (
                              <span className="text-4xl">🧃</span>
                            )}
                          </div>
                          <div className="flex-grow">
                            <h3 className="text-lg font-bold text-gray-900 mb-1">
                              {product.name}
                            </h3>
                            <p className="text-sm text-gray-600 mb-2">
                              Brand: {product.brand?.name || 'Unknown'}
                            </p>
                            {product.description && (
                              <p className="text-gray-600 mb-3">{product.description}</p>
                            )}
                            <div className="grid md:grid-cols-3 gap-4 text-sm">
                              <div>
                                <p className="text-gray-600">SKU</p>
                                <p className="font-medium text-gray-900">{product.sku}</p>
                              </div>
                              <div>
                                <p className="text-gray-600">Volume</p>
                                <p className="font-medium text-gray-900">{product.volume}</p>
                              </div>
                              <div>
                                <p className="text-gray-600">Price</p>
                                <p className="font-medium text-gray-900">₹{product.price}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => handleApproveProduct(product._id)}
                          className="bg-primary-orange text-white px-6 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition ml-6"
                        >
                          Approve
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Supermarkets Tab */}
            {activeTab === 'supermarkets' && (
              <div className="space-y-4">
                {pendingSupermarkets.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-gray-600">No pending supermarket approvals</p>
                  </div>
                ) : (
                  pendingSupermarkets.map((supermarket) => (
                    <div key={supermarket._id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-grow">
                          <h3 className="text-lg font-bold text-gray-900 mb-2">
                            {supermarket.name}
                          </h3>
                          <div className="grid md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">Address</p>
                              <p className="font-medium text-gray-900">{supermarket.address}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Contact Phone</p>
                              <p className="font-medium text-gray-900">{supermarket.phone}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Email</p>
                              <p className="font-medium text-gray-900">{supermarket.email}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Registered On</p>
                              <p className="font-medium text-gray-900">
                                {new Date(supermarket.createdAt).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => handleApproveSupermarket(supermarket._id)}
                          className="bg-primary-orange text-white px-6 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition ml-6"
                        >
                          Approve
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminApprovals;
