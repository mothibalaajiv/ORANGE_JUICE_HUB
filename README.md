# 🍊 Tangy Town - Fresh Juice E-Commerce Platform

A modern, production-ready e-commerce platform for ordering orange and white juices with real-time delivery tracking.

## 🚀 Features

### For Users
- Browse branded juices (Tropicana, Real, Minute Maid, etc.)
- Smart search with filters
- Secure checkout with Razorpay
- Real-time order tracking with map
- Order history and favorites

### For Brands
- Product catalog management
- Sales analytics dashboard
- Export insights (CSV/XLSX/PDF)
- Top products and supermarket insights

### For Delivery Partners
- Nearby order assignments (5-minute acceptance window)
- View nearby supermarkets with stock
- Earnings tracking
- Rating system

### For Supermarkets
- Inventory management
- Stock level monitoring
- Automatic stock updates on pickup

### For Admin
- Full dashboard for all roles
- Manual order reassignment
- System-wide analytics and reports

## 🛠️ Tech Stack

- **Frontend**: React, Tailwind CSS, React Router
- **Backend**: Flask (Python), Flask-SocketIO
- **Database**: MongoDB Atlas
- **Payment**: Razorpay
- **Real-time**: WebSockets
- **Background Jobs**: APScheduler
- **Maps**: Google Maps API

## 📁 Project Structure

```
ORANGE_JUICE_HUB/
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models/          # MongoDB models
│   │   ├── routes/          # API blueprints
│   │   ├── utils/           # Helper functions
│   │   └── services/        # Business logic
│   ├── requirements.txt
│   └── run.py
├── frontend/                # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🔧 Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with:
```
MONGODB_URI=mongodb+srv://megha:Megha2711$@cluster0.nf1dcp2.mongodb.net/
JWT_SECRET_KEY=your-secret-key-here
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

5. Run backend:
```bash
python run.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_RAZORPAY_KEY_ID=your-razorpay-key
REACT_APP_GOOGLE_MAPS_API_KEY=your-google-maps-key
```

4. Run frontend:
```bash
npm start
```

Frontend will run on `http://localhost:3000`

## 🎨 Design System

### Color Palette
- **Primary Orange**: `#FFA500`
- **Fresh Green**: `#32CD32`
- **Soft White**: `#FFFFFF`
- **Secondary Yellow**: `#FFD700`
- **Light Gray**: `#F5F5F5`

### Typography
- **Font Family**: Poppins, sans-serif
- **Heading**: Bold 600-700
- **Body**: Regular 400

## 🔐 Authentication

The platform uses JWT-based authentication with role-based access control (RBAC):
- User
- Brand
- Supermarket
- Delivery Partner
- Admin

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT
- `GET /api/auth/me` - Get current user profile

### Product Endpoints
- `GET /api/products` - List products with filters
- `POST /api/products` - Create product (Brand only)
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product

### Order Endpoints
- `POST /api/orders` - Create order and trigger assignment
- `GET /api/orders/:id` - Get order details
- `POST /api/orders/:id/picked-up` - Mark as picked up
- `POST /api/orders/:id/delivered` - Mark as delivered

### Payment Endpoints
- `POST /api/payments/razorpay/create-order` - Create Razorpay order
- `POST /api/payments/razorpay/webhook` - Payment webhook

### Analytics Endpoints
- `GET /api/brands/:id/insights` - Get brand analytics
- `GET /api/brands/:id/insights/export` - Export CSV/XLSX/PDF

## 🚚 Delivery Partner Assignment Flow

1. User places order and completes payment
2. System finds nearest available delivery partner
3. Assignment sent to partner (5-minute timer starts)
4. If accepted: Partner sees nearby supermarkets with stock
5. If not accepted: Auto-assign to next nearest partner
6. Partner picks up from supermarket → Stock decrements
7. Partner delivers to user → Order completed

## 📱 Responsive Design

The platform is fully responsive and mobile-first:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 🔒 Security Features

- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Razorpay signature verification
- Input validation and sanitization
- CORS configuration
- Rate limiting

## 📈 Future Enhancements

- [ ] Push notifications (FCM)
- [ ] Email notifications
- [ ] Loyalty points system
- [ ] AI-based product recommendations
- [ ] Multi-language support
- [ ] Dark mode

## 👥 Contributing

This is a production e-commerce platform. For contributions, please follow standard Git workflow.

## 📄 License

Proprietary - All rights reserved

## 📞 Support

For support, contact the development team.
