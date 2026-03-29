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
from werkzeug.security import check_password_hash, generate_password_hash
import stripe
import hashlib, time

load_dotenv()

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
app = Flask(__name__, static_folder=None)  # disable built-in static; we handle it ourselves
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-me')

# Register HeroCall platform blueprint (customer dashboard API)
from platform_api import platform_bp
app.register_blueprint(platform_bp)

ALLOWED_ORIGINS = [
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'https://herocall.io',
    'https://www.herocall.io',
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

# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
stripe.api_key = STRIPE_SECRET_KEY


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
    index_path = path + '/index.html'
    if os.path.isfile(os.path.join(STATIC_DIR, path, 'index.html')):
        return send_from_directory(STATIC_DIR, index_path)

    # 3b. Preview pages: /preview/TOKEN → preview/index.html
    if path.startswith('preview/') and '.' not in path:
        preview_page = os.path.join(STATIC_DIR, 'preview', 'index.html')
        if os.path.isfile(preview_page):
            return send_from_directory(os.path.join(STATIC_DIR, 'preview'), 'index.html')

    # 4. Try path.html (e.g. /consultation → consultation.html)
    html_path = path + '.html'
    if os.path.isfile(os.path.join(STATIC_DIR, html_path)):
        return send_from_directory(STATIC_DIR, html_path)

    # 5. Custom 404 page
    error_page = os.path.join(STATIC_DIR, '404.html')
    if os.path.isfile(error_page):
        return send_from_directory(STATIC_DIR, '404.html'), 404
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
            headers={'Content-Disposition': 'attachment; filename=HeroCall-signups.csv'}
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
    <hr style="border:none; border-top:1px solid #eee; margin:16px 0;">
    <p style="font-size:0.8em; color:#aaa; text-align:center;">
      <a href="https://x.com/herocallio" style="color:#aaa; margin:0 4px;">X/Twitter</a> · 
      <a href="https://instagram.com/herocall.io" style="color:#aaa; margin:0 4px;">Instagram</a> · 
      <a href="https://linkedin.com/company/herocall" style="color:#aaa; margin:0 4px;">LinkedIn</a> · 
      <a href="https://tryherocall.io" style="color:#10b981;">tryherocall.io</a>
    </p>
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
                    <h1 style="font-size:1.3rem; margin:0; color:#0f172a;">HeroCall</h1>
                  </div>
                  <h2 style="font-size:1.4rem; color:#0f172a; margin-bottom:16px;">{subject}</h2>
                  <div style="font-size:1rem; line-height:1.7; color:#475569;">
                    {body.replace(chr(10), '<br>')}
                  </div>
                  <div style="margin-top:32px; padding-top:20px; border-top:1px solid #e2e8f0; text-align:center;">
                    <p style="margin-bottom:12px;">
                      <a href="https://x.com/herocallio" style="display:inline-block; margin:0 6px; text-decoration:none;">
                        <img src="https://cdn-icons-png.flaticon.com/24/5968/5968958.png" width="20" height="20" alt="X" style="vertical-align:middle;">
                      </a>
                      <a href="https://instagram.com/herocall.io" style="display:inline-block; margin:0 6px; text-decoration:none;">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174855.png" width="20" height="20" alt="Instagram" style="vertical-align:middle;">
                      </a>
                      <a href="https://linkedin.com/company/herocall" style="display:inline-block; margin:0 6px; text-decoration:none;">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" width="20" height="20" alt="LinkedIn" style="vertical-align:middle;">
                      </a>
                    </p>
                    <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:4px;">You received this because you subscribed to HeroCall updates.</p>
                    <p style="font-size:0.75rem;"><a href="#" style="color:#94a3b8;">Unsubscribe</a> · <a href="https://tryherocall.io" style="color:#10b981;">tryherocall.io</a></p>
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
# Portal endpoints (Web Development client demos)
# ---------------------------------------------------------------------------

@app.route('/api/portal/login', methods=['POST'])
def portal_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    try:
        res = supabase.table('portal_clients').select('*').eq('email', email).execute()
        clients = res.data or []

        if not clients:
            return jsonify({'error': 'Invalid email or password.'}), 401

        client = clients[0]
        if not check_password_hash(client['password_hash'], password):
            return jsonify({'error': 'Invalid email or password.'}), 401

        session['portal_client_id'] = client['id']
        session['portal_email'] = client['email']

        return jsonify({
            'message': 'Login successful.',
            'client': {
                'id': client['id'],
                'email': client['email'],
                'business_name': client['business_name'],
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portal/me', methods=['GET'])
def portal_me():
    client_id = session.get('portal_client_id')
    if not client_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    try:
        res = supabase.table('portal_clients').select('id, email, business_name').eq('id', client_id).execute()
        clients = res.data or []
        if not clients:
            session.pop('portal_client_id', None)
            session.pop('portal_email', None)
            return jsonify({'error': 'Client not found.'}), 401

        return jsonify({'client': clients[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portal/logout', methods=['POST'])
def portal_logout():
    session.pop('portal_client_id', None)
    session.pop('portal_email', None)
    return jsonify({'message': 'Logged out.'})


@app.route('/api/portal/demo', methods=['GET'])
def portal_demo():
    client_id = session.get('portal_client_id')
    if not client_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    try:
        res = supabase.table('portal_clients').select(
            'business_name, original_url, demo_url, improvements, metrics'
        ).eq('id', client_id).execute()
        clients = res.data or []

        if not clients:
            return jsonify({'error': 'Demo not found.'}), 404

        return jsonify(clients[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portal/request-build', methods=['POST'])
def portal_request_build():
    client_id = session.get('portal_client_id')
    if not client_id:
        return jsonify({'error': 'Not authenticated.'}), 401

    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()

    try:
        supabase.table('build_requests').insert({
            'client_id': client_id,
            'message': message or None,
        }).execute()
        return jsonify({'message': 'Build request submitted.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Portal demo file serving (authenticated, scoped to client)
# ---------------------------------------------------------------------------

DEMOS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'portal', 'demos'))

@app.route('/api/portal/demo-page', methods=['GET'])
def portal_demo_page():
    """Serve the client's demo HTML file. Only accessible to the authenticated client
    whose demo_url points to this route."""
    client_id = session.get('portal_client_id')
    if not client_id:
        return 'Unauthorized', 401

    try:
        res = supabase.table('portal_clients').select('demo_url').eq('id', client_id).execute()
        clients = res.data or []
        if not clients or not clients[0].get('demo_url'):
            return 'Demo not found', 404

        # demo_url stores the filename (e.g. "pipexpress")
        demo_file = clients[0]['demo_url'] + '.html'
        demo_path = os.path.join(DEMOS_DIR, demo_file)

        if not os.path.isfile(demo_path):
            return 'Demo not found', 404

        return send_from_directory(DEMOS_DIR, demo_file)
    except Exception as e:
        return str(e), 500


@app.route('/api/portal/demo-screenshot', methods=['GET'])
def portal_demo_screenshot():
    """Serve a screenshot of the client's demo site."""
    client_id = session.get('portal_client_id')
    if not client_id:
        return 'Unauthorized', 401

    try:
        res = supabase.table('portal_clients').select('demo_url').eq('id', client_id).execute()
        clients = res.data or []
        if not clients or not clients[0].get('demo_url'):
            return 'Demo not found', 404

        demo_name = clients[0]['demo_url']

        # Serve stored screenshot (png or jpg)
        for ext in ['png', 'jpg', 'jpeg']:
            screenshot_file = demo_name + '.' + ext
            if os.path.isfile(os.path.join(DEMOS_DIR, screenshot_file)):
                return send_from_directory(DEMOS_DIR, screenshot_file)

        return 'Screenshot not found', 404
    except Exception as e:
        return str(e), 500


# ---------------------------------------------------------------------------
# Web Development lead capture
# ---------------------------------------------------------------------------

@app.route('/api/webdev/leads', methods=['POST'])
def webdev_leads():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    try:
        row = {'email': email}
        if data.get('business_name'):
            row['business_name'] = data['business_name'].strip()
        if data.get('website_url'):
            row['website_url'] = data['website_url'].strip()
        if data.get('phone'):
            row['phone'] = data['phone'].strip()
        if data.get('source'):
            row['source'] = data['source']
        if data.get('city'):
            row['city'] = data['city'].strip()
        if data.get('state'):
            row['state'] = data['state'].strip()

        supabase.table('webdev_leads').insert(row).execute()
        return jsonify({'message': 'Lead captured.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Public preview (token-based, no login required)
# ---------------------------------------------------------------------------

@app.route('/api/preview/<token>', methods=['GET'])
def preview_data(token):
    """Return preview data for a public token link."""
    try:
        res = supabase.table('preview_links').select(
            'business_name, original_url, demo_file, expires_at, views'
        ).eq('token', token).execute()
        links = res.data or []

        if not links:
            return jsonify({'error': 'Preview not found.'}), 404

        link = links[0]

        # Check expiration
        if link.get('expires_at'):
            from datetime import datetime, timezone
            expires = datetime.fromisoformat(link['expires_at'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expires:
                return jsonify({'error': 'Preview expired.'}), 410

        return jsonify({
            'business_name': link['business_name'],
            'original_url': link.get('original_url', ''),
            'demo_file': link.get('demo_file', ''),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<token>/demo', methods=['GET'])
def preview_demo(token):
    """Serve the demo HTML for a public preview link."""
    try:
        res = supabase.table('preview_links').select('demo_file, expires_at').eq('token', token).execute()
        links = res.data or []

        if not links:
            return 'Not found', 404

        link = links[0]

        if link.get('expires_at'):
            from datetime import datetime, timezone
            expires = datetime.fromisoformat(link['expires_at'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expires:
                return 'Preview expired', 410

        demo_file = link.get('demo_file', '') + '.html'
        if not os.path.isfile(os.path.join(DEMOS_DIR, demo_file)):
            return 'Demo not found', 404

        return send_from_directory(DEMOS_DIR, demo_file)
    except Exception as e:
        return str(e), 500


@app.route('/api/preview/<token>/view', methods=['POST'])
def preview_track_view(token):
    """Increment view count for a preview link."""
    try:
        res = supabase.table('preview_links').select('id, views').eq('token', token).execute()
        links = res.data or []
        if links:
            views = (links[0].get('views') or 0) + 1
            supabase.table('preview_links').update({'views': views}).eq('id', links[0]['id']).execute()
        return jsonify({'ok': True})
    except Exception:
        return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Billing (Stripe)
# ---------------------------------------------------------------------------

def _get_stripe_customer_id():
    """Get the Stripe customer ID for the currently logged-in user."""
    token = session.get('access_token')
    if not token:
        return None, None
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        client.auth.set_session(token, session.get('refresh_token', ''))
        user_resp = client.auth.get_user()
        user = user_resp.user
        if not user:
            return None, None

        # Check if user has a stripe_customer_id in metadata
        meta = user.user_metadata or {}
        stripe_id = meta.get('stripe_customer_id')

        if not stripe_id:
            # Search Stripe by email
            customers = stripe.Customer.list(email=user.email, limit=1)
            if customers.data:
                stripe_id = customers.data[0].id
            else:
                return user, None

        return user, stripe_id
    except Exception:
        return None, None


@app.route('/api/billing', methods=['GET'])
def billing_info():
    """Return subscription, payment method, and invoice history."""
    user, stripe_customer_id = _get_stripe_customer_id()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    result = {
        'subscription': None,
        'payment_method': None,
        'invoices': [],
    }

    if not stripe_customer_id or not STRIPE_SECRET_KEY:
        return jsonify(result)

    try:
        # Get subscriptions
        subs = stripe.Subscription.list(customer=stripe_customer_id, limit=1, status='all')
        if subs.data:
            sub = subs.data[0]
            plan = sub['items']['data'][0]['plan'] if sub['items']['data'] else {}
            amount = plan.get('amount', 0)
            interval = plan.get('interval', 'month')

            result['subscription'] = {
                'id': sub.id,
                'status': sub.status,
                'plan_name': plan.get('nickname') or plan.get('product', ''),
                'price': f"${amount / 100:.2f}/{interval}" if amount else '',
                'current_period': f"{_ts_to_date(sub.current_period_start)} — {_ts_to_date(sub.current_period_end)}",
                'next_billing': _ts_to_date(sub.current_period_end),
                'started': _ts_to_date(sub.start_date) if sub.start_date else _ts_to_date(sub.created),
                'cancel_at_period_end': sub.cancel_at_period_end,
            }

            # Try to resolve product name
            try:
                product = stripe.Product.retrieve(plan.get('product', ''))
                result['subscription']['plan_name'] = product.name
            except Exception:
                pass

        # Get payment methods
        pms = stripe.PaymentMethod.list(customer=stripe_customer_id, type='card', limit=1)
        if pms.data:
            pm = pms.data[0]
            card = pm.card
            result['payment_method'] = {
                'brand': card.brand.title() if card.brand else 'Card',
                'last4': card.last4,
                'exp_month': str(card.exp_month).zfill(2),
                'exp_year': str(card.exp_year),
            }

        # Get invoices
        invoices = stripe.Invoice.list(customer=stripe_customer_id, limit=24)
        result['invoices'] = [{
            'id': inv.id,
            'date': _ts_to_date(inv.created),
            'amount': inv.amount_paid or inv.total,
            'status': inv.status,
            'pdf': inv.invoice_pdf,
        } for inv in invoices.data]

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(result)


@app.route('/api/billing/portal', methods=['POST'])
def billing_portal():
    """Create a Stripe Customer Portal session for managing subscription/payment."""
    user, stripe_customer_id = _get_stripe_customer_id()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    if not stripe_customer_id:
        return jsonify({'error': 'No billing account found'}), 404

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=request.host_url.rstrip('/') + '/billing',
        )
        return jsonify({'url': portal_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/billing/cancel', methods=['POST'])
def billing_cancel():
    """Cancel subscription at end of billing period."""
    user, stripe_customer_id = _get_stripe_customer_id()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        subs = stripe.Subscription.list(customer=stripe_customer_id, limit=1, status='active')
        if not subs.data:
            return jsonify({'error': 'No active subscription found'}), 404

        stripe.Subscription.modify(subs.data[0].id, cancel_at_period_end=True)
        return jsonify({'ok': True, 'message': 'Subscription will cancel at end of billing period.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for subscription events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', '')

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return 'Invalid signature', 400
    else:
        event = stripe.Event.construct_from(request.get_json(), stripe.api_key)

    # Handle events as needed
    event_type = event['type']
    # Log for now — extend as needed
    print(f"[Stripe] {event_type}: {event['data']['object'].get('id', '')}")

    return jsonify({'received': True})


def _ts_to_date(ts):
    """Convert Unix timestamp to readable date."""
    if not ts:
        return '—'
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%b %d, %Y')


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not email or not message:
        return jsonify({'error': 'Email and message are required.'}), 400

    try:
        supabase.table('contact_messages').insert({
            'name': name or None,
            'email': email,
            'subject': subject or None,
            'message': message,
        }).execute()
        return jsonify({'message': 'Message sent.'})
    except Exception as e:
        # If table doesn't exist yet, still return success to user
        return jsonify({'message': 'Message received.'})


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)
