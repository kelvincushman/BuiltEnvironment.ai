"""add findings table

Revision ID: 20251029_0000_003
Revises: 20251028_2000_002
Create Date: 2025-10-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251029_0000_003'
down_revision = '20251028_2000_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    findingtype_enum = postgresql.ENUM(
        'compliance_issue', 'recommendation', 'observation', 'missing_info',
        name='findingtype',
        create_type=False
    )
    findingtype_enum.create(op.get_bind(), checkfirst=True)

    findingseverity_enum = postgresql.ENUM(
        'critical', 'major', 'minor', 'info',
        name='findingseverity',
        create_type=False
    )
    findingseverity_enum.create(op.get_bind(), checkfirst=True)

    findingstatus_enum = postgresql.ENUM(
        'open', 'in_review', 'resolved', 'dismissed',
        name='findingstatus',
        create_type=False
    )
    findingstatus_enum.create(op.get_bind(), checkfirst=True)

    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Finding classification
        sa.Column('finding_type', sa.Enum('compliance_issue', 'recommendation', 'observation', 'missing_info', name='findingtype'), nullable=False, index=True),
        sa.Column('severity', sa.Enum('critical', 'major', 'minor', 'info', name='findingseverity'), nullable=False, index=True),
        sa.Column('status', sa.Enum('open', 'in_review', 'resolved', 'dismissed', name='findingstatus'), nullable=False, server_default='open', index=True),

        # Regulation/standard reference
        sa.Column('category', sa.String(100), nullable=False, index=True),
        sa.Column('regulation_reference', sa.String(255)),
        sa.Column('standard_reference', sa.String(255)),

        # Finding details
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('recommendation', sa.Text),

        # Document location
        sa.Column('page_number', sa.Integer),
        sa.Column('section', sa.String(255)),
        sa.Column('line_number', sa.Integer),

        # AI metadata
        sa.Column('specialist_agent', sa.String(100), nullable=False, index=True),
        sa.Column('confidence_score', sa.Float),
        sa.Column('ai_reasoning', sa.Text),

        # Source context (RAG chunks)
        sa.Column('source_chunks', postgresql.JSONB, server_default='[]'),

        # Additional metadata
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),

        # Foreign keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )

    # Create indexes for common queries
    op.create_index('ix_findings_tenant_project', 'findings', ['tenant_id', 'project_id'])
    op.create_index('ix_findings_tenant_document', 'findings', ['tenant_id', 'document_id'])
    op.create_index('ix_findings_severity_status', 'findings', ['severity', 'status'])
    op.create_index('ix_findings_created_at', 'findings', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_findings_created_at', 'findings')
    op.drop_index('ix_findings_severity_status', 'findings')
    op.drop_index('ix_findings_tenant_document', 'findings')
    op.drop_index('ix_findings_tenant_project', 'findings')

    # Drop table
    op.drop_table('findings')

    # Drop enums
    sa.Enum(name='findingstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='findingseverity').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='findingtype').drop(op.get_bind(), checkfirst=True)
