from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Friendship

social_bp = Blueprint('social', __name__)

@social_bp.route('/')
@login_required
def friends_dashboard():
    # friends where user sent request, and friend accepted
    friends_sent = Friendship.query.filter_by(user_id=current_user.id, status='accepted').all()
    # friends where user received request, and user accepted
    friends_received = Friendship.query.filter_by(friend_id=current_user.id, status='accepted').all()
    
    # Get all active friends
    friends = [f.friend for f in friends_sent] + [f.user for f in friends_received]
    
    # Pending requests received by me
    pending_requests = Friendship.query.filter_by(friend_id=current_user.id, status='pending').all()
    
    return render_template('friends.html', friends=friends, pending_requests=pending_requests, user=current_user)

@social_bp.route('/add', methods=['POST'])
@login_required
def add_friend():
    friend_username = request.form.get('username')
    friend = User.query.filter_by(username=friend_username).first()
    
    if not friend:
        flash('User not found!', 'error')
    elif friend.id == current_user.id:
        flash('You cannot add yourself!', 'error')
    else:
        # Check if friendship already exists
        existing = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend.id)) |
            ((Friendship.user_id == friend.id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if existing:
            flash('You are already friends or have a pending request.', 'warning')
        else:
            new_friendship = Friendship(user_id=current_user.id, friend_id=friend.id)
            db.session.add(new_friendship)
            db.session.commit()
            flash(f'Friend request sent to {friend.username}', 'success')
            
    return redirect(url_for('social.friends_dashboard'))

@social_bp.route('/accept/<int:request_id>')
@login_required
def accept_friend(request_id):
    friendship = Friendship.query.get_or_404(request_id)
    if friendship.friend_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('social.friends_dashboard'))
        
    friendship.status = 'accepted'
    db.session.commit()
    flash(f'You are now friends with {friendship.user.username}', 'success')
    return redirect(url_for('social.friends_dashboard'))
