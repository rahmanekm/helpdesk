from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from .forms import ArticleForm, CommentForm
from ..models import Article, Category, ArticleComment, Tag, ArticleVote, db
from ..decorators import admin_required, agent_required
from . import bp
from functools import wraps

def admin_or_agent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin or current_user.is_agent):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('articles')
@login_required
def list_articles():
    page = request.args.get('page', 1, type=int)
    if current_user.is_admin or current_user.is_agent:
        # Admins and agents can see all articles
        articles = Article.query.order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    else:
        # Regular users can only see published articles
        articles = Article.query.filter_by(status='Published').order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('knowledge_base/list_articles.html', articles=articles)

@bp.route('articles/<int:id>')
@login_required
def view_article(id):
    article = Article.query.get_or_404(id)
    
    # Only allow viewing published articles for non-admins and non-agents
    if article.status != 'Published' and not (current_user.is_admin or current_user.is_agent):
        abort(403)
        
    article.views += 1
    db.session.commit()
    
    # Get related articles (same category)
    if current_user.is_admin or current_user.is_agent:
        related_articles = Article.query.filter(
            Article.category_id == article.category_id,
            Article.id != article.id
        ).order_by(Article.views.desc()).limit(5).all()
    else:
        related_articles = Article.query.filter(
            Article.category_id == article.category_id,
            Article.id != article.id,
            Article.status == 'Published'
        ).order_by(Article.views.desc()).limit(5).all()
    
    # Get user's vote if exists
    user_vote = article.get_user_vote(current_user)
    
    form = CommentForm()
    return render_template('knowledge_base/view_article.html',
                         article=article,
                         related_articles=related_articles,
                         user_vote=user_vote,
                         form=form)

@bp.route('articles/create', methods=['GET', 'POST'])
@login_required
@admin_or_agent_required
def create_article():
    form = ArticleForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            status=form.status.data
        )
        
        if form.category.data:
            article.category_id = form.category.data
            
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                article.tags.append(tag)
        
        db.session.add(article)
        db.session.commit()
        flash('Article created successfully.', 'success')
        return redirect(url_for('.view_article', id=article.id))
        
    return render_template('knowledge_base/edit_article.html', form=form)

@bp.route('articles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_agent_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    form = ArticleForm(obj=article)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.status = form.status.data
        
        if form.category.data:
            article.category_id = form.category.data
        else:
            article.category_id = None
            
        # Update tags
        article.tags = []
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                article.tags.append(tag)
        
        db.session.commit()
        flash('Article updated successfully.', 'success')
        return redirect(url_for('.view_article', id=article.id))
        
    return render_template('knowledge_base/edit_article.html', form=form, article=article)

@bp.route('articles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully.', 'success')
    return redirect(url_for('.list_articles'))

@bp.route('articles/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    article = Article.query.get_or_404(article_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = ArticleComment(
            content=form.content.data,
            article_id=article.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.')
    return redirect(url_for('.view_article', id=article.id))

@bp.route('categories/<int:category_id>')
@login_required
def category_articles(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    
    if current_user.is_admin or current_user.is_agent:
        articles = Article.query.filter_by(category_id=category_id).order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    else:
        articles = Article.query.filter_by(
            category_id=category_id,
            status='Published'
        ).order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
        
    return render_template('knowledge_base/list_articles.html',
                         category=category,
                         articles=articles)

@bp.route('articles/<int:article_id>/vote', methods=['POST'])
@login_required
def vote_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    # Only allow voting on published articles for non-admins and non-agents
    if article.status != 'Published' and not (current_user.is_admin or current_user.is_agent):
        return jsonify({'error': 'Cannot vote on unpublished articles'}), 403
        
    is_helpful = request.json.get('is_helpful')
    
    if is_helpful is None:
        return jsonify({'error': 'is_helpful parameter is required'}), 400
        
    # Check for existing vote
    existing_vote = ArticleVote.query.filter_by(
        article_id=article_id,
        user_id=current_user.id
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.is_helpful = is_helpful
    else:
        # Create new vote
        vote = ArticleVote(
            article_id=article_id,
            user_id=current_user.id,
            is_helpful=is_helpful
        )
        db.session.add(vote)
    
    db.session.commit()
    
    return jsonify({
        'helpful_count': article.helpful_count,
        'not_helpful_count': article.not_helpful_count
    })