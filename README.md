# **🎯 FaceTrack – Face Recognition Based Attendance System**
FaceTrack is a secure, ML-powered attendance system that uses face recognition to automatically mark attendance.
It eliminates proxy attendance and manual errors by verifying a person’s identity through facial features.


## Key Features
  ### Admin Features
   1. Secure admin login (Django Admin – session based)
   2. Add users by:
     1. Capturing face image
     2. Providing email ID
   3. Automatically creates user accounts with a default password
   4. Stores facial embeddings securely in the database

 ### User Features
   1. Login using JWT authentication
   2. View personal attendance history
   3. Attendance is marked automatically using face recognition
   4. No manual attendance entry

## 🔐 Authentication Design
This project intentionally uses two authentication mechanisms:

### Django Admin (Session-based)
   1. Used only for admin
      
### JWT Authentication (Token-based)
   1. Used for normal users
   2. Secures all user APIs


## 🧬 Face Recognition Flow
  ### ➤ Admin Face Enrollment
   1. Admin captures a user’s face image
   2. Backend extracts facial embedding using ML model
   3. Embedding is stored in FaceProfile table
   4. User account is created automatically

  ### ➤ Attendance Marking
   1. User opens camera and captures image
   2. Backend extracts face embedding
   3. Embedding is compared with stored embeddings
   4. If match confidence is above threshold:
       -> Attendance marked as Present
   5. Duplicate attendance for the same day is prevented
   

## 🧠 Why Face Embeddings (Not Images)?
   1. Raw images are large and insecure
   2. Embeddings are:
		1. Lightweight numeric vectors
		2. Cannot be reverse-engineered into faces
		3. Faster for similarity comparison
   3. This makes the system secure and scalable.


## 🛡️ Security Considerations
   1. Attendance cannot be marked using Postman or fake requests
   2. CSRF protection enabled for admin
   3. JWT expiry automatically logs users out
   4. Server is the single source of truth


## ☁️ Deployment Challenges & Solutions
  ### Challenge
   1. Free cloud tiers have limited memory (512MB)
   2. Deep learning models can cause OOM crashes

  ### Solution
   1. Replaced heavy RetinaFace detector with OpenCV
   2. Reduced memory usage significantly
   3. Tuned Gunicorn to single worker
   4. Optimized image preprocessing
### This reflects real-world engineering trade-offs.


## 🧠 What This Project Demonstrates
   1. Real-world backend architecture
   2. Secure authentication design
   3. ML integration with backend APIs
   4. Production deployment problem-solving
   5. Performance & memory optimization
   6. Clean separation of concerns
