# 🚀 Tangy Town - Complete Setup Guide

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Configure .env file
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
# Configure .env file
npm start
```

## Environment Variables

### Backend (.env)
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/tangytown
JWT_SECRET=your_jwt_secret_key_here
JWT_REFRESH_SECRET=your_refresh_secret_here
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_secret_here
GOOGLE_MAPS_API_KEY=your_google_maps_key
FLASK_ENV=development
PORT=5000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_RAZORPAY_KEY_ID=rzp_test_your_key
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_key
```

## Default Admin Account
After first run, create admin via MongoDB:
```javascript
db.users.insertOne({
  name: "Admin",
  email: "admin@tangytown.com",
  password: "$2b$10$hashed_password_here",
  role: "admin",
  createdAt: new Date()
})
```

## Testing the Application
1. Start backend: `python run.py`
2. Start frontend: `npm start`
3. Open http://localhost:3000
4. Sign up as different roles
5. Test complete order flow

## Deployment Checklist
- [ ] Set production environment variables
- [ ] Update MongoDB whitelist
- [ ] Configure CORS for production URL
- [ ] Set up Razorpay webhook URL
- [ ] Enable rate limiting
- [ ] Set up logging and monitoring
- [ ] Configure SSL certificates
- [ ] Test payment flow in production
- [ ] Set up backup strategy

## Troubleshooting
- **MongoDB connection failed**: Check connection string and IP whitelist
- **CORS errors**: Verify CORS_ORIGINS in backend config
- **Payment not working**: Verify Razorpay keys in both backend and frontend
- **Socket.IO not connecting**: Check if backend is running on correct port
