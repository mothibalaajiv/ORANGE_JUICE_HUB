import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const { getCartCount } = useCart();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getDashboardLink = () => {
    if (!user) return '/';
    return `/${user.role}`;
  };

  const cartCount = getCartCount();

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
            <div className="text-3xl">🍊</div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-orange to-secondary-darkOrange bg-clip-text text-transparent">
              Tangy Town
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6 flex-1 justify-end">
            <Link
              to="/"
              className="text-gray-700 hover:text-primary-orange font-medium transition"
            >
              Home
            </Link>
            <Link
              to="/products"
              className="text-gray-700 hover:text-primary-orange font-medium transition"
            >
              Products
            </Link>
            <Link
              to="/brands"
              className="text-gray-700 hover:text-primary-orange font-medium transition"
            >
              Brands
            </Link>

            {isAuthenticated ? (
              <>
                {user?.role === 'user' && (
                  <Link
                    to="/user/cart"
                    className="relative text-gray-700 hover:text-primary-orange transition"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                      />
                    </svg>
                    {cartCount > 0 && (
                      <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                        {cartCount}
                      </span>
                    )}
                  </Link>
                )}

                <Link
                  to={getDashboardLink()}
                  className="text-gray-700 hover:text-primary-orange font-medium transition"
                >
                  Dashboard
                </Link>

                <button
                  onClick={handleLogout}
                  className="bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-orange font-medium transition"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden text-gray-700 hover:text-primary-orange"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 pt-2 pb-4 space-y-3">
            <Link
              to="/"
              className="block text-gray-700 hover:text-primary-orange font-medium py-2"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/products"
              className="block text-gray-700 hover:text-primary-orange font-medium py-2"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Products
            </Link>
            <Link
              to="/brands"
              className="block text-gray-700 hover:text-primary-orange font-medium py-2"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Brands
            </Link>

            {isAuthenticated ? (
              <>
                {user?.role === 'user' && (
                  <Link
                    to="/user/cart"
                    className="block text-gray-700 hover:text-primary-orange font-medium py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Cart {cartCount > 0 && `(${cartCount})`}
                  </Link>
                )}

                <Link
                  to={getDashboardLink()}
                  className="block text-gray-700 hover:text-primary-orange font-medium py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>

                <button
                  onClick={() => {
                    handleLogout();
                    setIsMobileMenuOpen(false);
                  }}
                  className="w-full bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition text-left"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block text-gray-700 hover:text-primary-orange font-medium py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="block w-full bg-primary-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-secondary-darkOrange transition text-center"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
