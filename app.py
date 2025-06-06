from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Project, BlogPost, ContactMessage
import os
from datetime import datetime

app = Flask(__name__)

# Database Configuration
# For local development, use SQLite. For production, use PostgreSQL or other.
# The DATABASE_URL environment variable will be used if set (e.g., by Heroku/Render)
# otherwise, it defaults to a local SQLite database.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database/portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_strong_secret_key_here') # Replace with a strong secret key

db.init_app(app)

# Ensure the database directory exists
with app.app_context():
    db_dir = os.path.join(app.root_path, 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db.create_all() # Creates tables if they don't exist

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

@app.route('/')
def home():
    featured_projects = Project.query.filter_by(featured=True).order_by(Project.date_created.desc()).limit(3).all()
    latest_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(3).all()
    return render_template('index.html', projects=featured_projects, posts=latest_posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.date_created.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/project/<slug>')
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template('project_detail.html', project=project)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts_pagination = BlogPost.query.order_by(BlogPost.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('blog.html', posts_pagination=posts_pagination)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('blog_post.html', post=post)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message_text = request.form.get('message')

            if not name or not email or not message_text:
                flash('Name, Email, and Message are required fields.', 'error')
                return render_template('contact.html', form_data=request.form)
            
            new_message = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Your message has been sent successfully! I will get back to you soon.', 'success')
            return redirect(url_for('contact')) # Or a thank you page
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error processing contact form: {e}")
            flash('An error occurred while sending your message. Please try again.', 'error')

    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- Helper function to add sample data (optional, for development) ---
def add_sample_data():
    with app.app_context():
        # Clear existing data
        db.session.query(Project).delete()
        db.session.query(BlogPost).delete()
        db.session.query(ContactMessage).delete()
        db.session.commit()

        # Sample Projects
        projects_data = [
            {
                'title': 'Project Alpha', 
                'slug': 'project-alpha', 
                'short_description': 'A dynamic e-commerce platform with a focus on user experience and seamless checkout processes.', 
                'description': 'Project Alpha is a full-featured e-commerce solution built with modern technologies. It includes product listings, user accounts, a shopping cart, and an admin panel for managing inventory and orders. The frontend is built with React for a responsive and interactive experience, while the backend uses Node.js and Express for robust API services, connected to a MongoDB database for flexibility.',
                'image_url': 'static/images/project_1_thumb.jpg', 
                'technologies': 'React,Node.js,MongoDB,Express.js,Tailwind CSS',
                'project_link': '#', 
                'repo_link': '#',
                'featured': True
            },
            {
                'title': 'Project Beta', 
                'slug': 'project-beta', 
                'short_description': 'An interactive data visualization tool for analyzing complex datasets with an intuitive interface.', 
                'description': 'Project Beta allows users to upload, process, and visualize large datasets. It features various chart types, filtering options, and data export capabilities. Built with Vue.js for the frontend for dynamic visualizations using D3.js, and Python/Flask on the backend for data processing and API endpoints.',
                'image_url': 'static/images/project_2_thumb.jpg', 
                'technologies': 'Vue.js,D3.js,Python,Flask,Pandas',
                'project_link': '#', 
                'repo_link': '#',
                'featured': True
            },
            {
                'title': 'Project Gamma', 
                'slug': 'project-gamma', 
                'short_description': 'A mobile-first social networking app designed for community engagement and content sharing.', 
                'description': 'Project Gamma is a social platform focusing on local communities. Users can create profiles, join groups, post updates, and share media. It emphasizes a clean UI and real-time interactions. Developed using React Native for cross-platform mobile compatibility and Firebase for backend services including authentication, database, and storage.',
                'image_url': 'static/images/project_3_thumb.jpg', 
                'technologies': 'React Native,Firebase,UX Design,JavaScript',
                'project_link': '#', 
                'repo_link': '#',
                'featured': True
            },
             {
                'title': 'Project Delta', 
                'slug': 'project-delta', 
                'short_description': 'A comprehensive personal finance tracker with budgeting tools and expense analysis.', 
                'description': 'Project Delta helps users manage their finances effectively. It supports multiple accounts, transaction categorization, budget creation, and insightful reports on spending habits. The backend is powered by Django, providing a secure and scalable API, while the frontend is a responsive web app built with HTML, CSS (Tailwind), and Vanilla JavaScript.',
                'image_url': 'static/images/placeholder_project.png', # Placeholder, replace with actual image 
                'technologies': 'Django,Python,JavaScript,Tailwind CSS,SQLite',
                'project_link': '#', 
                'repo_link': '#',
                'featured': False
            }
        ]
        for p_data in projects_data:
            project = Project(**p_data)
            db.session.add(project)

        # Sample Blog Posts
        blog_posts_data = [
            {
                'title': 'The Future of CSS: What\'s New and Exciting', 
                'slug': 'future-of-css', 
                'excerpt': 'Exploring upcoming CSS features like container queries, :has() selector, and new color spaces.', 
                'content': 'The world of CSS is constantly evolving, bringing powerful new tools for web developers. In this post, we explore some of the most anticipated features that are changing how we build layouts and style websites. Container queries allow components to adapt to their container size, not just the viewport. The :has() selector, often dubbed the \'parent selector\', opens up new possibilities for conditional styling. We also delve into new color spaces and functions that offer more vibrant and consistent colors across devices. Stay ahead of the curve by learning about these exciting advancements!',
                'cover_image_url': 'static/images/blog_1_cover.jpg', 
                'category': 'Web Development', 
                'tags': 'CSS,Frontend,Web Design,Future Tech'
            },
            {
                'title': 'Mastering Asynchronous JavaScript', 
                'slug': 'async-javascript', 
                'excerpt': 'A deep dive into Promises, async/await, and handling asynchronous operations effectively.', 
                'content': 'Asynchronous programming is a cornerstone of modern JavaScript development, especially for web applications that need to perform non-blocking operations like API calls. This post provides a comprehensive guide to understanding and mastering asynchronous JavaScript. We start with callbacks, move to Promises for better error handling and readability, and finally explore the elegant syntax of async/await. Learn best practices for managing complex asynchronous flows and avoiding common pitfalls like callback hell.',
                'cover_image_url': 'static/images/blog_2_cover.jpg', 
                'category': 'JavaScript', 
                'tags': 'JavaScript,Async,Promises,Node.js,Programming'
            },
            {
                'title': 'Navigating Your First Year as a Developer', 
                'slug': 'first-year-dev', 
                'excerpt': 'Tips and advice for new developers on learning, growing, and succeeding in the tech industry.', 
                'content': 'The first year as a software developer can be both exciting and challenging. This article offers practical advice for those starting their journey in the tech world. Topics include effective learning strategies, finding mentors, dealing with imposter syndrome, contributing to a team, and building a sustainable career. Learn how to make the most of your first year and set yourself up for long-term success.',
                'cover_image_url': 'static/images/blog_3_cover.jpg', 
                'category': 'Career', 
                'tags': 'Career Advice,Software Development,Junior Developer,Tech Industry'
            },
            {
                'title': 'Introduction to Docker for Web Developers', 
                'slug': 'docker-for-web-devs', 
                'excerpt': 'Learn how Docker can streamline your development workflow and simplify deployment.', 
                'content': 'Docker has revolutionized how applications are built, shipped, and run. For web developers, it offers consistent development environments, easier collaboration, and simplified deployment processes. This introductory guide covers the basics of Docker, including images, containers, Dockerfiles, and Docker Compose. Understand the benefits of containerization and how to integrate Docker into your web development projects to improve efficiency and reduce headaches.',
                'cover_image_url': 'static/images/placeholder_blog.png', # Placeholder, replace with actual image
                'category': 'DevOps', 
                'tags': 'Docker,Deployment,Web Development,Tools'
            }
        ]
        for b_data in blog_posts_data:
            post = BlogPost(**b_data)
            db.session.add(post)
        
        db.session.commit()
        print("Sample data added.")

if __name__ == '__main__':
    with app.app_context():
        # Check if DB needs seeding (e.g. if Projects table is empty)
        if not Project.query.first() and not BlogPost.query.first():
            print("Database appears to be empty. Adding sample data...")
            add_sample_data()
        else:
            print("Database already contains data. Skipping sample data addition.")
    # The host and port are typically managed by Gunicorn in startup.sh
    # For direct `python app.py` execution for development:
    app.run(debug=True, host='0.0.0.0', port=9000)
