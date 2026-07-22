"""Email notifications for high-scoring job matches."""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

logger = logging.getLogger(__name__)


def _build_subject(match: dict[str, Any]) -> str:
    return f"[{match['score']}/10] {match['company']} - {match['title']}"


def _build_body(match: dict[str, Any], profile_name: str) -> str:
    reasons = match.get("match_reasons", [])
    reasons_html = "".join(f"<li>{reason}</li>" for reason in reasons)
    reasons_text = "\n".join(f"  • {reason}" for reason in reasons)

    html = f"""
    <html>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.5;">
        <h2>{match['company']} — {match['title']}</h2>
        <p><strong>Match score:</strong> {match['score']}/10</p>
        <p><strong>Location:</strong> {match['location']}</p>
        <p><strong>Role types:</strong> {', '.join(match.get('role_types', []))}</p>
        <h3>Why this fits {profile_name}</h3>
        <ul>{reasons_html}</ul>
        <h3>Key requirements</h3>
        <p>{match.get('requirements_snippet', '')}</p>
        <p><a href="{match['url']}">View job posting →</a></p>
        <hr>
        <p style="color:#666;font-size:12px;">MBA Internship Scraper · Summer 2027 · UNC Kenan-Flagler</p>
      </body>
    </html>
    """

    text = f"""{match['company']} — {match['title']}
Match score: {match['score']}/10
Location: {match['location']}
Role types: {', '.join(match.get('role_types', []))}

Why this fits {profile_name}:
{reasons_text}

Key requirements:
{match.get('requirements_snippet', '')}

Apply: {match['url']}
"""
    return html, text


class EmailNotifier:
    def __init__(
        self,
        *,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        recipient: str,
        profile_name: str,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.recipient = recipient
        self.profile_name = profile_name

    @classmethod
    def from_env(cls, *, profile_name: str, recipient: str | None = None) -> "EmailNotifier | None":
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        to_address = recipient or os.getenv("ALERT_EMAIL", "")

        if not smtp_user or not smtp_password or not to_address:
            return None

        return cls(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            recipient=to_address,
            profile_name=profile_name,
        )

    def send_match_alert(self, match: dict[str, Any]) -> None:
        html, text = _build_body(match, self.profile_name)
        message = MIMEMultipart("alternative")
        message["Subject"] = _build_subject(match)
        message["From"] = self.smtp_user
        message["To"] = self.recipient
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, [self.recipient], message.as_string())

        logger.info("Sent alert for %s — %s", match["company"], match["title"])

    def send_digest(self, matches: list[dict[str, Any]]) -> None:
        for match in matches:
            self.send_match_alert(match)
