from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from datetime import datetime
import os
import secrets
import string
from functools import wraps

app = Flask(__name__)
# Runtime config for Railway: read from env with safe fallbacks
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change')
db_url = os.getenv('DATABASE_URL', 'sqlite:///military_recruitment.db')
# Heroku/Railway may provide postgres://; SQLAlchemy expects postgresql://
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Admin credentials (change in production!)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Models
class Recruitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    birth_date = db.Column(db.String(50), nullable=False)
    r_age = db.Column(db.String(10))
    time_on_project = db.Column(db.String(100))
    previous_faction_experience = db.Column(db.String(200))
    shooting_skills = db.Column(db.String(10))
    knowledge_of_law = db.Column(db.Text)
    passport_series = db.Column(db.String(10))
    passport_number = db.Column(db.String(20))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    roblox_nick = db.Column(db.String(100))
    address = db.Column(db.Text)
    education = db.Column(db.String(200))
    work_experience = db.Column(db.Text)
    live_in_area = db.Column(db.String(200))
    ready_to_serve_the_country = db.Column(db.String(100))
    military_rank = db.Column(db.String(50))
    previous_service = db.Column(db.Text)
    department_preference = db.Column(db.String(200))
    additional_info = db.Column(db.Text)
    status = db.Column(db.String(50), default='На рассмотрении')
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        user_info = None
        ua = getattr(self, 'user_account', None)
        if ua:
            ua_obj = ua[0] if isinstance(ua, list) and len(ua) > 0 else ua
            if ua_obj:
                user_info = {
                    'username': ua_obj.username,
                    'password': ua_obj.password
                }
        
        return {
            'id': self.id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'birth_date': self.birth_date,
            'r_age': self.r_age,
            'time_on_project': self.time_on_project,
            'previous_faction_experience': self.previous_faction_experience,
            'shooting_skills': self.shooting_skills,
            'knowledge_of_law': self.knowledge_of_law,
            'passport_series': self.passport_series,
            'passport_number': self.passport_number,
            'phone': self.phone,
            'email': self.email,
            'roblox_nick': self.roblox_nick,
            'address': self.address,
            'education': self.education,
            'work_experience': self.work_experience,
            'live_in_area': self.live_in_area,
            'ready_to_serve_the_country': self.ready_to_serve_the_country,
            'military_rank': self.military_rank,
            'previous_service': self.previous_service,
            'department_preference': self.department_preference,
            'additional_info': self.additional_info,
            'status': self.status,
            'submission_date': self.submission_date.strftime('%Y-%m-%d %H:%M:%S'),
            'user_account': user_info
        }

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100))
    author = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date.strftime('%Y-%m-%d'),
            'category': self.category,
            'author': self.author
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recruitment_id = db.Column(db.Integer, db.ForeignKey('recruitment.id'), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    rank = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    recruitment = db.relationship('Recruitment', backref=backref('user_account', uselist=False))

# New models for user panel
class CombatTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='new')  # new, in_progress, done
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    due_date = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    issued_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='assigned')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DaySchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)  # e.g. Monday
    wake_up = db.Column(db.String(20))
    training = db.Column(db.String(50))
    duty = db.Column(db.String(50))
    rest = db.Column(db.String(50))
    lights_out = db.Column(db.String(20))

# Groups
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recruitment')
def recruitment():
    return render_template('recruitment.html')

# -------- User auth (non-admin) --------
def user_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard'))
        return render_template('login.html', role='user', error='Неверный логин или пароль')
    return render_template('login.html', role='user')

@app.route('/logout')
def user_logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/user')
@user_login_required
def user_dashboard():
    uid = session.get('user_id')
    user = User.query.get(uid) if uid else None
    return render_template('user_dashboard.html', current_user=user)

# -------- User APIs (scoped to current user) --------
def current_user_id():
    return session.get('user_id')

@app.route('/api/user/tasks', methods=['GET'])
@user_login_required
def api_user_tasks():
    uid = current_user_id()
    tasks = CombatTask.query.filter_by(user_id=uid).order_by(CombatTask.created_at.desc()).all()
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'due_date': t.due_date,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
        } for t in tasks
    ])

