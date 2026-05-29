"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2026-05-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("username", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("role", sa.Enum("farmer", "agronomist", "admin", name="userrole"), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("language", sa.String(), default="id"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_table(
        "crops",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("variety", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("growing_days", sa.Integer(), nullable=True),
        sa.Column("optimal_temp_min", sa.Float(), nullable=True),
        sa.Column("optimal_temp_max", sa.Float(), nullable=True),
        sa.Column("optimal_ph_min", sa.Float(), nullable=True),
        sa.Column("optimal_ph_max", sa.Float(), nullable=True),
        sa.Column("water_requirement_mm", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("altitude", sa.Float(), nullable=True),
        sa.Column("area_hectare", sa.Float(), nullable=True),
        sa.Column("soil_type", sa.String(), nullable=True),
        sa.Column("soil_ph", sa.Float(), nullable=True),
        sa.Column("soil_ec", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_table(
        "fields",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("area_hectare", sa.Float(), nullable=True),
        sa.Column("crop_type", sa.String(), nullable=True),
        sa.Column("planting_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "crop_cycles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_id", sa.Integer(), sa.ForeignKey("crops.id"), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("expected_harvest_date", sa.DateTime(), nullable=True),
        sa.Column("actual_harvest_date", sa.DateTime(), nullable=True),
        sa.Column("plant_count", sa.Integer(), nullable=True),
        sa.Column("spacing_meters", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "disease_records",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_id", sa.Integer(), sa.ForeignKey("crops.id"), nullable=False),
        sa.Column("detected_by", sa.String(), nullable=True),
        sa.Column("disease_name", sa.String(), nullable=True),
        sa.Column("severity_percentage", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("symptoms", sa.Text(), nullable=True),
        sa.Column("causes", sa.Text(), nullable=True),
        sa.Column("treatment", sa.Text(), nullable=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("detection_method", sa.String(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), default=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "fertilizer_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_cycle_id", sa.Integer(), sa.ForeignKey("crop_cycles.id"), nullable=True),
        sa.Column("recommendation_type", sa.String(), nullable=True),
        sa.Column("fertilizer_name", sa.String(), nullable=True),
        sa.Column("fertilizer_type", sa.String(), nullable=True),
        sa.Column("dosage_per_plant", sa.Float(), nullable=True),
        sa.Column("dosage_per_hectare", sa.Float(), nullable=True),
        sa.Column("application_method", sa.String(), nullable=True),
        sa.Column("application_interval_days", sa.Integer(), nullable=True),
        sa.Column("growth_stage", sa.String(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("cost_estimate", sa.Float(), nullable=True),
        sa.Column("is_organic", sa.Boolean(), default=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "spray_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_cycle_id", sa.Integer(), sa.ForeignKey("crop_cycles.id"), nullable=True),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("active_ingredient", sa.String(), nullable=True),
        sa.Column("target_pest", sa.String(), nullable=True),
        sa.Column("dosage", sa.Float(), nullable=True),
        sa.Column("dilution_rate", sa.Float(), nullable=True),
        sa.Column("application_method", sa.String(), nullable=True),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("next_spray_date", sa.DateTime(), nullable=True),
        sa.Column("weather_suitable", sa.Boolean(), default=True),
        sa.Column("pre_harvest_interval", sa.Integer(), nullable=True),
        sa.Column("resistance_group", sa.String(), nullable=True),
        sa.Column("compatibility_notes", sa.Text(), nullable=True),
        sa.Column("is_applied", sa.Boolean(), default=False),
        sa.Column("applied_date", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "weather_data",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("rainfall_mm", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("solar_radiation", sa.Float(), nullable=True),
        sa.Column("pressure", sa.Float(), nullable=True),
        sa.Column("condition", sa.String(), nullable=True),
        sa.Column("forecast", sa.JSON(), nullable=True),
        sa.Column("disease_risk_score", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "production_costs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_cycle_id", sa.Integer(), sa.ForeignKey("crop_cycles.id"), nullable=True),
        sa.Column("cost_category", sa.String(), nullable=False),
        sa.Column("item_name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column("total_cost", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "harvest_records",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_cycle_id", sa.Integer(), sa.ForeignKey("crop_cycles.id"), nullable=True),
        sa.Column("harvest_date", sa.DateTime(), nullable=False),
        sa.Column("quantity_kg", sa.Float(), nullable=True),
        sa.Column("marketable_kg", sa.Float(), nullable=True),
        sa.Column("reject_kg", sa.Float(), nullable=True),
        sa.Column("yield_per_hectare", sa.Float(), nullable=True),
        sa.Column("average_price", sa.Float(), nullable=True),
        sa.Column("total_revenue", sa.Float(), nullable=True),
        sa.Column("quality_grade", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("quantity_kg", sa.Float(), nullable=True),
        sa.Column("price_per_kg", sa.Float(), nullable=True),
        sa.Column("quality_grade", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("status", sa.Enum("available", "sold", "reserved", name="productstatus"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "market_prices",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("commodity", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("min_price", sa.Float(), nullable=True),
        sa.Column("max_price", sa.Float(), nullable=True),
        sa.Column("avg_price", sa.Float(), nullable=True),
        sa.Column("trend", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("market_prices")
    op.drop_table("products")
    op.drop_table("harvest_records")
    op.drop_table("production_costs")
    op.drop_table("weather_data")
    op.drop_table("spray_schedules")
    op.drop_table("fertilizer_recommendations")
    op.drop_table("disease_records")
    op.drop_table("crop_cycles")
    op.drop_table("fields")
    op.drop_table("farms")
    op.drop_table("crops")
    op.drop_table("users")
