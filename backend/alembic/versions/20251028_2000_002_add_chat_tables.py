"""add chat tables for conversations and messages

Revision ID: 002_add_chat_tables
Revises: 20251028_1300_001_initial_schema
Create Date: 2025-10-28 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_chat_tables'
down_revision = '20251028_1300_001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversation_status enum
    conversation_status_enum = postgresql.ENUM(
        'active', 'archived', 'deleted',
        name='conversationstatus',
        create_type=True
    )
    conversation_status_enum.create(op.get_bind())

    # Create message_role enum
    message_role_enum = postgresql.ENUM(
        'user', 'assistant', 'system',
        name='messagerole',
        create_type=True
    )
    message_role_enum.create(op.get_bind())

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'archived', 'deleted', name='conversationstatus'), nullable=True),
        sa.Column('specialist_agent', sa.String(length=100), nullable=True),
        sa.Column('document_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversations_status'), 'conversations', ['status'], unique=False)
    op.create_index(op.f('ix_conversations_tenant_id'), 'conversations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_conversations_project_id'), 'conversations', ['project_id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('rag_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_feedback', sa.String(length=20), nullable=True),
        sa.Column('feedback_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_messages_tenant_id'), 'messages', ['tenant_id'], unique=False)


def downgrade() -> None:
    # Drop messages table
    op.drop_index(op.f('ix_messages_tenant_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_project_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_tenant_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_status'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_created_at'), table_name='conversations')
    op.drop_table('conversations')

    # Drop enums
    message_role_enum = postgresql.ENUM('user', 'assistant', 'system', name='messagerole')
    message_role_enum.drop(op.get_bind())

    conversation_status_enum = postgresql.ENUM('active', 'archived', 'deleted', name='conversationstatus')
    conversation_status_enum.drop(op.get_bind())
