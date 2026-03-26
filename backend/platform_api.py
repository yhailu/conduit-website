"""
HeroCall Platform API — Customer self-serve dashboard backend.

Registers a Flask Blueprint with endpoints for:
  - Customer auth (signup/login with JWT)
  - Dashboard data
  - Agent CRUD
  - Call logs & appointments
  - Agent stats

Import and register this blueprint in app.py.
"""

import os
import uuid
import json
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client

from prompt_generator import generate_system_prompt, get_supported_industries
from vapi_client import create_assistant, assign_phone_number, get_call_logs as vapi_get_call_logs

# ---------------------------------------------------------------------------
# Blueprint setup
# ---------------------------------------------------------------------------

platform_bp = Blueprint("platform", __name__)

JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("FLASK_SECRET_KEY", "herocall-jwt-secret-change-me"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def _get_supabase() -> Client:
    """Return a Supabase client (reuse per-request via g)."""
    if "supabase" not in g:
        g.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return g.supabase


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _create_token(customer_id: str, email: str) -> str:
    payload = {
        "sub": customer_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def auth_required(f):
    """Decorator — requires valid JWT in Authorization header."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header."}), 401

        token = auth_header.split(" ", 1)[1]
        payload = _decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token."}), 401

        g.customer_id = payload["sub"]
        g.customer_email = payload.get("email", "")
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/auth/signup", methods=["POST"])
def platform_signup():
    """Create a new customer account."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    company_name = data.get("company_name", "").strip()
    phone = data.get("phone", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    sb = _get_supabase()

    # Check if email already exists
    existing = sb.table("customers").select("id").eq("email", email).execute()
    if existing.data:
        return jsonify({"error": "An account with this email already exists."}), 409

    customer_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)

    try:
        sb.table("customers").insert({
            "id": customer_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name or None,
            "company_name": company_name or None,
            "phone": phone or None,
            "plan": "trial",
            "status": "active",
        }).execute()
    except Exception as e:
        return jsonify({"error": f"Failed to create account: {e}"}), 500

    token = _create_token(customer_id, email)

    return jsonify({
        "message": "Account created successfully.",
        "token": token,
        "customer": {
            "id": customer_id,
            "email": email,
            "full_name": full_name,
            "company_name": company_name,
            "plan": "trial",
        },
    }), 201


@platform_bp.route("/api/platform/auth/login", methods=["POST"])
def platform_login():
    """Login and return a JWT."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    sb = _get_supabase()

    try:
        res = sb.table("customers").select("*").eq("email", email).execute()
        customers = res.data or []
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    if not customers:
        return jsonify({"error": "Invalid email or password."}), 401

    customer = customers[0]

    if not check_password_hash(customer["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    if customer.get("status") == "suspended":
        return jsonify({"error": "Your account has been suspended. Contact support."}), 403

    token = _create_token(customer["id"], customer["email"])

    return jsonify({
        "token": token,
        "customer": {
            "id": customer["id"],
            "email": customer["email"],
            "full_name": customer.get("full_name"),
            "company_name": customer.get("company_name"),
            "plan": customer.get("plan", "trial"),
        },
    })


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/dashboard", methods=["GET"])
@auth_required
def platform_dashboard():
    """Get customer dashboard overview: agents, recent calls, stats."""
    sb = _get_supabase()
    customer_id = g.customer_id

    # Fetch agents
    agents_res = sb.table("agents").select("*").eq("customer_id", customer_id).execute()
    agents = agents_res.data or []

    # Fetch recent calls (last 10)
    calls_res = (
        sb.table("call_logs")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    recent_calls = calls_res.data or []

    # Fetch upcoming appointments
    now_iso = datetime.now(timezone.utc).isoformat()
    appts_res = (
        sb.table("appointments")
        .select("*")
        .eq("customer_id", customer_id)
        .gte("appointment_date", now_iso)
        .order("appointment_date")
        .limit(5)
        .execute()
    )
    upcoming_appointments = appts_res.data or []

    # Aggregate stats
    all_calls = sb.table("call_logs").select("id, call_duration_seconds, call_outcome").eq("customer_id", customer_id).execute()
    all_calls_data = all_calls.data or []

    total_calls = len(all_calls_data)
    total_duration = sum(c.get("call_duration_seconds", 0) or 0 for c in all_calls_data)
    avg_duration = round(total_duration / total_calls) if total_calls > 0 else 0
    appointments_booked = sum(1 for c in all_calls_data if c.get("call_outcome") == "appointment_booked")

    # Customer info
    cust_res = sb.table("customers").select("email, full_name, company_name, plan, status, created_at").eq("id", customer_id).execute()
    customer_info = cust_res.data[0] if cust_res.data else {}

    return jsonify({
        "customer": customer_info,
        "agents": agents,
        "recent_calls": recent_calls,
        "upcoming_appointments": upcoming_appointments,
        "stats": {
            "total_calls": total_calls,
            "avg_call_duration_seconds": avg_duration,
            "appointments_booked": appointments_booked,
            "active_agents": sum(1 for a in agents if a.get("status") == "active"),
        },
    })


# ---------------------------------------------------------------------------
# Agents CRUD
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/agents", methods=["POST"])
@auth_required
def create_agent():
    """Create a new AI agent for the customer."""
    data = request.get_json(silent=True) or {}
    sb = _get_supabase()
    customer_id = g.customer_id

    business_name = data.get("business_name", "").strip()
    if not business_name:
        return jsonify({"error": "Business name is required."}), 400

    industry = data.get("industry", "").strip()
    services = data.get("services", [])
    business_hours = data.get("business_hours", {})
    calendar_url = data.get("calendar_url", "").strip() or None
    business_phone = data.get("business_phone", "").strip() or None
    business_address = data.get("business_address", "").strip() or None
    greeting_message = data.get("greeting_message", "").strip() or None
    agent_name = data.get("agent_name", "AI Receptionist").strip()

    # Generate system prompt
    system_prompt = generate_system_prompt(
        business_name=business_name,
        industry=industry,
        services=services,
        business_hours=business_hours,
        calendar_url=calendar_url,
        business_phone=business_phone,
        business_address=business_address,
        greeting_message=greeting_message,
        agent_name=agent_name,
    )

    # Create mock Vapi assistant
    vapi_result = create_assistant(
        name=f"{business_name} - {agent_name}",
        system_prompt=system_prompt,
    )
    vapi_assistant_id = vapi_result.get("id")

    # Assign mock phone number
    phone_result = assign_phone_number(vapi_assistant_id)
    assigned_phone = phone_result.get("phone_number")

    agent_id = str(uuid.uuid4())

    try:
        sb.table("agents").insert({
            "id": agent_id,
            "customer_id": customer_id,
            "agent_name": agent_name,
            "industry": industry or None,
            "business_name": business_name,
            "business_phone": business_phone,
            "business_address": business_address,
            "business_hours": business_hours or None,
            "services": services or None,
            "greeting_message": greeting_message,
            "system_prompt": system_prompt,
            "calendar_url": calendar_url,
            "phone_number": assigned_phone,
            "vapi_assistant_id": vapi_assistant_id,
            "status": "active",
        }).execute()
    except Exception as e:
        return jsonify({"error": f"Failed to create agent: {e}"}), 500

    return jsonify({
        "message": "Agent created successfully.",
        "agent": {
            "id": agent_id,
            "agent_name": agent_name,
            "business_name": business_name,
            "industry": industry,
            "phone_number": assigned_phone,
            "vapi_assistant_id": vapi_assistant_id,
            "status": "active",
        },
    }), 201


@platform_bp.route("/api/platform/agents", methods=["GET"])
@auth_required
def list_agents():
    """List all agents for the authenticated customer."""
    sb = _get_supabase()
    res = sb.table("agents").select("*").eq("customer_id", g.customer_id).order("created_at", desc=True).execute()
    return jsonify({"agents": res.data or []})


@platform_bp.route("/api/platform/agents/<agent_id>", methods=["GET"])
@auth_required
def get_agent(agent_id):
    """Get a single agent by ID (must belong to the authenticated customer)."""
    sb = _get_supabase()
    res = sb.table("agents").select("*").eq("id", agent_id).eq("customer_id", g.customer_id).execute()
    agents = res.data or []

    if not agents:
        return jsonify({"error": "Agent not found."}), 404

    return jsonify({"agent": agents[0]})


@platform_bp.route("/api/platform/agents/<agent_id>", methods=["PUT"])
@auth_required
def update_agent(agent_id):
    """Update agent settings."""
    data = request.get_json(silent=True) or {}
    sb = _get_supabase()

    # Verify ownership
    existing = sb.table("agents").select("id, customer_id").eq("id", agent_id).eq("customer_id", g.customer_id).execute()
    if not existing.data:
        return jsonify({"error": "Agent not found."}), 404

    # Allowed fields to update
    allowed = [
        "agent_name", "industry", "business_name", "business_phone",
        "business_address", "business_hours", "services", "greeting_message",
        "calendar_url", "status",
    ]
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({"error": "No valid fields to update."}), 400

    # Regenerate system prompt if business info changed
    prompt_fields = {"business_name", "industry", "services", "business_hours", "calendar_url",
                     "business_phone", "business_address", "greeting_message", "agent_name"}
    if prompt_fields & set(updates.keys()):
        # Fetch current agent to merge
        current = sb.table("agents").select("*").eq("id", agent_id).execute().data[0]
        merged = {**current, **updates}

        updates["system_prompt"] = generate_system_prompt(
            business_name=merged.get("business_name", ""),
            industry=merged.get("industry", ""),
            services=merged.get("services") or [],
            business_hours=merged.get("business_hours") or {},
            calendar_url=merged.get("calendar_url"),
            business_phone=merged.get("business_phone"),
            business_address=merged.get("business_address"),
            greeting_message=merged.get("greeting_message"),
            agent_name=merged.get("agent_name", "AI Receptionist"),
        )

    try:
        sb.table("agents").update(updates).eq("id", agent_id).execute()
    except Exception as e:
        return jsonify({"error": f"Failed to update agent: {e}"}), 500

    # Fetch updated agent
    updated = sb.table("agents").select("*").eq("id", agent_id).execute()
    return jsonify({"message": "Agent updated.", "agent": updated.data[0] if updated.data else {}})


# ---------------------------------------------------------------------------
# Call logs
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/agents/<agent_id>/calls", methods=["GET"])
@auth_required
def agent_calls(agent_id):
    """Get call history for an agent."""
    sb = _get_supabase()

    # Verify ownership
    agent = sb.table("agents").select("id").eq("id", agent_id).eq("customer_id", g.customer_id).execute()
    if not agent.data:
        return jsonify({"error": "Agent not found."}), 404

    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))

    res = (
        sb.table("call_logs")
        .select("*")
        .eq("agent_id", agent_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return jsonify({"calls": res.data or [], "limit": limit, "offset": offset})


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/agents/<agent_id>/appointments", methods=["GET"])
@auth_required
def agent_appointments(agent_id):
    """Get appointments for an agent."""
    sb = _get_supabase()

    # Verify ownership
    agent = sb.table("agents").select("id").eq("id", agent_id).eq("customer_id", g.customer_id).execute()
    if not agent.data:
        return jsonify({"error": "Agent not found."}), 404

    status_filter = request.args.get("status")  # optional: scheduled, completed, cancelled, no_show
    limit = min(int(request.args.get("limit", 50)), 200)

    query = sb.table("appointments").select("*").eq("agent_id", agent_id).order("appointment_date", desc=True).limit(limit)
    if status_filter:
        query = query.eq("status", status_filter)

    res = query.execute()
    return jsonify({"appointments": res.data or []})


# ---------------------------------------------------------------------------
# Agent stats
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/agents/<agent_id>/stats", methods=["GET"])
@auth_required
def agent_stats(agent_id):
    """Get aggregated stats for an agent."""
    sb = _get_supabase()

    # Verify ownership
    agent = sb.table("agents").select("id, agent_name, business_name, status, created_at").eq("id", agent_id).eq("customer_id", g.customer_id).execute()
    if not agent.data:
        return jsonify({"error": "Agent not found."}), 404

    # All calls for this agent
    calls_res = sb.table("call_logs").select("id, call_duration_seconds, call_outcome, created_at").eq("agent_id", agent_id).execute()
    calls = calls_res.data or []

    total_calls = len(calls)
    total_duration = sum(c.get("call_duration_seconds", 0) or 0 for c in calls)
    avg_duration = round(total_duration / total_calls) if total_calls > 0 else 0

    # Outcome breakdown
    outcomes = {}
    for c in calls:
        outcome = c.get("call_outcome", "unknown") or "unknown"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

    # Appointments count
    appts_res = sb.table("appointments").select("id, status").eq("agent_id", agent_id).execute()
    appts = appts_res.data or []
    appts_by_status = {}
    for a in appts:
        s = a.get("status", "unknown")
        appts_by_status[s] = appts_by_status.get(s, 0) + 1

    # Calls in last 7 days
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_calls = [c for c in calls if c.get("created_at", "") >= week_ago]

    return jsonify({
        "agent": agent.data[0],
        "stats": {
            "total_calls": total_calls,
            "total_call_duration_seconds": total_duration,
            "avg_call_duration_seconds": avg_duration,
            "calls_last_7_days": len(recent_calls),
            "outcome_breakdown": outcomes,
            "total_appointments": len(appts),
            "appointments_by_status": appts_by_status,
        },
    })


# ---------------------------------------------------------------------------
# Utility: supported industries
# ---------------------------------------------------------------------------

@platform_bp.route("/api/platform/industries", methods=["GET"])
def list_industries():
    """Return list of supported industries."""
    return jsonify({"industries": get_supported_industries()})
