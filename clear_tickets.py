from app import create_app, db
from app.models import Ticket, Comment, Attachment, TicketCustomField, SLAViolation, AuditLog

def clear_all_tickets():
    app = create_app()
    with app.app_context():
        try:
            # Delete all related records first
            print("Deleting comments...")
            Comment.query.delete()
            
            print("Deleting attachments...")
            Attachment.query.delete()
            
            print("Deleting custom fields...")
            TicketCustomField.query.delete()
            
            print("Deleting SLA violations...")
            SLAViolation.query.delete()
            
            print("Deleting ticket audit logs...")
            AuditLog.query.filter_by(entity_type='ticket').delete()
            
            print("Deleting tickets...")
            Ticket.query.delete()
            
            db.session.commit()
            print("All tickets and related data have been cleared successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    clear_all_tickets() 