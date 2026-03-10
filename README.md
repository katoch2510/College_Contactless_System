# Contactless Entry and Visitor Management System

## 📌 Project Overview

The **Contactless Entry and Visitor Management System** is a web-based application developed to manage entry and exit of visitors and regular members in a college environment without physical contact.

The system uses **Face Recognition for regular users** and **QR Code scanning for visitors** to automate the entry process.

This project helps improve **security, efficiency, and digital record management** inside educational institutions.

---

## 🚀 Features

### 1. Visitor Management

* Register visitor details (name and purpose)
* Automatic **QR code generation** for each visitor
* QR scanning for entry verification
* Entry and exit time recorded automatically

### 2. Regular User Entry (Students/Staff)

* Face registration system
* Face recognition for automatic entry
* Stores last entry time

### 3. Dashboard

* View visitor records
* Monitor entry logs
* Simple web interface for management

---

## 🛠️ Technologies Used

* **Python**
* **Flask (Web Framework)**
* **OpenCV** (Face Detection & Recognition)
* **SQLite Database**
* **HTML**
* **CSS**
* **QR Code Generator (qrcode library)**
* **NumPy**

---

## 📂 Project Structure

```
College_Contactless_System
│
├── app.py                 # Main Flask application
├── entry_system.db        # SQLite database
├── trainer.yml            # Face recognition trained model
│
├── faces/                 # Stored face images of registered users
│
├── static/
│   └── visitor_qr/        # Generated QR codes for visitors
│
└── templates/
    ├── index.html
    ├── dashboard.html
    ├── regular_register.html
    └── result.html
```

---

## ⚙️ Installation & Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/contactless-entry-system.git
cd contactless-entry-system
```

### Step 2: Install Required Libraries

```bash
pip install flask opencv-python numpy qrcode
```

### Step 3: Run the Project

```bash
python app.py
```

### Step 4: Open Browser

```
http://127.0.0.1:5000
```

---

## 🧠 How It Works

### Visitor Entry

1. Visitor enters their details.
2. System generates a **QR code**.
3. QR code is scanned at the gate.
4. Entry time is recorded in the database.

### Regular Users

1. User registers their face in the system.
2. Face images are stored in the **faces folder**.
3. The model trains using **LBPH Face Recognizer**.
4. Camera detects and recognizes the face.
5. Entry time is stored automatically.

---

## 🎯 Applications

* College campus security
* Office entry systems
* Smart visitor management
* Contactless attendance systems

---

## 📊 Future Improvements

* Mobile QR scanning
* Admin login panel
* Real-time visitor dashboard
* Email notifications
* Cloud database integration

---

## 👨‍💻 Author

**Piyush Katoch**
**Abhinav**
**Abhay Kumar**
**Harshit**


B.Tech Project
Contactless Entry + Visitor Management System

---

## 📜 License

This project is developed for **educational purposes**.
