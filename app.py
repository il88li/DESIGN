import os
import sys
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Portfolio, Video, Testimonial, Setting
from config import Config

# ===== إنشاء تطبيق Flask =====
app = Flask(__name__)
app.config.from_object(Config)

# ===== حل مشكلة نظام الملفات للقراءة فقط في Vercel =====
# إذا كان متغير DATABASE_URL موجوداً (أي أننا في بيئة إنتاج تستخدم PostgreSQL)،
# نغير مجلد المثيل إلى /tmp لتفادي محاولة الكتابة في نظام الملفات للقراءة فقط.
if os.environ.get('DATABASE_URL'):
    app.instance_path = '/tmp'
    # نضمن وجود المجلد (آمن لأن /tmp موجود دائماً)
    os.makedirs(app.instance_path, exist_ok=True)
    print(f"✅ تم تعيين instance_path إلى: {app.instance_path}")

# ===== تهيئة قاعدة البيانات =====
db.init_app(app)

# ===== إنشاء الجداول إذا لم تكن موجودة =====
with app.app_context():
    db.create_all()
    # إعدادات افتراضية (النص التعريفي والصورة الشخصية)
    if not Setting.query.filter_by(key='bio_text').first():
        bio = Setting(key='bio_text', value='أقدم حلولاً بصرية إبداعية تساعد العلامات التجارية والأفراد على الظهور بشكل احترافي ومميز. أؤمن أن لكل تصميم هوية، ولكل هوية هدف ورسالة.')
        db.session.add(bio)
    if not Setting.query.filter_by(key='profile_image').first():
        img = Setting(key='profile_image', value='https://via.placeholder.com/400x400/DBB5EE/4C0585?text=Your+Photo')
        db.session.add(img)
    db.session.commit()

# ===== دالة لرفع الصور (تدعم Supabase Storage أو التخزين المحلي) =====
def upload_to_supabase(file):
    """رفع الملف إلى Supabase Storage (إذا تم تكوينه) أو حفظه محلياً"""
    if not app.config.get('SUPABASE_URL') or not app.config.get('SUPABASE_KEY'):
        # الحل البديل: حفظ الملف محلياً (للاختبار المحلي فقط)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return os.path.join('uploads', filename)
    
    # استخدام Supabase Storage (إذا تم تفعيل المفاتيح)
    try:
        from supabase import create_client
        supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
        
        # إنشاء اسم ملف فريد
        ext = file.filename.rsplit('.', 1)[-1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # رفع الملف
        file_data = file.read()
        res = supabase.storage.from_('portfolio').upload(filename, file_data)
        
        # الحصول على الرابط العام
        public_url = supabase.storage.from_('portfolio').get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"خطأ في رفع الصورة: {e}")
        # في حالة الفشل، نحاول الحفظ محلياً
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return os.path.join('uploads', filename)

# ===== دالة لتسجيل الدخول =====
def is_authenticated():
    return session.get('logged_in', False)

# ===== الصفحة الرئيسية =====
@app.route('/')
def index():
    portfolio_items = Portfolio.query.order_by(Portfolio.created_at.desc()).all()
    videos = Video.query.order_by(Video.created_at.desc()).all()
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    bio = Setting.query.filter_by(key='bio_text').first()
    profile_img = Setting.query.filter_by(key='profile_image').first()
    
    return render_template('index.html',
                           portfolio=portfolio_items,
                           videos=videos,
                           testimonials=testimonials,
                           bio=bio.value if bio else '',
                           profile_img=profile_img.value if profile_img else '')

# ===== تسجيل الدخول =====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('كلمة المرور غير صحيحة', 'danger')
    return render_template('admin_login.html')

# ===== تسجيل الخروج =====
@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('index'))

# ===== لوحة التحكم =====
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_authenticated():
        flash('يرجى تسجيل الدخول أولاً', 'warning')
        return redirect(url_for('admin_login'))
    
    portfolio = Portfolio.query.all()
    videos = Video.query.all()
    testimonials = Testimonial.query.all()
    bio = Setting.query.filter_by(key='bio_text').first()
    profile_img = Setting.query.filter_by(key='profile_image').first()
    
    return render_template('admin_dashboard.html',
                           portfolio=portfolio,
                           videos=videos,
                           testimonials=testimonials,
                           bio=bio.value if bio else '',
                           profile_img=profile_img.value if profile_img else '')

# ===== إدارة الأعمال (إضافة) =====
@app.route('/admin/portfolio/add', methods=['POST'])
def add_portfolio():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image')
    
    if not title:
        flash('العنوان مطلوب', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    image_path = None
    if image and image.filename:
        image_path = upload_to_supabase(image)
    
    new_item = Portfolio(title=title, description=description, image=image_path)
    db.session.add(new_item)
    db.session.commit()
    flash('تمت إضافة المشروع بنجاح', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== إدارة الأعمال (حذف) =====
@app.route('/admin/portfolio/delete/<int:id>')
def delete_portfolio(id):
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    item = Portfolio.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('تم حذف المشروع', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== إدارة الفيديوهات (إضافة) =====
@app.route('/admin/video/add', methods=['POST'])
def add_video():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    title = request.form.get('video_title')
    description = request.form.get('video_description')
    url = request.form.get('video_url')
    
    if not title or not url:
        flash('العنوان والرابط مطلوبان', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_video = Video(title=title, description=description, url=url)
    db.session.add(new_video)
    db.session.commit()
    flash('تمت إضافة الفيديو بنجاح', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== إدارة الفيديوهات (حذف) =====
@app.route('/admin/video/delete/<int:id>')
def delete_video(id):
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    item = Video.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('تم حذف الفيديو', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== إدارة الآراء (إضافة) =====
@app.route('/admin/testimonial/add', methods=['POST'])
def add_testimonial():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    name = request.form.get('client_name')
    role = request.form.get('client_role')
    text = request.form.get('client_text')
    
    if not name or not text:
        flash('الاسم والنص مطلوبان', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_testimonial = Testimonial(name=name, role=role, text=text)
    db.session.add(new_testimonial)
    db.session.commit()
    flash('تمت إضافة الرأي بنجاح', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== إدارة الآراء (حذف) =====
@app.route('/admin/testimonial/delete/<int:id>')
def delete_testimonial(id):
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    item = Testimonial.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('تم حذف الرأي', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== تحديث الإعدادات (النص التعريفي والصورة) =====
@app.route('/admin/settings/update', methods=['POST'])
def update_settings():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    bio_text = request.form.get('bio_text')
    profile_image = request.files.get('profile_image')
    
    if bio_text:
        setting = Setting.query.filter_by(key='bio_text').first()
        if setting:
            setting.value = bio_text
        else:
            setting = Setting(key='bio_text', value=bio_text)
            db.session.add(setting)
    
    if profile_image and profile_image.filename:
        image_path = upload_to_supabase(profile_image)
        setting = Setting.query.filter_by(key='profile_image').first()
        if setting:
            setting.value = image_path
        else:
            setting = Setting(key='profile_image', value=image_path)
            db.session.add(setting)
    
    db.session.commit()
    flash('تم تحديث الإعدادات', 'success')
    return redirect(url_for('admin_dashboard'))

# ===== نقطة الدخول للتشغيل المحلي =====
if __name__ == '__main__':
    app.run(debug=True)