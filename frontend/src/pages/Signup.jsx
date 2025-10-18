import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    role: 'user',
    address: '',
    // Role-specific fields
    brandName: '',
    brandDescription: '',
    supermarketName: '',
    vehicleType: 'bike',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await signup(formData);
      
      if (result.success) {
        navigate(`/${result.user.role}`);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-orange to-secondary-darkOrange flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-8 animate-fade-in">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🍊</div>
          <h2 className="text-3xl font-bold text-gray-900">Join Tangy Town</h2>
          <p className="text-gray-600 mt-2">Create your account and start ordering!</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Account Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              I want to join as
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { value: 'user', label: 'Customer', icon: '👤' },
                { value: 'brand', label: 'Brand', icon: '🏢' },
                { value: 'partner', label: 'Delivery Partner', icon: '🚴' },
                { value: 'supermarket', label: 'Supermarket', icon: '🏪' },
              ].map((option) => (
                <label
                  key={option.value}
                  className={`cursor-pointer border-2 rounded-lg p-4 text-center transition ${
                    formData.role === option.value
                      ? 'border-primary-orange bg-orange-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="role"
                    value={option.value}
                    checked={formData.role === option.value}
                    onChange={handleChange}
                    className="hidden"
                  />
                  <div className="text-3xl mb-2">{option.icon}</div>
                  <div className="text-sm font-medium">{option.label}</div>
                </label>
              ))}
            </div>
          </div>

          {/* Basic Info */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                required
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                placeholder="+91 98765 43210"
              />
            </div>
          </div>

          {/* Address */}
          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
              Address
            </label>
            <textarea
              id="address"
              name="address"
              rows="2"
              value={formData.address}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
              placeholder="Your full address"
            />
          </div>

          {/* Role-specific fields */}
          {formData.role === 'brand' && (
            <>
              <div>
                <label htmlFor="brandName" className="block text-sm font-medium text-gray-700 mb-2">
                  Brand Name
                </label>
                <input
                  id="brandName"
                  name="brandName"
                  type="text"
                  required
                  value={formData.brandName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                  placeholder="Your Brand Name"
                />
              </div>
              <div>
                <label htmlFor="brandDescription" className="block text-sm font-medium text-gray-700 mb-2">
                  Brand Description
                </label>
                <textarea
                  id="brandDescription"
                  name="brandDescription"
                  rows="2"
                  value={formData.brandDescription}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                  placeholder="Tell us about your brand"
                />
              </div>
            </>
          )}

          {formData.role === 'supermarket' && (
            <div>
              <label htmlFor="supermarketName" className="block text-sm font-medium text-gray-700 mb-2">
                Supermarket Name
              </label>
              <input
                id="supermarketName"
                name="supermarketName"
                type="text"
                required
                value={formData.supermarketName}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
                placeholder="Your Supermarket Name"
              />
            </div>
          )}

          {formData.role === 'partner' && (
            <div>
              <label htmlFor="vehicleType" className="block text-sm font-medium text-gray-700 mb-2">
                Vehicle Type
              </label>
              <select
                id="vehicleType"
                name="vehicleType"
                value={formData.vehicleType}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-orange focus:border-transparent"
              >
                <option value="bike">Bike</option>
                <option value="scooter">Scooter</option>
                <option value="car">Car</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-orange text-white py-3 rounded-lg font-semibold hover:bg-secondary-darkOrange transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-orange font-semibold hover:underline">
              Login
            </Link>
          </p>
        </div>

        <div className="mt-6 text-center">
          <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
