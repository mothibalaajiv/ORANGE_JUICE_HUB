# 🔐 MongoDB SSL Handshake Error - Complete Fix

## 🔴 Error Message
```
SSL handshake failed: tlsv1 alert internal error
```

This happens with Python 3.13 and MongoDB Atlas SSL/TLS connections.

---

## ✅ **SOLUTION 1: Update Connection String (Fastest)**

### **Edit your `backend/.env` file:**

**Add SSL parameters to your MongoDB URI:**

```env
MONGODB_URI=mongodb+srv://megha:Megha2711%24@cluster0.nf1dcp2.mongodb.net/?retryWrites=true&w=majority&authSource=admin&tls=true&tlsAllowInvalidCertificates=true
```

**Key additions:**
- `&tls=true` - Explicitly enable TLS
- `&tlsAllowInvalidCertificates=true` - Bypass certificate validation (development only)

> ⚠️ **For development only!** Remove `tlsAllowInvalidCertificates=true` in production.

---

## ✅ **SOLUTION 2: Use Standard Connection (Not SRV)**

### **Replace your connection string format:**

**Instead of `mongodb+srv://...` use `mongodb://...`:**

Get the **standard connection string** from MongoDB Atlas:
1. Go to MongoDB Atlas → Connect
2. Choose **"Connect your application"**
3. Select **"Standard connection string"** (not SRV)
4. Copy and use that string

**Example:**
```env
MONGODB_URI=mongodb://megha:Megha2711%24@ac-ccuo1eg-shard-00-00.nf1dcp2.mongodb.net:27017,ac-ccuo1eg-shard-00-01.nf1dcp2.mongodb.net:27017,ac-ccuo1eg-shard-00-02.nf1dcp2.mongodb.net:27017/?ssl=true&replicaSet=atlas-xxxxx-shard-0&authSource=admin&retryWrites=true&w=majority
```

---

## ✅ **SOLUTION 3: Update PyMongo and Dependencies**

### **Upgrade to latest pymongo:**

```bash
cd backend
venv\Scripts\activate
pip install --upgrade pymongo certifi
```

### **Then update requirements.txt:**

```txt
pymongo==4.6.3  # Latest version
certifi==2024.2.2
```

Restart backend after upgrade.

---

## ✅ **SOLUTION 4: Downgrade Python (If necessary)**

### **Python 3.13 has SSL issues, use Python 3.11 or 3.12:**

1. **Install Python 3.11:**
   - Download from: https://www.python.org/downloads/
   - Install Python 3.11.x (not 3.13)

2. **Recreate virtual environment:**
   ```bash
   cd backend
   # Delete old venv
   rmdir /s venv
   
   # Create new venv with Python 3.11
   py -3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start backend:**
   ```bash
   python run.py
   ```

---

## ✅ **SOLUTION 5: Use MongoDB URI with Certificate Bundle**

### **Explicitly specify SSL certificate:**

```python
# Edit backend/app/__init__.py
# Find the MongoClient line and update:

from pymongo import MongoClient
import certifi

# Instead of:
mongo_client = MongoClient(app.config['MONGODB_URI'])

# Use:
mongo_client = MongoClient(
    app.config['MONGODB_URI'],
    tls=True,
    tlsCAFile=certifi.where()
)
```

---

## 🧪 **Test Each Solution**

After trying each solution, test with:

```bash
cd backend
venv\Scripts\activate
python test_mongodb.py
```

**Success looks like:**
```
✅ Connected to MongoDB!
✅ Write successful!
🎉 ALL TESTS PASSED!
```

---

## 📋 **Complete Working .env Example**

```env
# MongoDB with SSL fix (Solution 1)
MONGODB_URI=mongodb+srv://megha:Megha2711%24@cluster0.nf1dcp2.mongodb.net/?retryWrites=true&w=majority&authSource=admin&tls=true&tlsAllowInvalidCertificates=true

# OR use standard connection (Solution 2)
# MONGODB_URI=mongodb://megha:Megha2711%24@ac-ccuo1eg-shard-00-00.nf1dcp2.mongodb.net:27017,ac-ccuo1eg-shard-00-01.nf1dcp2.mongodb.net:27017,ac-ccuo1eg-shard-00-02.nf1dcp2.mongodb.net:27017/?ssl=true&replicaSet=atlas-xxxxx-shard-0&authSource=admin&retryWrites=true&w=majority

DB_NAME=tangy_town
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-min-32-characters
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
FRONTEND_URL=http://localhost:3000
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

---

## 🔍 **Recommended Order of Solutions**

1. ⚡ **Try Solution 1 first** (add SSL params) - 30 seconds
2. 🔄 **Try Solution 3** (upgrade pymongo) - 2 minutes
3. 🔌 **Try Solution 2** (standard connection) - 5 minutes
4. 🐍 **Try Solution 4** (downgrade Python) - 15 minutes

---

## 🆘 **Still Not Working?**

### **Alternative: Use MongoDB Compass**

1. Download **MongoDB Compass** (official GUI)
2. Use your connection string
3. If Compass works, copy the exact string it uses
4. Use that string in your .env file

### **Check MongoDB Atlas**

1. Go to MongoDB Atlas dashboard
2. Check cluster is **ACTIVE** (green)
3. Network Access → Ensure **0.0.0.0/0** is whitelisted
4. Database Access → Ensure user has proper permissions

### **Try Different Network**

Sometimes SSL issues are network-related:
- Try mobile hotspot
- Try different WiFi
- Temporarily disable VPN/proxy

---

## ✅ **Success Indicators**

When fixed:
- No more "SSL handshake failed" errors
- `python test_mongodb.py` passes
- Backend starts without SSL errors
- Admin can be created successfully

---

**Most likely fix: Add `&tls=true&tlsAllowInvalidCertificates=true` to your connection string!** 🔧
