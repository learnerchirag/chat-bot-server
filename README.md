# Authentication Flow - Session-Based Authentication

This project implements a **session-based authentication** mechanism for managing user conversations in the chat-bot. The authentication system is designed to associate every conversation with a session while ensuring security and usability.

## **Overview**
- Authentication is **session-based**, meaning each user is assigned a unique session when they start a conversation.
- Sessions are **valid for 1 hour** from the time of creation.
- Each **session is linked to an IP address**, ensuring that only **one active session** is associated with a user at a time.
- **Email authentication** is used but is **not password-protected** for now, as the chat-bot serves an **informational purpose only**.

## **Authentication Flow**
1. **Session Creation**
   - When a user initiates a conversation, a **new session ID** is generated.
   - The session is **associated with the user's IP address** to prevent multiple simultaneous sessions.
   
2. **Session Validation**
   - Every request checks if a **valid session** exists for the IP address.
   - If the session is **older than 1 hour**, it is invalidated, and a new session must be created.

3. **Email Usage (Without Password Protection)**
   - Users provide their **email for identification**, but no password is required.
   - This keeps authentication lightweight, as the chat-bot is purely for informational purposes.

## **Security Considerations**
- **IP Binding**: Ensures that only one session is linked per user at a time, preventing unauthorized session sharing.
- **Short Session Lifetime**: Sessions expire in **1 hour**, reducing security risks from session hijacking.
- **No Persistent User Data**: Since there is no password storage, risks related to credential leaks are eliminated.

## **Future Enhancements**
- Implementing **OAuth or JWT-based authentication** for enhanced security.
- Adding **rate limiting** to prevent abuse.
- Introducing **optional password protection** for email-based login.

## **Setup & Prerequisites**
### **Requirements**
- **Python 3.8+**
- **FastAPI** framework
- **MongoDB** as the database
- **Infisical** for remote secret management
- **requirements.txt** file for dependency installation

### **Installation & Setup**
1. **Clone the repository**
   ```sh
   git clone https://github.com/your-repo.git
   cd your-repo
   ```

2. **Create a virtual environment** (recommended)
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables** using Infisical:
   - Ensure your Infisical environment is configured.
   - Retrieve secrets and set them in `.env` file or load them dynamically in the application.

5. **Run the FastAPI server**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API documentation**
   - Open your browser and navigate to: [http://localhost:8000/docs](http://localhost:8000/docs)

---
This authentication system ensures a **secure and efficient** method of managing user sessions while keeping it simple for informational interactions.