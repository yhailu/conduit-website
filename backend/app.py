import os
import csv
import io
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session, send_from_directory, Response
from flask_cors import CORS
from supabase import create_client, Client

load_dotenv()

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
app = Flask(__name__, static_folder=None)  # disable built-in static; we handle it ourselves
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-me')

ALLOWED_ORIGINS = [
    'http://localhost:5000',
    'http://127.0.0.1:5000',
]
# Add production origin from env (e.g. https://conduit-website.onrender.com)
if os.getenv('RENDER_EXTERNAL_URL'):
    ALLOWED_ORIGINS.append(os.getenv('RENDER_EXTERNAL_URL'))
if os.getenv('CORS_ORIGIN'):
    ALLOWED_ORIGINS.append(os.getenv('CORS_ORIGIN'))

CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
NOTIFY_EMAIL = os.getenv('NOTIFY_EMAIL', '')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_authenticated_client():
    """Return a Supabase client authenticated with the current session token, or None."""
    token = session.get('access_token')
    if not token:
        return None
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        client.auth.set_session(session['access_token'], session.get('refresh_token', ''))
        return client
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Static file serving — clean URLs
# ---------------------------------------------------------------------------

@app.route('/')
def serve_index():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    # 1. Redirect /foo.html → /foo (strip .html from URL bar)
    if path.endswith('.html'):
        clean = path[:-5]  # remove .html
        if clean.endswith('/index'):
            clean = clean[:-6]  # /blog/index → /blog
        return redirect(f'/{clean}', code=301)

    # 2. Exact file match (css, js, images, etc.)
    full = os.path.join(STATIC_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(STATIC_DIR, path)

    # 3. Try path/index.html (e.g. /blog → blog/index.html)
    index_path = os.path.join(path, 'index.html')
    if os.path.isfile(os.path.join(STATIC_DIR, index_path)):
        return send_from_directory(STATIC_DIR, index_path)

    # 4. Try path.html (e.g. /consultation → consultation.html)
    html_path = path + '.html'
    if os.path.isfile(os.path.join(STATIC_DIR, html_path)):
        return send_from_directory(STATIC_DIR, html_path)

    # 5. 404
    return 'Not Found', 404


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    try:
        res = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {'full_name': full_name}
            }
        })

        user = res.user
        sess = res.session

        if sess:
            session['access_token'] = sess.access_token
            session['refresh_token'] = sess.refresh_token

        return jsonify({
            'message': 'Signup successful. Check your email to confirm.',
            'user': {
                'id': str(user.id) if user else None,
                'email': user.email if user else email,
            },
            'confirmed': sess is not None,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    try:
        res = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password,
        })

        sess = res.session
        user = res.user

        session['access_token'] = sess.access_token
        session['refresh_token'] = sess.refresh_token

        return jsonify({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': (user.user_metadata or {}).get('full_name', ''),
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        client = get_authenticated_client()
        if client:
            client.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return jsonify({'message': 'Logged out.'})


@app.route('/api/auth/me', methods=['GET'])
def me():
    token = session.get('access_token')
    if not token:
        return jsonify({'user': None}), 200

    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        client.auth.set_session(token, session.get('refresh_token', ''))
        user_resp = client.auth.get_user()
        user = user_resp.user

        if not user:
            session.clear()
            return jsonify({'user': None}), 200

        return jsonify({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': (user.user_metadata or {}).get('full_name', ''),
            }
        })
    except Exception:
        session.clear()
        return jsonify({'user': None}), 200


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Please enter your email address.'}), 400

    try:
        supabase.auth.reset_password_for_email(email, {
            'redirect_to': request.host_url.rstrip('/') + '/login'
        })
        return jsonify({'message': 'Password reset email sent! Check your inbox.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/auth/google', methods=['GET'])
def google_oauth():
    try:
        res = supabase.auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {
                'redirect_to': request.host_url.rstrip('/') + '/api/auth/callback'
            }
        })
        return redirect(res.url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback from Supabase. The access_token comes as a URL fragment
    or as query params depending on Supabase config. We store them in the session."""
    access_token = request.args.get('access_token')
    refresh_token = request.args.get('refresh_token')

    if access_token:
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token or ''
        return redirect('/')

    # Supabase sometimes puts tokens in the URL fragment (#access_token=...).
    # We serve a small page that reads the fragment and posts it back.
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Authenticating...</title></head>
    <body>
    <script>
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);
      const access_token = params.get('access_token');
      const refresh_token = params.get('refresh_token');
      if (access_token) {
        fetch('/api/auth/callback/complete', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({ access_token, refresh_token })
        }).then(() => window.location.href = '/');
      } else {
        window.location.href = '/login';
      }
    </script>
    </body>
    </html>
    '''


@app.route('/api/auth/callback/complete', methods=['POST'])
def auth_callback_complete():
    data = request.get_json(silent=True) or {}
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token', '')
    if access_token:
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        return jsonify({'ok': True})
    return jsonify({'error': 'No token'}), 400


# ---------------------------------------------------------------------------
# Email capture endpoints
# ---------------------------------------------------------------------------

@app.route('/api/email-capture', methods=['POST'])
def email_capture():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    source = data.get('source', 'unknown')

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    try:
        row = {'email': email, 'source': source}
        if data.get('signed_up_at'):
            row['signed_up_at'] = data['signed_up_at']
        supabase.table('signups').insert(row).execute()
        return jsonify({'message': 'Email captured.'})
    except Exception as e:
        err_str = str(e)
        if '23505' in err_str:
            return jsonify({'message': 'Email already registered.'})
        return jsonify({'error': err_str}), 500


@app.route('/api/admin/emails', methods=['GET'])
def admin_emails():
    try:
        res = supabase.table('signups').select('*').order('signed_up_at', desc=True).execute()
        return jsonify({'emails': res.data or []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/emails/export', methods=['GET'])
def admin_emails_export():
    try:
        res = supabase.table('signups').select('*').order('signed_up_at', desc=True).execute()
        emails = res.data or []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Email', 'Source', 'Signed Up At'])
        for e in emails:
            writer.writerow([e.get('email', ''), e.get('source', ''), e.get('signed_up_at', '')])

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=orchestraflow-signups.csv'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------

def send_notification_email(consultation):
    """Send an email notification about a new consultation booking."""
    if not SMTP_USER or not SMTP_PASSWORD or not NOTIFY_EMAIL:
        app.logger.warning('SMTP not configured — skipping email notification.')
        return False

    subject = f"New Consultation Request from {consultation['name']}"

    html_body = f"""
    <h2>🎯 New Consultation Booking</h2>
    <table style="border-collapse:collapse; font-family:Arial,sans-serif;">
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Name</td><td style="padding:8px;">{consultation['name']}</td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Email</td><td style="padding:8px;"><a href="mailto:{consultation['email']}">{consultation['email']}</a></td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Phone</td><td style="padding:8px;">{consultation.get('phone', 'N/A')}</td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Company</td><td style="padding:8px;">{consultation['company']}</td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Company Size</td><td style="padding:8px;">{consultation.get('company_size', 'N/A')}</td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Industry</td><td style="padding:8px;">{consultation.get('industry', 'N/A')}</td></tr>
      <tr><td style="padding:8px; font-weight:bold; color:#555;">Message</td><td style="padding:8px;">{consultation.get('message', 'N/A')}</td></tr>
    </table>
    <br>
    <p style="color:#888; font-size:0.85em;">Reply to the customer within 2 hours as promised on the site.</p>
    """

    plain_body = (
        f"New Consultation Booking\n\n"
        f"Name: {consultation['name']}\n"
        f"Email: {consultation['email']}\n"
        f"Phone: {consultation.get('phone', 'N/A')}\n"
        f"Company: {consultation['company']}\n"
        f"Company Size: {consultation.get('company_size', 'N/A')}\n"
        f"Industry: {consultation.get('industry', 'N/A')}\n"
        f"Message: {consultation.get('message', 'N/A')}\n"
    )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = NOTIFY_EMAIL
    msg['Reply-To'] = consultation['email']
    msg.attach(MIMEText(plain_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        app.logger.info(f"Notification email sent for {consultation['email']}")
        return True
    except Exception as e:
        app.logger.error(f"Failed to send notification email: {e}")
        return False


# ---------------------------------------------------------------------------
# Consultation booking endpoint
# ---------------------------------------------------------------------------

@app.route('/api/consultation', methods=['POST'])
def book_consultation():
    data = request.get_json(silent=True) or {}

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    company = data.get('company', '').strip()
    company_size = data.get('company_size', '').strip()
    industry = data.get('industry', '').strip()
    message = data.get('message', '').strip()

    # Validation
    if not name or not email or not company:
        return jsonify({'error': 'Name, email, and company are required.'}), 400

    consultation = {
        'name': name,
        'email': email,
        'phone': phone or None,
        'company': company,
        'company_size': company_size or None,
        'industry': industry or None,
        'message': message or None,
    }

    # 1. Save to database
    try:
        supabase.table('consultations').insert(consultation).execute()
    except Exception as e:
        app.logger.error(f"Failed to save consultation: {e}")
        return jsonify({'error': 'Failed to save your request. Please try again.'}), 500

    # 2. Send email notification in background thread (don't block the response)
    threading.Thread(target=send_notification_email, args=(consultation,), daemon=True).start()

    return jsonify({'message': 'Consultation request received! We\'ll contact you within 2 hours.'})


# ---------------------------------------------------------------------------
# Newsletter endpoints
# ---------------------------------------------------------------------------

@app.route('/api/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    source = data.get('source', 'website')

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    try:
        supabase.table('newsletter_subscribers').insert({
            'email': email,
            'source': source,
            'is_active': True
        }).execute()
        return jsonify({'message': 'Subscribed successfully!'})
    except Exception as e:
        if '23505' in str(e):
            # Already subscribed — reactivate if needed
            try:
                supabase.table('newsletter_subscribers').update({
                    'is_active': True,
                    'unsubscribed_at': None
                }).eq('email', email).execute()
            except Exception:
                pass
            return jsonify({'message': 'Welcome back! You\'re resubscribed.'})
        return jsonify({'error': str(e)}), 500


@app.route('/api/newsletter/unsubscribe', methods=['POST'])
def newsletter_unsubscribe():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    try:
        supabase.table('newsletter_subscribers').update({
            'is_active': False,
            'unsubscribed_at': 'now()'
        }).eq('email', email).execute()
        return jsonify({'message': 'Unsubscribed successfully.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/newsletter/subscribers', methods=['GET'])
def newsletter_subscribers():
    try:
        res = supabase.table('newsletter_subscribers').select('*').eq('is_active', True).order('subscribed_at', desc=True).execute()
        return jsonify({'subscribers': res.data or [], 'count': len(res.data or [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/newsletter/stats', methods=['GET'])
def newsletter_stats():
    try:
        subs = supabase.table('newsletter_subscribers').select('id, is_active, subscribed_at').execute()
        campaigns = supabase.table('newsletter_campaigns').select('id, status').execute()

        all_subs = subs.data or []
        active = [s for s in all_subs if s.get('is_active')]
        sent_campaigns = [c for c in (campaigns.data or []) if c.get('status') == 'sent']

        return jsonify({
            'active_subscribers': len(active),
            'total_subscribers': len(all_subs),
            'campaigns_sent': len(sent_campaigns)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/newsletter/send', methods=['POST'])
def newsletter_send():
    data = request.get_json(silent=True) or {}
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not subject or not body:
        return jsonify({'error': 'Subject and body are required.'}), 400

    # Get active subscribers
    try:
        res = supabase.table('newsletter_subscribers').select('email').eq('is_active', True).execute()
        subscribers = [s['email'] for s in (res.data or [])]
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subscribers: {e}'}), 500

    if not subscribers:
        return jsonify({'error': 'No active subscribers to send to.'}), 400

    # Save campaign
    try:
        campaign = supabase.table('newsletter_campaigns').insert({
            'subject': subject,
            'body': body,
            'recipient_count': len(subscribers),
            'status': 'sending'
        }).execute()
        campaign_id = campaign.data[0]['id'] if campaign.data else None
    except Exception as e:
        return jsonify({'error': f'Failed to save campaign: {e}'}), 500

    # Send emails in background
    def send_campaign():
        success_count = 0
        for email in subscribers:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = SMTP_USER
                msg['To'] = email

                # Plain text version
                msg.attach(MIMEText(body, 'plain'))

                # HTML version
                html = f"""
                <div style="max-width:600px; margin:0 auto; font-family:Arial,sans-serif; color:#333;">
                  <div style="padding:24px 0; border-bottom:2px solid #10b981; margin-bottom:24px;">
                    <h1 style="font-size:1.3rem; margin:0; color:#0f172a;">orchestraflow</h1>
                  </div>
                  <h2 style="font-size:1.4rem; color:#0f172a; margin-bottom:16px;">{subject}</h2>
                  <div style="font-size:1rem; line-height:1.7; color:#475569;">
                    {body.replace(chr(10), '<br>')}
                  </div>
                  <div style="margin-top:32px; padding-top:16px; border-top:1px solid #e2e8f0; font-size:0.8rem; color:#94a3b8;">
                    <p>You received this because you subscribed to OrchestraFlow updates.</p>
                    <p><a href="#" style="color:#94a3b8;">Unsubscribe</a></p>
                  </div>
                </div>
                """
                msg.attach(MIMEText(html, 'html'))

                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)
                success_count += 1
            except Exception as e:
                app.logger.error(f"Failed to send to {email}: {e}")

        # Update campaign status
        if campaign_id:
            try:
                status = 'sent' if success_count > 0 else 'failed'
                supabase.table('newsletter_campaigns').update({
                    'status': status,
                    'sent_at': 'now()'
                }).eq('id', campaign_id).execute()
            except Exception:
                pass

        app.logger.info(f"Newsletter sent to {success_count}/{len(subscribers)} subscribers")

    threading.Thread(target=send_campaign, daemon=True).start()

    return jsonify({
        'message': f'Newsletter queued for {len(subscribers)} subscribers!',
        'recipient_count': len(subscribers)
    })


@app.route('/api/newsletter/campaigns', methods=['GET'])
def newsletter_campaigns():
    try:
        res = supabase.table('newsletter_campaigns').select('*').order('created_at', desc=True).limit(20).execute()
        return jsonify({'campaigns': res.data or []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)
