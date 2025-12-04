from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    from app.decorators import get_dashboard_for_role
    
    # Get the dashboard route for the user's role
    dashboard_route = get_dashboard_for_role(current_user)
    
    # If no valid dashboard is found, show debug info
    if dashboard_route == 'main.index':
        return f"Unknown Role: '{current_user.role.name}'. User: {current_user.email}"
    
    return redirect(url_for(dashboard_route))
