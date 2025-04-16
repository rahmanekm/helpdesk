from app import create_app, db
from app.models import User, Category, Ticket, Comment, Attachment, Notification

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Ticket': Ticket,
        'Comment': Comment,
        'Attachment': Attachment,
        'Notification': Notification
    }

if __name__ == '__main__':
    app.run(debug=True) 