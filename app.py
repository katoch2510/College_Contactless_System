from flask import Flask, render_template, request
import cv2
import sqlite3
import os
import qrcode
import numpy as np
import time
from datetime import datetime

app = Flask(__name__)

# ---------------- CONFIG ----------------
DB = "entry_system.db"
QR_DIR = "static/visitor_qr"
FACE_DIR = "faces"

os.makedirs(QR_DIR, exist_ok=True)
os.makedirs(FACE_DIR, exist_ok=True)

# ---------------- DATABASE INIT ----------------
def init_db():
    db = sqlite3.connect(DB)
    cur = db.cursor()

    # Visitor Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS visitors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        purpose TEXT,
        entry_time TEXT,
        exit_time TEXT
    )
    """)

    # Regular Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS regular_users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        last_entry TEXT
    )
    """)

    db.commit()
    db.close()

init_db()

# ---------------- FACE SETUP ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def load_model():
    if os.path.exists("trainer.yml"):
        r = cv2.face.LBPHFaceRecognizer_create()
        r.read("trainer.yml")
        return r
    return None

recognizer = load_model()
qr_detector = cv2.QRCodeDetector()

# ---------------- TRAIN MODEL ----------------
def train_model():
    faces_data = []
    labels = []

    for user in os.listdir(FACE_DIR):
        user_path = os.path.join(FACE_DIR, user)

        if not os.path.isdir(user_path):
            continue

        try:
            uid = int(user.split("_")[1])
        except:
            continue

        for img in os.listdir(user_path):
            img_path = os.path.join(user_path, img)
            img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img_gray is None:
                continue

            detected = face_cascade.detectMultiScale(img_gray)

            for (x, y, w, h) in detected:
                faces_data.append(img_gray[y:y+h, x:x+w])
                labels.append(uid)

    if len(faces_data) == 0:
        return

    recognizer_new = cv2.face.LBPHFaceRecognizer_create()
    recognizer_new.train(faces_data, np.array(labels))
    recognizer_new.save("trainer.yml")

    global recognizer
    recognizer = recognizer_new

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- REGISTER REGULAR USER ----------------
@app.route("/regular-register", methods=["GET", "POST"])
def regular_register():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]

        db = sqlite3.connect(DB)
        cur = db.cursor()
        cur.execute("INSERT INTO regular_users(name, role) VALUES (?,?)", (name, role))
        user_id = cur.lastrowid
        db.commit()
        db.close()

        user_folder = os.path.join(FACE_DIR, f"user_{user_id}")
        os.makedirs(user_folder, exist_ok=True)

        cap = cv2.VideoCapture(0)
        count = 0

        while count < 20:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x,y,w,h) in faces:
                count += 1
                cv2.imwrite(f"{user_folder}/{count}.jpg", gray[y:y+h,x:x+w])
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            cv2.imshow("Register Face", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        train_model()

        return render_template("result.html", status="Regular User Registered Successfully")

    return render_template("regular_register.html")

# ---------------- VISITOR REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        purpose = request.form["purpose"]

        db = sqlite3.connect(DB)
        cur = db.cursor()
        cur.execute(
            "INSERT INTO visitors(name, purpose, entry_time) VALUES (?, ?, ?)",
            (name, purpose, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        vid = cur.lastrowid
        db.commit()
        db.close()

        qr = qrcode.make(f"VISITOR_{vid}")
        qr_path = os.path.join(QR_DIR, f"{vid}.png")
        qr.save(qr_path)

        return render_template("result.html",
                               status="Visitor Registered Successfully",
                               qr="/" + qr_path)

    return render_template("register.html")

# ---------------- SCAN (QR + FACE) ----------------
@app.route("/scan")
def scan():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return render_template("result.html", status="Camera not accessible")

    start = time.time()
    status = "No QR or Face Detected"

    while time.time() - start < 10:   # 10 second timeout
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ---------------- QR DETECTION ----------------
        data, bbox, _ = qr_detector.detectAndDecode(frame)

        if data:
            print("QR detected:", data)

            if data.startswith("VISITOR_"):
                vid = data.split("_")[1]

                db = sqlite3.connect(DB)
                cur = db.cursor()

                cur.execute("SELECT exit_time FROM visitors WHERE id=?", (vid,))
                result = cur.fetchone()

                if result and result[0] is None:
                    cur.execute(
                        "UPDATE visitors SET exit_time=? WHERE id=?",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vid)
                    )
                    status = "Visitor Exit Recorded Successfully"
                else:
                    status = "Already Exited or Invalid"

                db.commit()
                db.close()

            cap.release()
            cv2.destroyAllWindows()
            return render_template("result.html", status=status)

        # ---------------- FACE DETECTION ----------------
        if recognizer:
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                try:
                    uid, conf = recognizer.predict(gray[y:y+h, x:x+w])

                    if conf < 65:
                        db = sqlite3.connect(DB)
                        cur = db.cursor()

                        cur.execute("SELECT name, role FROM regular_users WHERE id=?", (uid,))
                        user = cur.fetchone()

                        if user:
                            cur.execute(
                                "UPDATE regular_users SET last_entry=? WHERE id=?",
                                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), uid)
                            )
                            status = f"{user[0]} ({user[1]}) Entry Recorded"

                        db.commit()
                        db.close()

                        cap.release()
                        cv2.destroyAllWindows()
                        return render_template("result.html", status=status)

                except:
                    continue

        cv2.imshow("Scanning...", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    return render_template("result.html", status="Scan Timeout – Try Again")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    db = sqlite3.connect(DB)
    cur = db.cursor()

    cur.execute("SELECT * FROM visitors ORDER BY id DESC")
    visitors = cur.fetchall()

    cur.execute("SELECT * FROM regular_users ORDER BY id DESC")
    regulars = cur.fetchall()

    db.close()

    return render_template("dashboard.html",
                           visitors=visitors,
                           regulars=regulars)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)