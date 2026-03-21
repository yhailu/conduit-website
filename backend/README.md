# OrchestraFlow Website - Python/Flask Backend

## Quick Setup

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Copy `.env.example` to `.env` (or edit the existing `.env`) and fill in your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_SECRET=your-google-secret
   FLASK_SECRET_KEY=some-random-secret
   ```

3. **Run the server**
   ```bash
   python app.py
   ```
   The server starts on `http://localhost:5000`. It serves the static HTML files **and** the API endpoints.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/signup` | Email/password signup |
| POST | `/api/auth/login` | Email/password login |
| POST | `/api/auth/logout` | Logout (clear session) |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/forgot-password` | Send password reset email |
| GET | `/api/auth/google` | Start Google OAuth flow |
| GET | `/api/auth/callback` | OAuth callback handler |
| POST | `/api/email-capture` | Save email to signups table |
| GET | `/api/admin/emails` | List all captured emails |
| GET | `/api/admin/emails/export` | Export emails as CSV download |

## Architecture

- **Flask** serves both the static site (HTML/CSS/JS) and the API under `/api/*`
- **supabase-py** handles all Supabase interactions server-side
- Auth tokens are stored in Flask server-side sessions (HTTP-only cookies)
- The frontend uses `fetch()` with `credentials: 'include'` - no Supabase JS SDK needed