@app.route('/api/user/assignments', methods=['GET'])
@user_login_required
def api_user_assignments():
    uid = current_user_id()
    items = Assignment.query.filter_by(user_id=uid).order_by(Assignment.created_at.desc()).all()
    return jsonify([
        {
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'issued_by': a.issued_by,
            'status': a.status,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
        } for a in items
    ])

@app.route('/api/user/notifications', methods=['GET'])
@user_login_required
def api_user_notifications():
    uid = current_user_id()
    items = Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).all()
    return jsonify([
        {
            'id': n.id,
            'content': n.content,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
        } for n in items
    ])

@app.route('/api/user/schedule', methods=['GET'])
@user_login_required
def api_user_schedule():
    uid = current_user_id()
    items = DaySchedule.query.filter_by(user_id=uid).all()
    return jsonify([
        {
            'id': s.id,
            'day': s.day,
            'wake_up': s.wake_up,
            'training': s.training,
            'duty': s.duty,
            'rest': s.rest,
            'lights_out': s.lights_out
        } for s in items
    ])
@app.route('/recruitment/submit', methods=['POST'])
def submit_recruitment():
    try:
        # Accept both JSON and form submissions
        data = request.get_json(silent=True) or request.form.to_dict()

        # Debug: log incoming payload
        app.logger.info({'event': 'recruitment_submit_received', 'payload': data})

        # Basic required fields validation
        required_fields = [
            'last_name', 'first_name', 'birth_date', 'r_age', 'time_on_project',
            'previous_faction_experience', 'shooting_skills', 'knowledge_of_law', 'phone',
            'username', 'password'
        ]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({'success': False, 'message': f"Отсутствуют обязательные поля: {', '.join(missing)}"}), 400

        new_recruitment = Recruitment(
            last_name=data.get('last_name', ''),
            first_name=data.get('first_name', ''),
            middle_name=data.get('middle_name', ''),
            birth_date=data.get('birth_date', ''),
            r_age=data.get('r_age', ''),
            time_on_project=data.get('time_on_project', ''),
            previous_faction_experience=data.get('previous_faction_experience', ''),
            shooting_skills=data.get('shooting_skills', ''),
            knowledge_of_law=data.get('knowledge_of_law', ''),
            passport_series=data.get('passport_series', ''),
            passport_number=data.get('passport_number', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            roblox_nick=data.get('roblox_nick', ''),
            address=data.get('address', ''),
            education=data.get('education', ''),
            work_experience=data.get('work_experience', ''),
            live_in_area=data.get('live_in_area', ''),
            ready_to_serve_the_country=data.get('ready_to_serve_the_country', ''),
            military_rank=data.get('military_rank', ''),
            previous_service=data.get('previous_service', ''),
            department_preference=data.get('department_preference', ''),
            additional_info=data.get('additional_info', '')
        )
        
        db.session.add(new_recruitment)
        db.session.commit()
        app.logger.info({'event': 'recruitment_saved', 'record': new_recruitment.to_dict()})
        
        # Создаем аккаунт пользователя с указанными логином и паролем
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # Простейшая валидация логина/пароля
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Логин должен быть не короче 3 символов'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Пароль должен быть не короче 6 символов'}), 400

        # Проверка уникальности логина
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Логин уже занят, выберите другой'}), 400

        new_user = User(
            recruitment_id=new_recruitment.id,
            username=username,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        app.logger.info({'event': 'user_created_for_recruitment', 'recruitment_id': new_recruitment.id, 'username': username})
        
        return jsonify({
            'success': True, 
            'message': 'Заявка успешно отправлена! Учетная запись создана.',
            'id': new_recruitment.id,
            'username': username,
            'password': password,
            'show_credentials': True
        })
    except Exception as e:
        db.session.rollback()
        app.logger.exception({'event': 'recruitment_submit_failed', 'error': str(e)})
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', role='admin', error='Неверный логин или пароль')
    
    return render_template('login.html', role='admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/applications')
@login_required
def admin_applications():
    return render_template('admin_applications.html')

@app.route('/admin/news')
@login_required
def admin_news():
    return render_template('admin_news.html')

@app.route('/admin/users')
@login_required
def admin_users():
    return render_template('admin_users.html')

@app.route('/api/applications', methods=['GET'])
def get_applications():
    applications = Recruitment.query.order_by(Recruitment.submission_date.desc()).all()
    return jsonify([app.to_dict() for app in applications])

@app.route('/api/applications/<int:id>', methods=['GET'])
def get_application(id):
    application = Recruitment.query.get_or_404(id)
    return jsonify(application.to_dict())

@app.route('/api/applications/<int:id>/status', methods=['PUT'])
def update_application_status(id):
    application = Recruitment.query.get_or_404(id)
    data = request.get_json()
    application.status = data.get('status', application.status)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Статус обновлен'})

@app.route('/api/news', methods=['GET'])
def get_news():
    news = News.query.order_by(News.date.desc()).limit(10).all()
    return jsonify([item.to_dict() for item in news])

@app.route('/api/news', methods=['POST'])
@login_required
def create_news():
    data = request.get_json()
    news_item = News(
        title=data['title'],
        content=data['content'],
        category=data.get('category', ''),
        author=data.get('author', 'Администратор')
    )
    db.session.add(news_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Новость создана', 'id': news_item.id})

@app.route('/api/news/<int:id>', methods=['GET'])
def get_news_item(id):
    news_item = News.query.get_or_404(id)
    return jsonify(news_item.to_dict())

@app.route('/api/news/<int:id>', methods=['PUT'])
@login_required
def update_news(id):
    news_item = News.query.get_or_404(id)
    data = request.get_json()
    
    news_item.title = data.get('title', news_item.title)
    news_item.content = data.get('content', news_item.content)
    news_item.category = data.get('category', news_item.category)
    news_item.author = data.get('author', news_item.author)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Новость обновлена'})

@app.route('/api/news/<int:id>', methods=['DELETE'])
@login_required
def delete_news(id):
    news_item = News.query.get_or_404(id)
    db.session.delete(news_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Новость удалена'})

# -------- Admin APIs: Groups management --------
@app.route('/api/admin/users', methods=['GET'])
@login_required
def admin_list_users():
    users = User.query.order_by(User.created_date.desc()).all()
    return jsonify([{ 'id': u.id, 'username': u.username, 'rank': (u.rank or '') } for u in users])

@app.route('/api/admin/groups', methods=['GET'])
@login_required
def admin_list_groups():
    groups = Group.query.order_by(Group.created_at.desc()).all()
    return jsonify([{ 'id': g.id, 'name': g.name, 'description': g.description } for g in groups])

@app.route('/api/admin/groups', methods=['POST'])
@login_required
def admin_create_group():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Название группы обязательно'}), 400
    if Group.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': 'Группа с таким названием уже существует'}), 400
    g = Group(name=name, description=data.get('description', ''))
    db.session.add(g)
    db.session.commit()
    return jsonify({'success': True, 'id': g.id})

@app.route('/api/admin/groups/<int:group_id>', methods=['PUT'])
@login_required
def admin_update_group(group_id):
    g = Group.query.get_or_404(group_id)
    data = request.get_json() or {}
    if 'name' in data:
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Название не может быть пустым'}), 400
        exists = Group.query.filter(Group.name==name, Group.id!=group_id).first()
        if exists:
            return jsonify({'success': False, 'message': 'Название уже занято'}), 400
        g.name = name
    if 'description' in data:
        g.description = data.get('description')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/groups/<int:group_id>', methods=['DELETE'])
@login_required
def admin_delete_group(group_id):
    g = Group.query.get_or_404(group_id)
    GroupMember.query.filter_by(group_id=group_id).delete()
    db.session.delete(g)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def admin_update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    if 'rank' in data:
        user.rank = data.get('rank')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/groups/<int:group_id>/members', methods=['GET'])
@login_required
def admin_list_group_members(group_id):
    Group.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group_id).all()
    return jsonify([{ 'id': m.id, 'user_id': m.user_id, 'username': User.query.get(m.user_id).username } for m in members])

@app.route('/api/admin/groups/<int:group_id>/members', methods=['POST'])
@login_required
def admin_add_group_member(group_id):
    Group.query.get_or_404(group_id)
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    exists = GroupMember.query.filter_by(group_id=group_id, user_id=user.id).first()
    if exists:
        return jsonify({'success': False, 'message': 'Уже в группе'}), 400
    gm = GroupMember(group_id=group_id, user_id=user.id)
    db.session.add(gm)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/groups/<int:group_id>/members/<int:user_id>', methods=['DELETE'])
@login_required
def admin_remove_group_member(group_id, user_id):
    gm = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first_or_404()
    db.session.delete(gm)
    db.session.commit()
    return jsonify({'success': True})

# -------- Admin APIs: Actions (tasks, assignments, schedule) --------
def _resolve_targets(user_id, group_id):
    targets = []
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return []
        targets = [user.id]
    elif group_id:
        user_ids = [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]
        targets = user_ids
    return targets

@app.route('/api/admin/actions/task', methods=['POST'])
@login_required
def admin_create_task():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Заголовок обязателен'}), 400
    targets = _resolve_targets(user_id, group_id)
    for uid in targets:
        t = CombatTask(
            user_id=uid,
            title=title,
            description=data.get('description', ''),
            status=data.get('status', 'new'),
            priority=data.get('priority', 'normal'),
            due_date=data.get('due_date')
        )
        db.session.add(t)
    db.session.commit()
    return jsonify({'success': True, 'created_for': len(targets)})

@app.route('/api/admin/actions/assignment', methods=['POST'])
@login_required
def admin_create_assignment():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Заголовок обязателен'}), 400
    targets = _resolve_targets(user_id, group_id)
    for uid in targets:
        a = Assignment(
            user_id=uid,
            title=title,
            description=data.get('description', ''),
            issued_by=data.get('issued_by', 'Командование'),
            status=data.get('status', 'assigned'),
        )
        db.session.add(a)
    db.session.commit()
    return jsonify({'success': True, 'created_for': len(targets)})

@app.route('/api/admin/actions/schedule', methods=['POST'])
@login_required
def admin_create_schedule():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    day = data.get('day', '').strip()
    if not day:
        return jsonify({'success': False, 'message': 'День обязателен'}), 400
    targets = _resolve_targets(user_id, group_id)
    for uid in targets:
        s = DaySchedule(
            user_id=uid,
            day=day,
            wake_up=data.get('wake_up'),
            training=data.get('training'),
            duty=data.get('duty'),
            rest=data.get('rest'),
            lights_out=data.get('lights_out')
        )
        db.session.add(s)
    db.session.commit()
    return jsonify({'success': True, 'created_for': len(targets)})

# Initialize database automatically if empty (table or DB does not exist)
def auto_db_init():
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if not tables:
            db.create_all()
            app.logger.info('[Auto-DB-Init] Все таблицы созданы (база была пуста)')
        else:
            app.logger.info('[Auto-DB-Init] Таблицы уже существуют, инициализация не требуется')
    except Exception as e:
        app.logger.error(f'[Auto-DB-Init] Ошибка инициализации БД: {e}')

with app.app_context():
    auto_db_init()
    # SQLite-only compatibility ALTERs (skip on Postgres)
    try:
        if db.engine.url.drivername.startswith('sqlite'):
            existing_cols = {row[1] for row in db.session.execute(db.text('PRAGMA table_info(recruitment)'))}
            recruitment_columns = {
                'r_age': 'VARCHAR(10)',
                'time_on_project': 'VARCHAR(100)',
                'previous_faction_experience': 'VARCHAR(200)',
                'shooting_skills': 'VARCHAR(10)',
                'knowledge_of_law': 'TEXT',
                'passport_series': 'VARCHAR(10)',
                'passport_number': 'VARCHAR(20)',
                'email': 'VARCHAR(100)',
                'roblox_nick': 'VARCHAR(100)',
                'address': 'TEXT',
                'education': 'VARCHAR(200)',
                'work_experience': 'TEXT',
                'live_in_area': 'VARCHAR(200)',
                'ready_to_serve_the_country': 'VARCHAR(100)',
                'military_rank': 'VARCHAR(50)',
                'previous_service': 'TEXT',
                'department_preference': 'VARCHAR(200)',
                'additional_info': 'TEXT'
            }
            for col_name, col_type in recruitment_columns.items():
                if col_name not in existing_cols:
                    db.session.execute(db.text(f'ALTER TABLE recruitment ADD COLUMN {col_name} {col_type}'))

            user_cols = {row[1] for row in db.session.execute(db.text('PRAGMA table_info(user)'))}
            if 'rank' not in user_cols:
                db.session.execute(db.text('ALTER TABLE user ADD COLUMN rank VARCHAR(50)'))
            db.session.commit()
    except Exception:
        db.session.rollback()
    
    # No default news seeding

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1', host='0.0.0.0', port=int(os.getenv('PORT', '8080')))

