import React, { useEffect, useState } from 'react';
import api from '../../services/api';

const SupermarketInventory = () => {
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    productId: '',
    quantity: '',
    priceOverride: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [inventoryRes, productsRes] = await Promise.all([
        api.get('/supermarkets/inventory'),
        api.get('/products'),
      ]);

      setInventory(inventoryRes.data.inventory);
      setProducts(productsRes.data.products);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await api.post('/supermarkets/inventory', formData);
      setShowModal(false);
      setFormData({ productId: '', quantity: '', priceOverride: '' });
      fetchData();
    } catch (error) {
      console.error('Error adding inventory:', error);
      alert(error.response?.data?.error || 'Failed to add inventory');
    }
  };

  const handleDelete = async (inventoryId) => {
    if (window.confirm('Are you sure you want to remove this product from inventory?')) {
      try {
        await api.delete(`/supermarkets/inventory/${inventoryId}`);
        fetchData();
      } catch (error) {
        console.error('Error deleting inventory:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-neutral-lightGray py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
            <p className="text-gray-600 mt-1">Manage your product stock levels</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-primary-orange text-white px-6 py-3 rounded-lg font-semibold hover:bg-secondary-darkOrange transition"
          >
            + Add Product
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-orange"></div>
          </div>
        ) : inventory.length === 0 ? (
          <div className="bg-white rounded-lg shadow-card p-12 text-center">
            <div className="text-6xl mb-4">📦</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No inventory yet</h3>
            <p className="text-gray-600 mb-6">Start by adding products to your inventory</p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-primary-orange text-white px-6 py-3 rounded-lg font-semibold hover:bg-secondary-darkOrange transition"
            >
              Add Your First Product
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-neutral-lightGray">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Product</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Brand</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Volume</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Price</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Quantity</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {inventory.map((item) => (
                    <tr key={item._id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <p className="font-medium text-gray-900">{item.product?.name}</p>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{item.product?.brandName}</td>
                      <td className="px-6 py-4 text-gray-600">{item.product?.volume}</td>
                      <td className="px-6 py-4">
                        <p className="font-semibold text-gray-900">
                          ₹{item.priceOverride || item.product?.price}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`font-bold ${
                          item.quantity === 0 
                            ? 'text-red-600' 
                            : item.quantity < 10 
                            ? 'text-yellow-600' 
                            : 'text-blue-600'
                        }`}>
                          {item.quantity}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          item.quantity === 0 
                            ? 'bg-red-100 text-red-800' 
                            : item.quantity < 10 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {item.quantity === 0 ? 'Out of Stock' : item.quantity < 10 ? 'Low Stock' : 'In Stock'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDelete(item._id)}
                          className="text-red-600 hover:text-red-800 font-medium text-sm"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Add Inventory Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">Add Product to Inventory</h2>
              </div>
              
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Product *
                  </label>
                  <select
                    name="productId"
                    required
                    value={formData.productId}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                  >
                    <option value="">Choose a product...</option>
                    {products.map((product) => (
                      <option key={product._id} value={product._id}>
                        {product.name} - {product.volume} (₹{product.price})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity *
                  </label>
                  <input
                    type="number"
                    name="quantity"
                    required
                    min="0"
                    value={formData.quantity}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                    placeholder="Enter quantity"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Custom Price (Optional)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="priceOverride"
                    value={formData.priceOverride}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                    placeholder="Leave blank to use default price"
                  />
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-primary-orange text-white py-3 rounded-lg font-semibold hover:bg-secondary-darkOrange transition"
                  >
                    Add to Inventory
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setFormData({ productId: '', quantity: '', priceOverride: '' });
                    }}
                    className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupermarketInventory;
