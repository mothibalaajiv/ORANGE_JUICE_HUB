import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Public Pages
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Login from './pages/Login';
import Signup from './pages/Signup';
import BrandsPage from './pages/BrandsPage';

// User Pages
import UserDashboard from './pages/user/Dashboard';
import Cart from './pages/user/Cart';
import Checkout from './pages/user/Checkout';
import OrderTracking from './pages/user/OrderTracking';
import UserProfile from './pages/user/Profile';

// Brand Pages
import BrandDashboard from './pages/brand/Dashboard';
import BrandProducts from './pages/brand/Products';
import BrandAnalytics from './pages/brand/Analytics';

// Partner Pages
import PartnerDashboard from './pages/partner/Dashboard';
import PartnerEarnings from './pages/partner/Earnings';

// Supermarket Pages
import SupermarketDashboard from './pages/supermarket/Dashboard';
import SupermarketInventory from './pages/supermarket/Inventory';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import AdminUsers from './pages/admin/Users';
import AdminOrders from './pages/admin/Orders';
import AdminApprovals from './pages/admin/Approvals';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppContent() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/brands" element={<BrandsPage />} />
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to={`/${user?.role}`} />} />
          <Route path="/signup" element={!isAuthenticated ? <Signup /> : <Navigate to={`/${user?.role}`} />} />

          {/* User Routes */}
          <Route
            path="/user"
            element={
              <ProtectedRoute allowedRoles={['user']}>
                <UserDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/user/cart"
            element={
              <ProtectedRoute allowedRoles={['user']}>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path="/user/checkout"
            element={
              <ProtectedRoute allowedRoles={['user']}>
                <Checkout />
              </ProtectedRoute>
            }
          />
          <Route
            path="/user/orders/:orderId"
            element={
              <ProtectedRoute allowedRoles={['user']}>
                <OrderTracking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/user/profile"
            element={
              <ProtectedRoute allowedRoles={['user']}>
                <UserProfile />
              </ProtectedRoute>
            }
          />

          {/* Brand Routes */}
          <Route
            path="/brand"
            element={
              <ProtectedRoute allowedRoles={['brand']}>
                <BrandDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/brand/products"
            element={
              <ProtectedRoute allowedRoles={['brand']}>
                <BrandProducts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/brand/analytics"
            element={
              <ProtectedRoute allowedRoles={['brand']}>
                <BrandAnalytics />
              </ProtectedRoute>
            }
          />

          {/* Partner Routes */}
          <Route
            path="/partner"
            element={
              <ProtectedRoute allowedRoles={['partner']}>
                <PartnerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/partner/earnings"
            element={
              <ProtectedRoute allowedRoles={['partner']}>
                <PartnerEarnings />
              </ProtectedRoute>
            }
          />

          {/* Supermarket Routes */}
          <Route
            path="/supermarket"
            element={
              <ProtectedRoute allowedRoles={['supermarket']}>
                <SupermarketDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/supermarket/inventory"
            element={
              <ProtectedRoute allowedRoles={['supermarket']}>
                <SupermarketInventory />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminUsers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/orders"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/approvals"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminApprovals />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <CartProvider>
          <AppContent />
        </CartProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
