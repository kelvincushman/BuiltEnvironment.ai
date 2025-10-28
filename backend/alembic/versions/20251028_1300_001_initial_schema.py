"""Initial schema with all core models

Revision ID: 001
Revises:
Create Date: 2025-10-28 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create all initial tables for BuiltEnvironment.ai:
    - tenants: Multi-tenant organizations
    - users: User accounts with tenant association
    - subscriptions: Stripe subscription management
    - projects: Building projects
    - documents: Uploaded documents with AI analysis
    - audit_events: Comprehensive activity tracking
    """

    # Create enums
    subscription_status_enum = postgresql.ENUM(
        'trialing', 'active', 'past_due', 'canceled', 'unpaid',
        'incomplete', 'incomplete_expired',
        name='subscriptionstatus'
    )
    subscription_status_enum.create(op.get_bind())

    subscription_tier_enum = postgresql.ENUM(
        'starter', 'professional', 'enterprise',
        name='subscriptiontier'
    )
    subscription_tier_enum.create(op.get_bind())

    project_status_enum = postgresql.ENUM(
        'draft', 'in_review', 'ai_analysis_complete', 'engineer_review',
        'validated', 'submitted', 'approved', 'archived',
        name='projectstatus'
    )
    project_status_enum.create(op.get_bind())

    document_type_enum = postgresql.ENUM(
        'architectural', 'structural', 'mechanical', 'electrical',
        'fire_safety', 'accessibility', 'building_control',
        'technical_spec', 'report', 'other',
        name='documenttype'
    )
    document_type_enum.create(op.get_bind())

    document_status_enum = postgresql.ENUM(
        'uploaded', 'processing', 'indexed', 'ai_analysis_complete',
        'ready_for_review', 'engineer_review', 'validated', 'error',
        name='documentstatus'
    )
    document_status_enum.create(op.get_bind())

    event_type_enum = postgresql.ENUM(
        'user.auth', 'user.action', 'document.upload', 'document.process',
        'ai.analysis', 'ai.agent', 'compliance.check', 'engineer.review',
        'subscription', 'system',
        name='eventtype'
    )
    event_type_enum.create(op.get_bind())

    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('postcode', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), server_default='United Kingdom'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_trial', sa.Boolean(), server_default='true'),
        sa.Column('max_users', sa.Integer(), server_default='3'),
        sa.Column('max_projects', sa.Integer(), server_default='5'),
        sa.Column('max_storage_gb', sa.Integer(), server_default='10'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('job_title', sa.String(100), nullable=True),
        sa.Column('is_engineer', sa.Boolean(), server_default='false'),
        sa.Column('engineer_registration_number', sa.String(100), nullable=True),
        sa.Column('engineer_qualification', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True),
        sa.Column('stripe_price_id', sa.String(255), nullable=True),
        sa.Column('tier', subscription_tier_enum, nullable=False, server_default='starter'),
        sa.Column('status', subscription_status_enum, nullable=False, server_default='trialing'),
        sa.Column('billing_cycle', sa.String(20), server_default='monthly'),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('currency', sa.String(3), server_default='GBP'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_data', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_subscriptions_tenant_id', 'subscriptions', ['tenant_id'], unique=True)
    op.create_index('ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'], unique=True)
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('postcode', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), server_default='United Kingdom'),
        sa.Column('project_type', sa.String(100), nullable=True),
        sa.Column('building_use', sa.String(100), nullable=True),
        sa.Column('status', project_status_enum, server_default='draft'),
        sa.Column('compliance_summary', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'),
        sa.Column('engineer_validated', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_projects_tenant_id', 'projects', ['tenant_id'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_extension', sa.String(10), nullable=False),
        sa.Column('document_type', document_type_enum, server_default='other'),
        sa.Column('status', document_status_enum, server_default='uploaded'),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('ai_analysis', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'),
        sa.Column('compliance_findings', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'),
        sa.Column('vector_indexed', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('engineer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_documents_tenant_id', 'documents', ['tenant_id'])
    op.create_index('ix_documents_project_id', 'documents', ['project_id'])

    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), server_default='success'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_type', sa.String(20), nullable=False),
        sa.Column('actor_id', sa.String(255), nullable=True),
        sa.Column('ai_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_events_tenant_id', 'audit_events', ['tenant_id'])
    op.create_index('ix_audit_events_user_id', 'audit_events', ['user_id'])
    op.create_index('ix_audit_events_event_type', 'audit_events', ['event_type'])
    op.create_index('ix_audit_events_timestamp', 'audit_events', ['timestamp'])
    op.create_index('ix_audit_events_resource_id', 'audit_events', ['resource_id'])


def downgrade() -> None:
    """
    Drop all tables and enums in reverse order.
    """
    # Drop tables (in reverse order of creation due to foreign keys)
    op.drop_table('audit_events')
    op.drop_table('documents')
    op.drop_table('projects')
    op.drop_table('subscriptions')
    op.drop_table('users')
    op.drop_table('tenants')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS eventtype')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS projectstatus')
    op.execute('DROP TYPE IF EXISTS subscriptiontier')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
