# 🔑 Admin User Setup & Approval System

## 🎯 **YES, THERE IS AN ADMIN ROLE!**

The admin approves:
- ✅ **Brands** - Before they can add products
- ✅ **Products** - Before they appear in catalog
- ✅ **Supermarkets** - Before they can manage inventory

---

## 🚀 **Create Admin User (One-Time Setup)**

### **Run this command:**

```bash
cd backend
venv\Scripts\activate
python create_admin.py
```

### **Default Admin Credentials:**

```
Email: admin@tangytown.com
Password: Admin@123
```

> ⚠️ **IMPORTANT:** Change password after first login!

---

## 📝 **Admin Login Steps**

### **1. Start Your Application:**

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### **2. Login as Admin:**

1. Go to: **http://localhost:3000/login**
2. Enter admin credentials:
   - Email: `admin@tangytown.com`
   - Password: `Admin@123`
3. Click **"Login"**

### **3. Access Admin Dashboard:**

After login, you'll be redirected to:
```
http://localhost:3000/admin/dashboard
```

---

## ✅ **Approve Brands & Supermarkets**

### **Navigate to Approvals Page:**

**From Admin Dashboard:**
- Click **"Pending Approvals"** card
- Or go to: `http://localhost:3000/admin/approvals`

### **Approve Brands:**

1. See list of **Pending Brands**
2. Review brand details (name, email, registration date)
3. Click **"Approve"** button (orange)
4. Brand can now add products!

### **Approve Products:**

1. See list of **Pending Products**
2. Review product details (name, price, brand)
3. Click **"Approve"** button (orange)
4. Product appears in customer catalog!

### **Approve Supermarkets:**

1. See list of **Pending Supermarkets**
2. Review supermarket details (name, address)
3. Click **"Approve"** button (orange)
4. Supermarket can now manage inventory!

---

## 🎨 **Admin Dashboard Features**

### **Main Dashboard** (`/admin/dashboard`)
- 📊 **Statistics Cards**
  - Total Users
  - Total Orders
  - Total Revenue
  - Active Partners
- 📈 **Recent Orders** (last 10)
- 🔗 **Quick Actions**
  - Manage Approvals
  - View Orders
  - Manage Users

### **Approvals Page** (`/admin/approvals`)
- 🏢 **Pending Brands** - Approve/Reject
- 🧃 **Pending Products** - Approve/Reject
- 🏪 **Pending Supermarkets** - Approve/Reject

### **Orders Management** (`/admin/orders`)
- 📦 View all orders across platform
- 🔍 Filter by status
- 📋 See order details (items, customer, partner)

### **Users Management** (`/admin/users`)
- 👥 View all users by role
- 🔍 Search and filter users
- 📊 User statistics

---

## 🔄 **Approval Workflow**

### **Brand Registration Flow:**
```
1. User signs up as "Brand" → Brand Status: Pending
2. Brand waits for admin approval
3. Admin approves brand → Brand Status: Approved
4. Brand can now add products
5. Products need approval too
6. Admin approves products → Products visible to customers
```

### **Supermarket Registration Flow:**
```
1. User signs up as "Supermarket" → Supermarket Status: Pending
2. Supermarket waits for admin approval
3. Admin approves supermarket → Supermarket Status: Approved
4. Supermarket can now add inventory
5. Products become available for orders
```

---

## 🔐 **Admin Security**

### **Change Default Password:**

1. Login with default credentials
2. Go to **Admin Dashboard** → **Profile**
3. Click **"Change Password"**
4. Enter new strong password
5. Save changes

### **Strong Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### **Recommended Password Example:**
```
TangyAdmin2024!
SecurePass@123
AdminTown#456
```

---

## 👥 **Create Multiple Admins**

### **Method 1: Using create_admin.py (Edit script)**

Edit `backend/create_admin.py` and change:
```python
ADMIN_EMAIL = "admin2@tangytown.com"
ADMIN_PASSWORD = "NewAdmin@123"
ADMIN_NAME = "Secondary Admin"
```

Then run:
```bash
python create_admin.py
```

### **Method 2: MongoDB Compass (Manual)**

1. Open **MongoDB Compass**
2. Connect to your cluster
3. Go to `tangy_town` database → `users` collection
4. Click **"Add Document"**
5. Paste this (update email/password):
```json
{
  "name": "New Admin",
  "email": "newadmin@tangytown.com",
  "passwordHash": "$2b$12$HASH_FROM_BCRYPT",
  "role": "admin",
  "phone": "+91-9999999999",
  "active": true,
  "verified": true,
  "createdAt": { "$date": "2025-10-18T08:00:00Z" },
  "updatedAt": { "$date": "2025-10-18T08:00:00Z" }
}
```

---

## 🧪 **Test Approval Flow**

### **Complete Test Scenario:**

1. **Create Admin:**
   ```bash
   python create_admin.py
   ```

2. **Sign up as Brand:**
   - Go to: http://localhost:3000/signup
   - Select role: "Brand"
   - Fill details, submit
   - Note: Brand dashboard shows "Pending Approval"

3. **Login as Admin:**
   - Go to: http://localhost:3000/login
   - Login with admin credentials
   - Go to: Approvals page

4. **Approve Brand:**
   - See pending brand
   - Click "Approve"
   - Brand gets approved instantly

5. **Brand Adds Product:**
   - Logout admin
   - Login as brand
   - Go to: Products → Add Product
   - Submit product

6. **Admin Approves Product:**
   - Login as admin
   - Go to: Approvals → Products tab
   - Approve the product

7. **Product Visible:**
   - Logout admin
   - Browse as customer
   - Product appears in catalog!

---

## 📊 **Admin Permissions**

Admins can:
- ✅ Approve/reject brands
- ✅ Approve/reject products
- ✅ Approve/reject supermarkets
- ✅ View all orders
- ✅ View all users
- ✅ Monitor platform statistics
- ✅ Access all features

Admins CANNOT:
- ❌ Place orders (use customer account)
- ❌ Add products (use brand account)
- ❌ Deliver orders (use partner account)

---

## 🆘 **Troubleshooting**

### **"Admin user already exists" message:**
- ✅ This is fine! Use existing credentials
- Email: `admin@tangytown.com`
- Password: `Admin@123`

### **Can't login as admin:**
1. Check MongoDB connection is working
2. Run `python test_mongodb.py` to verify
3. Check if admin user exists in MongoDB Atlas
4. Try creating admin again: `python create_admin.py`

### **Approval button not working:**
1. Check browser console for errors
2. Verify backend is running
3. Check admin is logged in (look at JWT token)
4. Refresh the page

### **Brands/Products not appearing after approval:**
1. Refresh the brand dashboard
2. Check MongoDB Atlas → `brands` collection → `approved: true`
3. Restart frontend: `npm start`

---

## 📋 **Quick Reference**

| Action | Command/URL |
|--------|-------------|
| Create Admin | `python create_admin.py` |
| Admin Login | http://localhost:3000/login |
| Admin Dashboard | http://localhost:3000/admin/dashboard |
| Approvals Page | http://localhost:3000/admin/approvals |
| Admin Email | admin@tangytown.com |
| Admin Password | Admin@123 |

---

## 🎉 **Success Checklist**

- [ ] Admin user created (`python create_admin.py`)
- [ ] Can login as admin
- [ ] Can access admin dashboard
- [ ] Can see pending brands/supermarkets
- [ ] Can approve brands
- [ ] Approved brands can add products
- [ ] Can approve products
- [ ] Products visible in customer catalog

---

**🔑 Your admin is the gatekeeper of the platform! All brands and supermarkets need admin approval before they can operate.** 🚀
