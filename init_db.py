from datetime import datetime, timedelta
from datetime import timezone
from app import create_app, db
from app.models import (
    User, Category, Article, Tag, TicketStatus, TicketPriority,
    TicketChannel, Ticket, Comment, Asset, TicketTag
)

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.drop_all()
        db.create_all()
        
        # Create sample users
        admin = User(
            email='admin@example.com',
            username='admin',
            role='admin',
            is_active=True
        )
        admin.set_password('admin')
        
        agent = User(
            email='agent@example.com',
            username='agent',
            role='agent',
            is_active=True
        )
        agent.set_password('agent')
        
        user = User(
            email='user@example.com',
            username='user',
            role='user',
            is_active=True
        )
        user.set_password('user')
        
        db.session.add(admin)
        db.session.add(agent)
        db.session.add(user)
        
        # Create categories
        categories = [
            Category(name='Getting Started', description='Basic guides and tutorials'),
            Category(name='Account Management', description='User account related articles'),
            Category(name='Troubleshooting', description='Common issues and solutions'),
            Category(name='Security', description='Security best practices'),
            Category(name='FAQs', description='Frequently asked questions'),
            Category(name='Hardware', description='Hardware related issues'),
            Category(name='Software', description='Software related issues'),
            Category(name='Network', description='Network related issues')
        ]
        for category in categories:
            db.session.add(category)
        
        # Create ticket statuses
        statuses = [
            TicketStatus(name='Open', description='New ticket awaiting agent assignment', color='#dc3545', is_closed=False),
            TicketStatus(name='In Progress', description='Ticket is being worked on', color='#ffc107', is_closed=False),
            TicketStatus(name='Pending', description='Awaiting customer response', color='#17a2b8', is_closed=False),
            TicketStatus(name='Resolved', description='Issue has been resolved', color='#28a745', is_closed=True),
            TicketStatus(name='Closed', description='Ticket has been closed', color='#6c757d', is_closed=True)
        ]
        for status in statuses:
            db.session.add(status)
        
        # Create ticket priorities
        priorities = [
            TicketPriority(name='Low', color='#28a745', response_time=480, resolution_time=2880),  # 8h response, 2d resolution
            TicketPriority(name='Medium', color='#ffc107', response_time=240, resolution_time=1440),  # 4h response, 1d resolution
            TicketPriority(name='High', color='#dc3545', response_time=60, resolution_time=480),  # 1h response, 8h resolution
            TicketPriority(name='Critical', color='#dc3545', response_time=30, resolution_time=240)  # 30m response, 4h resolution
        ]
        for priority in priorities:
            db.session.add(priority)
        
        # Create ticket channels
        channels = [
            TicketChannel(name='Web Portal'),
            TicketChannel(name='Email'),
            TicketChannel(name='Phone'),
            TicketChannel(name='Chat')
        ]
        for channel in channels:
            db.session.add(channel)
        
        # Create sample assets
        assets = [
            Asset(
                name='Laptop-001',
                asset_type='Hardware',
                status='Active',
                serial_number='LT001',
                purchase_date=datetime.now(timezone.utc) - timedelta(days=365),
                warranty_end=datetime.now(timezone.utc) + timedelta(days=365),
                location='Main Office',
                assigned_to_id=user.id
            ),
            Asset(
                name='Desktop-001',
                asset_type='Hardware',
                status='Active',
                serial_number='DT001',
                purchase_date=datetime.now(timezone.utc) - timedelta(days=180),
                warranty_end=datetime.now(timezone.utc) + timedelta(days=550),
                location='Main Office',
                assigned_to_id=agent.id
            )
        ]
        for asset in assets:
            db.session.add(asset)
        
        # Create sample articles
        articles = [
            {
                'title': 'Welcome to Forefront IT Helpdesk',
                'content': '''
                <h2>Welcome to Forefront IT Helpdesk!</h2>
                <p>This article will help you get started with our platform.</p>
                <h3>Key Features:</h3>
                <ul>
                    <li>Knowledge Base</li>
                    <li>Ticket Management</li>
                    <li>User Support</li>
                </ul>
                ''',
                'category': 'Getting Started',
                'tags': ['welcome', 'introduction', 'guide'],
                'status': 'Published'
            },
            {
                'title': 'How to Reset Your Password',
                'content': '''
                <h2>Password Reset Guide</h2>
                <p>Follow these steps to reset your password:</p>
                <ol>
                    <li>Click on "Forgot Password"</li>
                    <li>Enter your email address</li>
                    <li>Check your email for reset instructions</li>
                    <li>Create a new password</li>
                </ol>
                ''',
                'category': 'Account Management',
                'tags': ['password', 'account', 'security'],
                'status': 'Published'
            }
        ]
        
        # Add articles
        for article_data in articles:
            category = Category.query.filter_by(name=article_data['category']).first()
            article = Article(
                title=article_data['title'],
                content=article_data['content'],
                status=article_data['status'],
                category_id=category.id,
                author_id=admin.id
            )
            
            # Add tags
            for tag_name in article_data['tags']:
                tag = Tag(name=tag_name)
                article.tags.append(tag)
            
            db.session.add(article)
        
        # Create sample tickets
        tickets = [
            {
                'subject': 'Cannot access email',
                'description': 'I am unable to access my email account since this morning.',
                'category': 'Software',
                'priority': 'High',
                'status': 'Open',
                'tags': ['email', 'access'],
                'assets': ['Laptop-001']
            },
            {
                'subject': 'Printer not working',
                'description': 'The office printer is showing an error message.',
                'category': 'Hardware',
                'priority': 'Medium',
                'status': 'In Progress',
                'tags': ['printer', 'hardware'],
                'assets': []
            },
            {
                'subject': 'Need software installation',
                'description': 'Please install the latest version of Microsoft Office on my computer.',
                'category': 'Software',
                'priority': 'Low',
                'status': 'Pending',
                'tags': ['software', 'installation'],
                'assets': ['Desktop-001']
            }
        ]
        
        # Add tickets
        for ticket_data in tickets:
            category = Category.query.filter_by(name=ticket_data['category']).first()
            priority = TicketPriority.query.filter_by(name=ticket_data['priority']).first()
            status = TicketStatus.query.filter_by(name=ticket_data['status']).first()
            channel = TicketChannel.query.filter_by(name='Web Portal').first()
            
            ticket = Ticket(
                subject=ticket_data['subject'],
                description=ticket_data['description'],
                category_id=category.id,
                priority_id=priority.id,
                status_id=status.id,
                channel_id=channel.id,
                submitter_id=user.id,
                requester_id=user.id,
                assigned_agent_id=agent.id if ticket_data['status'] != 'Open' else None,
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
                updated_at=datetime.now(timezone.utc) - timedelta(hours=2)
            )
            
            # Add tags with autoflush disabled
            db.session.autoflush = False
            for tag_name in ticket_data['tags']:
                tag = TicketTag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = TicketTag(name=tag_name)
                    db.session.add(tag)
                ticket.tags.append(tag)
            db.session.autoflush = True
            
            # Add assets with autoflush disabled
            db.session.autoflush = False
            for asset_name in ticket_data['assets']:
                asset = Asset.query.filter_by(name=asset_name).first()
                if asset:
                    ticket.assets.append(asset)
            db.session.autoflush = True
            
            db.session.add(ticket)
            
            # Add sample comment if ticket is not open
            if ticket_data['status'] != 'Open':
                comment = Comment(
                    content='I am working on this issue.',
                    ticket_id=ticket.id,
                    author_id=agent.id,
                    created_at=datetime.now(timezone.utc) - timedelta(hours=3)
                )
                db.session.add(comment)
        
        db.session.commit()
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_db() 