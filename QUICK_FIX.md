# 🚨 QUICK FIX - Authentication Failed Error

## ⚡ The Problem
Your MongoDB password contains `$` which breaks the connection string!

---

## ✅ **FASTEST FIX (2 minutes)**

### Open your `backend/.env` file and change this line:

**❌ Current (BROKEN):**
```env
MONGODB_URI=mongodb+srv://megha:Megha2711$@cluster0.nf1dcp2.mongodb.net/
```

**✅ Fixed (URL Encoded):**
```env
MONGODB_URI=mongodb+srv://megha:Megha2711%24@cluster0.nf1dcp2.mongodb.net/?retryWrites=true&w=majority&authSource=admin
```

**Key Changes:**
1. `$` → `%24` (URL encoded)
2. Added `?retryWrites=true&w=majority&authSource=admin` at the end

---

## 🧪 **Test Your Fix**

```bash
cd backend
venv\Scripts\activate
python test_mongodb.py
```

**If successful, you'll see:**
```
✅ Connected to MongoDB!
✅ Write successful!
🎉 ALL TESTS PASSED!
```

---

## 🚀 **Then Start Your Server**

```bash
python run.py
```

**Look for:**
```
✓ MongoDB indexes created successfully
 * Running on http://127.0.0.1:5000
```

✅ **No more "Authentication failed" error!**

---

## 🔄 **Alternative: Change Password (If encoding doesn't work)**

1. Go to **MongoDB Atlas** → **Database Access**
2. Edit user **"megha"**
3. Change password to: `Megha2711` (no special chars)
4. Update `.env`:
```env
MONGODB_URI=mongodb+srv://megha:Megha2711@cluster0.nf1dcp2.mongodb.net/?retryWrites=true&w=majority&authSource=admin
```

---

## 📚 **More Help**

- **Full authentication guide:** `MONGODB_AUTH_FIX.md`
- **General MongoDB setup:** `MONGODB_SETUP.md`

---

**Most likely you just need to change `$` to `%24` in your .env file! 🎯**
