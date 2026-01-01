import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    EMAIL_FROM, EMAIL_FROM_NAME, FRONTEND_URL
)


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using SMTP."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Email Service] SMTP credentials not configured, skipping email")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())

        print(f"[Email Service] Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        print(f"[Email Service] Failed to send email to {to_email}: {str(e)}")
        return False


def send_task_shared_notification(
    recipient_email: str,
    sharer_email: str,
    task_title: str,
    task_id: int,
    permission: str
) -> bool:
    """Send notification when someone shares a task with you."""
    task_url = f"{FRONTEND_URL}/task/{task_id}"
    permission_text = "view" if permission == "view" else "view and edit"

    subject = f"Task shared with you: {task_title}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 30px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f8fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
                border-top: none;
                border-radius: 0 0 12px 12px;
            }}
            .task-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                margin: 20px 0;
            }}
            .task-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
                margin: 0 0 10px 0;
            }}
            .permission-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .permission-view {{
                background: #e0e7ff;
                color: #4338ca;
            }}
            .permission-edit {{
                background: #d1fae5;
                color: #065f46;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 15px;
            }}
            .footer {{
                text-align: center;
                color: #64748b;
                font-size: 12px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin: 0; font-size: 24px;">New Task Shared</h1>
        </div>
        <div class="content">
            <p>Hi there,</p>
            <p><strong>{sharer_email}</strong> has shared a task with you.</p>

            <div class="task-card">
                <p class="task-title">{task_title}</p>
                <span class="permission-badge permission-{permission}">
                    Can {permission_text}
                </span>
            </div>

            <p>Click below to view this task in your workspace:</p>
            <a href="{task_url}" class="btn">View Task</a>

            <div class="footer">
                <p>This email was sent by Task Manager</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(recipient_email, subject, html_content)


def send_deadline_reminder(
    recipient_email: str,
    task_title: str,
    task_id: int,
    deadline: datetime
) -> bool:
    """Send reminder email when task deadline is approaching (1 hour)."""
    task_url = f"{FRONTEND_URL}/task/{task_id}"
    deadline_str = deadline.strftime("%B %d, %Y at %I:%M %p")

    subject = f"Reminder: Task due in 1 hour - {task_title}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                color: white;
                padding: 30px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f8fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
                border-top: none;
                border-radius: 0 0 12px 12px;
            }}
            .task-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #ef4444;
                margin: 20px 0;
            }}
            .task-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
                margin: 0 0 10px 0;
            }}
            .deadline {{
                color: #ef4444;
                font-weight: 600;
                font-size: 14px;
            }}
            .time-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 15px;
            }}
            .footer {{
                text-align: center;
                color: #64748b;
                font-size: 12px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="time-icon">⏰</div>
            <h1 style="margin: 0; font-size: 24px;">Deadline Approaching!</h1>
        </div>
        <div class="content">
            <p>Hi there,</p>
            <p>Your task is due in <strong>1 hour</strong>. Don't forget to complete it!</p>

            <div class="task-card">
                <p class="task-title">{task_title}</p>
                <p class="deadline">Due: {deadline_str}</p>
            </div>

            <p>Click below to open your task workspace:</p>
            <a href="{task_url}" class="btn">Open Task</a>

            <div class="footer">
                <p>This email was sent by Task Manager</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(recipient_email, subject, html_content)
