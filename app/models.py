from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
import jwt
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    department = db.Column(db.String(64))
    role = db.Column(db.String(20), nullable=False, default='user')  # user, agent, admin
    is_active = db.Column(db.Boolean, default=True)
    organization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submitted_tickets = db.relationship('Ticket', backref='submitter', lazy='dynamic',
                                      foreign_keys='Ticket.submitter_id')
    requested_tickets = db.relationship('Ticket', backref='requester', lazy='dynamic',
                                      foreign_keys='Ticket.requester_id')
    assigned_tickets = db.relationship('Ticket', backref='agent', lazy='dynamic',
                                     foreign_keys='Ticket.assigned_agent_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    messages = db.relationship('Message', backref='sender', lazy=True)
    articles = db.relationship('Article', backref='author', lazy=True)
    assigned_assets = db.relationship('Asset', backref='assigned_to', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user')
    
    # Add two-factor authentication fields
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_agent(self):
        return self.role == 'agent'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=3600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='ticket_category', lazy='dynamic')
    articles = db.relationship('Article', backref='category', lazy=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('ticket_statuses.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('ticket_priorities.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('ticket_channels.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    first_response_at = db.Column(db.DateTime)
    resolution_time = db.Column(db.Integer)  # in minutes
    is_merged = db.Column(db.Boolean, default=False)
    parent_ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    
    # Foreign keys
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic')
    attachments = db.relationship('Attachment', backref='ticket', lazy='dynamic')
    messages = db.relationship('Message', backref='ticket', lazy=True)
    custom_fields = db.relationship('TicketCustomField', backref='ticket', lazy=True)
    sla_violations = db.relationship('SLAViolation', backref='ticket', lazy=True)
    merged_tickets = db.relationship('Ticket', backref=db.backref('parent_ticket', remote_side=[id]))
    audit_logs = db.relationship('AuditLog',
                               primaryjoin="and_(Ticket.id==foreign(AuditLog.entity_id), "
                                         "AuditLog.entity_type=='ticket')",
                               backref=db.backref('ticket', lazy='joined'),
                               lazy='dynamic',
                               order_by='desc(AuditLog.timestamp)')
    
    def get_status(self):
        return self.status_obj.name if self.status_obj else 'Unknown'
    
    def get_priority(self):
        return self.priority_level.name if self.priority_level else 'Medium'
    
    def is_overdue(self):
        if self.due_date and datetime.utcnow() > self.due_date:
            return True
        return False
    
    def merge_with(self, other_ticket):
        if other_ticket.id != self.id:
            other_ticket.is_merged = True
            other_ticket.parent_ticket_id = self.id
            return True
        return False

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)  # in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    attachments = db.relationship('Attachment', backref='message', lazy=True,
                                foreign_keys='Attachment.message_id')

# Knowledge Base Models
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#6c757d')
    articles = db.relationship('Article', secondary='article_tag_association', backref='tags')

class ArticleVote(db.Model):
    __tablename__ = 'article_votes'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_helpful = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraint
    __table_args__ = (
        db.UniqueConstraint('article_id', 'user_id', name='uix_article_user_vote'),
    )

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Draft')
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comments = db.relationship('ArticleComment', backref='article', lazy=True)
    votes = db.relationship('ArticleVote', backref='article', lazy=True)
    
    @property
    def helpful_count(self):
        return sum(1 for vote in self.votes if vote.is_helpful)
        
    @property
    def not_helpful_count(self):
        return sum(1 for vote in self.votes if not vote.is_helpful)
        
    def get_user_vote(self, user):
        for vote in self.votes:
            if vote.user_id == user.id:
                return vote
        return None

# Association table for articles and tags
article_tag_association = db.Table('article_tag_association',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class ArticleComment(db.Model):
    __tablename__ = 'article_comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    author = db.relationship('User', backref='article_comments')

# Custom Fields
class CustomField(db.Model):
    __tablename__ = 'custom_fields'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(20), nullable=False)  # text, number, select, checkbox, etc.
    is_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TicketCustomField(db.Model):
    __tablename__ = 'ticket_custom_fields'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Text)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('custom_fields.id'), nullable=False)

