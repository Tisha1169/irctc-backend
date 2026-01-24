# 🚆 IRCTC Mini Backend System (Django + MySQL + MongoDB)

A production-style IRCTC backend system built using Django REST Framework with real-world concepts like JWT authentication, seat locking, concurrent booking handling, waitlist system, admin analytics, MongoDB logging and rate limiting.

This project simulates how real railway booking systems work.

---

## 🔥 Features Implemented

### ✅ Authentication System
- User Registration API
- JWT Login (Access + Refresh Tokens)
- Protected Endpoints

### ✅ Booking Engine
- Real-time seat availability check
- Atomic booking (race-condition safe)
- Seat locking using database transactions
- Auto WAITLIST when seats full
- Auto CONFIRM when cancellation happens

### ✅ Cancellation System
- Seat restore on cancel
- Auto upgrade WAITLIST → CONFIRMED

### ✅ Admin APIs
- View booking statistics
- System monitoring endpoints

### ✅ Database Architecture
- MySQL → Core transactional data
- MongoDB → Booking logs & analytics

### ✅ Security
- JWT Authentication
- Rate limiting (anti abuse)
- Permission based endpoints

---

## 🏗 Tech Stack

| Layer | Technology |
------|---------
Backend | Django REST Framework
Database | MySQL
Analytics DB | MongoDB
Auth | JWT
Concurrency | Transactions + Row Locking
API Testing | Thunder Client / Postman

---

## 📁 Project Structure

