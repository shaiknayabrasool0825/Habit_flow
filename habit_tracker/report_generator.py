import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from models import db, User, Habit, HabitLog, Suggestion
from flask import current_app

REPORT_DIR = 'reports'

def get_performance_color(rate):
    if rate >= 80:
        return colors.green
    elif rate >= 50:
        return colors.orange
    else:
        return colors.red

def calculate_stats(user_id, start_date, end_date):
    """Calculates statistics for a given user and date range."""
    habits = Habit.query.filter_by(user_id=user_id).all()
    habit_ids = [h.id for h in habits]
    
    logs = HabitLog.query.filter(
        HabitLog.habit_id.in_(habit_ids),
        HabitLog.date >= start_date,
        HabitLog.date <= end_date
    ).all()
    
    total_expected = len(habits) * ((end_date - start_date).days + 1)
    if total_expected == 0:
        return None
        
    completions = [l for l in logs if l.status]
    completion_rate = (len(completions) / total_expected) * 100 if total_expected > 0 else 0
    total_xp = sum(l.xp_earned for l in logs if l.xp_earned)
    
    # Best/Worst Day
    day_counts = {}
    current = start_date
    while current <= end_date:
        day_counts[current] = 0
        current += timedelta(days=1)
        
    for l in completions:
        day_counts[l.date] = day_counts.get(l.date, 0) + 1
        
    best_day_date = max(day_counts, key=day_counts.get) if day_counts else None
    worst_day_date = min(day_counts, key=day_counts.get) if day_counts else None
    
    # Strongest/Weakest Habit
    habit_performance = {}
    for h in habits:
        h_logs = [l for l in logs if l.habit_id == h.id]
        successes = len([l for l in h_logs if l.status])
        total = (end_date - start_date).days + 1
        habit_performance[h.name] = (successes / total) if total > 0 else 0
        
    strongest = max(habit_performance, key=habit_performance.get) if habit_performance else "N/A"
    weakest = min(habit_performance, key=habit_performance.get) if habit_performance else "N/A"
    
    user = User.query.get(user_id)
    
    # AI Suggestion
    suggestion = Suggestion.query.filter_by(user_id=user_id).order_by(Suggestion.created_at.desc()).first()
    suggestion_msg = suggestion.message if suggestion else "Keep up the great work! Consistency is key."

    return {
        'user_name': user.username,
        'completion_rate': round(completion_rate, 1),
        'total_xp': total_xp,
        'strongest': strongest,
        'weakest': weakest,
        'best_day': best_day_date.strftime('%A, %b %d') if best_day_date else "N/A",
        'worst_day': worst_day_date.strftime('%A, %b %d') if worst_day_date else "N/A",
        'streak': user.current_streak,
        'suggestion': suggestion_msg
    }

def generate_pdf(filename, title, period_label, stats):
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    filepath = os.path.join(REPORT_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#4F46E5"),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    elements = []
    
    # Header
    elements.append(Paragraph("HabitFlow Progress Report", title_style))
    elements.append(Paragraph(f"{period_label} Report for {stats['user_name']}", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Performance Circle (Simulated with Table color)
    perf_color = get_performance_color(stats['completion_rate'])
    
    summary_data = [
        [Paragraph(f"<b>Completion Rate</b>", styles['Normal']), 
         Paragraph(f"<font color='{perf_color}'><b>{stats['completion_rate']}%</b></font>", styles['Normal'])],
        ["Total XP Earned", f"{stats['total_xp']} XP"],
        ["Current Streak", f"{stats['streak']} Days"],
        ["Strongest Habit", stats['strongest']],
        ["Weakest Habit", stats['weakest']],
        ["Best Day", stats['best_day']],
        ["Worst Day", stats['worst_day']],
    ]
    
    t = Table(summary_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 30))
    
    # Coach Section
    elements.append(Paragraph("<b>🤖 AI Coach Insights</b>", styles['Heading2']))
    elements.append(Paragraph(stats['suggestion'], styles['Normal']))
    
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Italic']))
    
    doc.build(elements)
    return filepath

def generate_daily_report(user_id):
    today = datetime.utcnow().date()
    stats = calculate_stats(user_id, today, today)
    if not stats: return None
    return generate_pdf(f"user_{user_id}_daily.pdf", "Daily Report", f"Daily ({today})", stats)

def generate_weekly_report(user_id):
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=6)
    stats = calculate_stats(user_id, start_of_week, today)
    if not stats: return None
    return generate_pdf(f"user_{user_id}_weekly.pdf", "Weekly Report", f"Weekly ({start_of_week} to {today})", stats)

def generate_monthly_report(user_id):
    today = datetime.utcnow().date()
    start_of_month = today - timedelta(days=29)
    stats = calculate_stats(user_id, start_of_month, today)
    if not stats: return None
    return generate_pdf(f"user_{user_id}_monthly.pdf", "Monthly Report", f"Monthly (Last 30 Days)", stats)
