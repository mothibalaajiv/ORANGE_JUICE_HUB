# MongoDB Atlas Setup & Troubleshooting

## 🔧 Issue: "Signup failed, no database created in my cluster"

This happens when the backend cannot connect to MongoDB Atlas. Follow these steps:

---

## ✅ Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for a FREE account
3. Create a **FREE M0 Cluster** (512MB storage, perfect for development)
4. Choose a cloud provider and region closest to you
5. Wait 1-3 minutes for cluster creation

---

## ✅ Step 2: Configure Network Access

**THIS IS THE MOST COMMON ISSUE!**

1. In MongoDB Atlas, click **"Network Access"** in the left sidebar
2. Click **"Add IP Address"**
3. Select **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Click **"Confirm"**

> ⚠️ **Important:** Without this, your connection will timeout!

---

## ✅ Step 3: Create Database User

1. Click **"Database Access"** in the left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Set username: `tangytown_user` (or your choice)
5. Set a strong password (save this!)
6. Set role: **"Atlas admin"** or **"Read and write to any database"**
7. Click **"Add User"**

---

## ✅ Step 4: Get Connection String

1. Click **"Database"** in the left sidebar
2. Click **"Connect"** button on your cluster
3. Choose **"Connect your application"**
4. Select **Driver: Python**, **Version: 3.12 or later**
5. Copy the connection string (looks like this):

```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

## ✅ Step 5: Configure Backend .env File

1. Open `backend/.env` file
2. Replace the connection string:

```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://tangytown_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=tangy_town

# JWT Secrets (generate random strings)
JWT_SECRET_KEY=your_super_secret_key_here_32_chars_min
JWT_REFRESH_SECRET_KEY=your_refresh_secret_key_32_chars_min

# Razorpay (get from razorpay.com)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Flask Environment
FLASK_ENV=development
```

**Important:**
- Replace `<username>` with your database username
- Replace `<password>` with your database password
- Replace `xxxxx` with your cluster identifier
- Add `&authSource=admin` at the end if authentication fails

---

## ✅ Step 6: Test Connection

Start your backend:

```bash
cd backend
venv\Scripts\activate
python run.py
```

**Look for this message:**
```
✓ MongoDB indexes created successfully
 * Running on http://127.0.0.1:5000
```

If you see this, connection is successful! ✅

---

## 🐛 Common Errors & Solutions

### Error: "Authentication failed"
**Solution:**
- Double-check username and password in connection string
- Ensure password has NO special characters like `@`, `#`, `:` 
- If it does, URL encode them or change password
- Add `&authSource=admin` to connection string

### Error: "Connection timeout"
**Solution:**
- Whitelist IP address (0.0.0.0/0) in Network Access
- Check your firewall/antivirus isn't blocking MongoDB ports
- Try using mobile hotspot to test if it's network issue

### Error: "Server selection timeout"
**Solution:**
- Ensure cluster is running (green dot in Atlas)
- Verify connection string is correct
- Check if MongoDB Atlas is having issues: https://status.mongodb.com/

### Error: "Database doesn't appear in Atlas"
**Solution:**
- MongoDB Atlas only shows databases AFTER first data insertion
- Try signing up a user first
- Refresh Atlas interface
- The database `tangy_town` will auto-create on first write operation

---

## 🧪 Manual Connection Test

Create a test file `backend/test_connection.py`:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['tangy_town']
    
    # Try to insert a test document
    result = db.test.insert_one({'test': 'connection'})
    print("✅ Connection successful!")
    print(f"✅ Document inserted with ID: {result.inserted_id}")
    
    # Clean up test
    db.test.delete_one({'_id': result.inserted_id})
    print("✅ Test cleanup complete")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
```

Run it:
```bash
cd backend
venv\Scripts\activate
python test_connection.py
```

---

## 📋 Complete .env Template

```env
# ===========================================
# MONGODB CONFIGURATION
# ===========================================
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&authSource=admin
DB_NAME=tangy_town

# ===========================================
# JWT CONFIGURATION
# ===========================================
JWT_SECRET_KEY=please_change_this_to_random_32_char_string
JWT_REFRESH_SECRET_KEY=please_change_this_to_another_random_string

# ===========================================
# RAZORPAY CONFIGURATION
# Get these from: https://dashboard.razorpay.com/
# ===========================================
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# ===========================================
# APPLICATION CONFIGURATION
# ===========================================
FRONTEND_URL=http://localhost:3000
FLASK_ENV=development

# Optional: Google Maps API (for advanced geolocation)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

---

## 🎯 Quick Checklist

- [ ] MongoDB Atlas cluster created
- [ ] IP whitelist configured (0.0.0.0/0)
- [ ] Database user created with proper permissions
- [ ] Connection string copied correctly
- [ ] Password in connection string is URL-encoded
- [ ] `.env` file exists in `backend/` directory
- [ ] `.env` has correct MONGODB_URI
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend starts without errors
- [ ] You see "✓ MongoDB indexes created successfully"

---

## 🆘 Still Having Issues?

1. **Check Backend Console**: Look for specific error messages
2. **MongoDB Atlas Logs**: Check Metrics tab in Atlas
3. **Test with MongoDB Compass**: Download MongoDB Compass and test connection string
4. **Firewall**: Temporarily disable firewall to test
5. **Use Different Network**: Try mobile hotspot

---

## 🎉 Success Indicators

When everything works:
1. Backend console shows: `✓ MongoDB indexes created successfully`
2. You can sign up a new user
3. Database `tangy_town` appears in MongoDB Atlas
4. Collections are created: `users`, `orders`, `products`, etc.

---

**Need Help?** Share the exact error message from your backend console!
