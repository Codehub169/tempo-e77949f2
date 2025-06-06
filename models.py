from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200), nullable=True) # For cards
    image_url = db.Column(db.String(200), nullable=True) # Thumbnail/main image
    technologies = db.Column(db.String(200), nullable=True) # Comma-separated or JSON string
    project_link = db.Column(db.String(200), nullable=True)
    repo_link = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)
    # For project detail page, can add more fields like gallery_images (JSON string of image paths)

    def __repr__(self):
        return f'<Project {self.title}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300), nullable=True) # For cards
    cover_image_url = db.Column(db.String(200), nullable=True)
    author = db.Column(db.String(80), nullable=False, default='John Doe')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(200), nullable=True) # Comma-separated or JSON string

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=True)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage from {self.name}>'
