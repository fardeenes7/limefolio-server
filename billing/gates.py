from billing.models import Plan, Subscription

def get_user_plan(user) -> Plan:
    """Returns the user's active plan or the Free plan if no active subscription."""
    try:
        sub = user.subscription
        if sub.is_access_allowed:
            return sub.plan
    except Exception:
        pass
    return Plan.objects.get(tier="free")

def check_limit(user, limit_field: str, current_count: int) -> dict:
    """
    Returns {"allowed": bool, "limit": int, "current": int, "upgrade_required": bool}
    Limit of -1 = unlimited.
    """
    plan = get_user_plan(user)
    limit = getattr(plan, limit_field)
    if limit == -1:
        return {"allowed": True, "limit": -1, "current": current_count, "upgrade_required": False}
    allowed = current_count < limit
    return {"allowed": allowed, "limit": limit, "current": current_count, "upgrade_required": not allowed}
