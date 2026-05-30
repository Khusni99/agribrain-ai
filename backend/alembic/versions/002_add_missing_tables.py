"""Add missing tables (disease_detections, whatsapp_sessions, etc.)

Revision ID: 002
Revises: 001
Create Date: 2026-05-31
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "disease_detections",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("cloudinary_url", sa.String(), nullable=True),
        sa.Column("original_filename", sa.String(), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("disease_name", sa.String(), index=True, nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("severity", sa.Float(), nullable=True),
        sa.Column("bounding_boxes", sa.JSON(), default=list),
        sa.Column("recommendations", sa.JSON(), default=list),
        sa.Column("prevention", sa.JSON(), default=list),
        sa.Column("economic_risk", sa.JSON(), default=dict),
        sa.Column("detection_provider", sa.String(), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "whatsapp_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phone_number", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("is_verified", sa.Boolean(), default=False),
        sa.Column("verification_code", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), default="mock"),
        sa.Column("provider_session_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("notification_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), default="sent"),
        sa.Column("provider_message_id", sa.String(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "reminder_preferences",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("whatsapp_enabled", sa.Boolean(), default=True),
        sa.Column("fertilizer_reminder", sa.Boolean(), default=True),
        sa.Column("spray_reminder", sa.Boolean(), default=True),
        sa.Column("harvest_reminder", sa.Boolean(), default=True),
        sa.Column("disease_risk_alert", sa.Boolean(), default=True),
        sa.Column("weather_alert", sa.Boolean(), default=False),
        sa.Column("reminder_time_start", sa.String(), default="06:00"),
        sa.Column("reminder_time_end", sa.String(), default="18:00"),
        sa.Column("advance_days_fertilizer", sa.Integer(), default=1),
        sa.Column("advance_days_spray", sa.Integer(), default=1),
        sa.Column("advance_days_harvest", sa.Integer(), default=3),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("reminder_preferences")
    op.drop_table("notification_logs")
    op.drop_table("whatsapp_sessions")
    op.drop_table("disease_detections")