# SLA Management
class SLA(db.Model):
    __tablename__ = 'slas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    response_time = db.Column(db.Integer)  # in minutes
    resolution_time = db.Column(db.Integer)  # in minutes
    priority = db.Column(db.String(20))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SLAViolation(db.Model):
    __tablename__ = 'sla_violations'
    id = db.Column(db.Integer, primary_key=True)
    violation_type = db.Column(db.String(20))  # response_time, resolution_time
    expected_time = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    sla_id = db.Column(db.Integer, db.ForeignKey('slas.id'), nullable=False)

# Automation Rules
class AutomationRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(50))  # ticket_created, ticket_updated, etc.
    conditions = db.Column(db.JSON)  # Store conditions as JSON
    actions = db.Column(db.JSON)  # Store actions as JSON
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Reports
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50))  # ticket_volume, agent_performance, etc.
    parameters = db.Column(db.JSON)  # Store report parameters as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TicketChannel(db.Model):
    __tablename__ = 'ticket_channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # email, phone, chat, portal
    is_active = db.Column(db.Boolean, default=True)
    tickets = db.relationship('Ticket', backref='channel', lazy='dynamic')

class TicketPriority(db.Model):
    __tablename__ = 'ticket_priorities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # low, medium, high, critical
    color = db.Column(db.String(7), nullable=False)  # hex color code
    response_time = db.Column(db.Integer)  # in minutes
    resolution_time = db.Column(db.Integer)  # in minutes
    tickets = db.relationship('Ticket', backref='priority_level', lazy='dynamic')

class TicketStatus(db.Model):
    __tablename__ = 'ticket_statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7), nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    tickets = db.relationship('Ticket', backref='status_obj', lazy='dynamic')

class TicketTag(db.Model):
    __tablename__ = 'ticket_tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    tickets = db.relationship('Ticket', secondary='ticket_tag_association', backref='tags')

ticket_tag_association = db.Table('ticket_tag_association',
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('ticket_tags.id'), primary_key=True)
)

class TicketTemplate(db.Model):
    __tablename__ = 'ticket_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('ticket_priorities.id'))
    fields = db.relationship('CustomField', secondary='template_field_association')

template_field_association = db.Table('template_field_association',
    db.Column('template_id', db.Integer, db.ForeignKey('ticket_templates.id'), primary_key=True),
    db.Column('field_id', db.Integer, db.ForeignKey('custom_fields.id'), primary_key=True)
)

# Association table for Ticket-Asset relationship
ticket_assets = db.Table('ticket_assets',
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('assets.id'), primary_key=True)
)

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # Hardware, Software, Network, etc.
    status = db.Column(db.String(50), nullable=False)  # Active, Inactive, Retired, etc.
    purchase_date = db.Column(db.DateTime)
    warranty_end = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    location = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tickets = db.relationship('Ticket', secondary='ticket_assets', backref=db.backref('assets', lazy='dynamic'))

    def __repr__(self):
        return f'<Asset {self.name}>'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    renewal_date = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    frequency = db.Column(db.String(50)) # e.g., monthly, annually
    status = db.Column(db.String(50)) # e.g., Active, Expired, Pending Renewal
    notes = db.Column(db.Text)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_to = db.relationship('User', backref='subscriptions_assigned', foreign_keys=[assigned_to_id])

    def __repr__(self):
        return f'<Subscription {self.name}>'

class OfficeInventory(db.Model):
    __tablename__ = 'office_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50)) # e.g., Furniture, Electronics, Peripherals
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    status = db.Column(db.String(50)) # e.g., In Use, Available, Damaged
    notes = db.Column(db.Text)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_to = db.relationship('User', backref='inventory_assigned', foreign_keys=[assigned_to_id])

    def __repr__(self):
        return f'<OfficeInventory {self.item_name}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    changes = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    
    __table_args__ = (
        db.Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
    )

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
