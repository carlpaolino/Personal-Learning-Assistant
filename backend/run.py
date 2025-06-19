from app import create_app, db
from app.models import User, Plan, Task, Upload, Reminder, ChatLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add database models to Flask shell context"""
    return {
        'db': db,
        'User': User,
        'Plan': Plan,
        'Task': Task,
        'Upload': Upload,
        'Reminder': Reminder,
        'ChatLog': ChatLog
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 