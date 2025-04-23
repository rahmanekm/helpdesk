from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Category, Ticket, Comment, Notification

def create_sample_data():
    # Create the Flask application context
    app = create_app()
    with app.app_context():
        # Clear existing data
        Comment.query.delete()
        Notification.query.delete()
        Ticket.query.delete()
        Category.query.delete()
        User.query.delete()
        
        # Create sample users
        users = [
            {
                'email': 'admin@helpdesk.com',
                'username': 'admin',
                'password': 'admin123',
                'department': 'IT',
                'role': 'admin'
            },
            {
                'email': 'agent@helpdesk.com',
                'username': 'agent',
                'password': 'agent123',
                'department': 'Support',
                'role': 'agent'
            },
            {
                'email': 'user@helpdesk.com',
                'username': 'user',
                'password': 'user123',
                'department': 'Marketing',
                'role': 'user'
            }
        ]
        
        created_users = {}
        for user_data in users:
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                department=user_data['department'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users[user_data['role']] = user
        
        # Create sample categories
        categories = [
            {
                'name': 'Hardware Issues',
                'description': 'Problems with physical computer hardware'
            },
            {
                'name': 'Software Issues',
                'description': 'Problems with software applications'
            },
            {
                'name': 'Network Issues',
                'description': 'Problems with internet or network connectivity'
            },
            {
                'name': 'Account Access',
                'description': 'Issues with account login or permissions'
            },
            {
                'name': 'General Inquiry',
                'description': 'General questions and information requests'
            }
        ]
        
        created_categories = {}
        for cat_data in categories:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
            created_categories[cat_data['name']] = category
        
        # Create sample tickets
        tickets = [
            {
                'subject': 'Cannot access my email',
                'description': 'I am unable to log in to my email account since this morning.',
                'category': 'Account Access',
                'priority': 'high',
                'status': 'open',
                'submitter': 'user',
                'created_at': datetime.utcnow() - timedelta(days=2)
            },
            {
                'subject': 'Printer not working',
                'description': 'The office printer on the 2nd floor is showing an error message.',
                'category': 'Hardware Issues',
                'priority': 'medium',
                'status': 'in_progress',
                'submitter': 'user',
                'assigned_to': 'agent',
                'created_at': datetime.utcnow() - timedelta(days=1)
            },
            {
                'subject': 'New software installation request',
                'description': 'Need Adobe Photoshop installed on my workstation.',
                'category': 'Software Issues',
                'priority': 'low',
                'status': 'assigned',
                'submitter': 'user',
                'assigned_to': 'agent',
                'created_at': datetime.utcnow() - timedelta(hours=12)
            },
            {
                'subject': 'Slow internet connection',
                'description': 'Internet speed has been very slow for the past hour.',
                'category': 'Network Issues',
                'priority': 'high',
                'status': 'resolved',
                'submitter': 'user',
                'assigned_to': 'agent',
                'created_at': datetime.utcnow() - timedelta(days=3),
                'closed_at': datetime.utcnow() - timedelta(days=2)
            },
            {
                'subject': 'Request for second monitor',
                'description': 'Requesting an additional monitor for improved productivity.',
                'category': 'Hardware Issues',
                'priority': 'low',
                'status': 'pending',
                'submitter': 'user',
                'assigned_to': 'agent',
                'created_at': datetime.utcnow() - timedelta(days=4)
            }
        ]
        
        created_tickets = []
        for ticket_data in tickets:
            ticket = Ticket(
                subject=ticket_data['subject'],
                description=ticket_data['description'],
                status=ticket_data['status'],
                priority=ticket_data['priority'],
                created_at=ticket_data['created_at'],
                submitter=created_users[ticket_data['submitter']],
                ticket_category=created_categories[ticket_data['category']]
            )
            if 'assigned_to' in ticket_data:
                ticket.assigned_agent = created_users[ticket_data['assigned_to']]
            if 'closed_at' in ticket_data:
                ticket.closed_at = ticket_data['closed_at']
            db.session.add(ticket)
            created_tickets.append(ticket)
        
        # Create sample comments
        comments = [
            {
                'ticket_index': 0,
                'content': 'Please provide your employee ID for verification.',
                'author': 'agent',
                'is_internal': False
            },
            {
                'ticket_index': 1,
                'content': 'I will check the printer shortly.',
                'author': 'agent',
                'is_internal': False
            },
            {
                'ticket_index': 1,
                'content': 'Printer needs new toner cartridge.',
                'author': 'agent',
                'is_internal': True
            },
            {
                'ticket_index': 2,
                'content': 'Software request approved. Will schedule installation.',
                'author': 'admin',
                'is_internal': False
            },
            {
                'ticket_index': 3,
                'content': 'Issue resolved - Router was rebooted.',
                'author': 'agent',
                'is_internal': False
            }
        ]
        
        for comment_data in comments:
            comment = Comment(
                content=comment_data['content'],
                is_internal=comment_data['is_internal'],
                ticket=created_tickets[comment_data['ticket_index']],
                author=created_users[comment_data['author']]
            )
            db.session.add(comment)
        
        # Create sample notifications
        notifications = [
            {
                'user': 'user',
                'message': 'Your ticket has been assigned to an agent.',
                'is_read': False
            },
            {
                'user': 'agent',
                'message': 'New ticket assigned to you: Printer not working',
                'is_read': True
            },
            {
                'user': 'admin',
                'message': 'New software installation request needs approval',
                'is_read': False
            }
        ]
        
        for notif_data in notifications:
            notification = Notification(
                message=notif_data['message'],
                is_read=notif_data['is_read'],
                user=created_users[notif_data['user']]
            )
            db.session.add(notification)
        
        # Commit all changes
        db.session.commit()
        print('Sample data has been created successfully!')

if __name__ == '__main__':
    create_sample_data()