from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def get_user_type_display(user_type):
    """회원 유형을 한글로 표시합니다."""
    user_type_map = {
        'band': '밴드',
        'individual': '개인연주자',
        'teacher': '강사',
        'other': '기타'
    }
    return user_type_map.get(user_type, user_type)

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # 교회 테이블 생성 (음악 연습 공간 정보 추가)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS churches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            description TEXT,
            capacity INTEGER,
            hourly_rate REAL,
            image_url TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            facilities TEXT,
            location_tag TEXT,
            equipment TEXT
        )
    ''')
    
    # 사용자 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            user_type TEXT DEFAULT 'band'
        )
    ''')
    
    # 예약 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            church_id INTEGER,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            purpose TEXT,
            member_count INTEGER,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (church_id) REFERENCES churches (id)
        )
    ''')
    
    # 샘플 데이터 삽입 (다양한 지역과 수용인원으로 업데이트)
    cursor.execute('SELECT COUNT(*) FROM churches')
    if cursor.fetchone()[0] == 0:
        sample_churches = [
            # 서울 관악구
            ('관악교회', '서울시 관악구 관악로 123', '관악구 중심에 위치한 현대적인 교회입니다. 음악 연습에 최적화된 공간을 제공합니다.', 15, 10000, 'church1', '02-1234-5678', 'gwanak@church.com', '음향시설, 악기보관함, 주차장, 휴게공간', '서울 관악구', '드럼세트, 베이스앰프, 기타앰프, 마이크, PA시스템, 믹서'),
            ('봉천교회', '서울시 관악구 봉천로 456', '봉천동에 위치한 따뜻한 분위기의 교회입니다. 조용한 연습 환경을 제공합니다.', 8, 5000, 'church2', '02-2345-6789', 'bongcheon@church.com', '음향시설, 연습실, 휴게공간, 주차장', '서울 관악구', '피아노, 앰프, 마이크, 키보드, 베이스'),
            ('신림교회', '서울시 관악구 신림로 789', '신림동의 중심에 위치한 교회입니다. 다양한 악기 연습이 가능합니다.', 20, 15000, 'church3', '02-3456-7890', 'sinrim@church.com', '음향시설, 다목적실, 주차장, 녹음실', '서울 관악구', '드럼세트, 베이스앰프, 키보드, 현악기, 마이크, 이펙터'),
            
            # 서울 동작구
            ('동작교회', '서울시 동작구 동작대로 321', '동작구에 위치한 현대적인 교회입니다. 최신 음향장비를 구비했습니다.', 12, 10000, 'church4', '02-4567-8901', 'dongjak@church.com', '음향시설, 연습실, 주차장, 휴게공간', '서울 동작구', '드럼세트, 기타, 베이스, 키보드, 마이크, PA시스템'),
            ('상도교회', '서울시 동작구 상도로 654', '상도동에 위치한 평화로운 교회입니다. 소규모 밴드 연습에 최적입니다.', 6, 5000, 'church5', '02-5678-9012', 'sangdo@church.com', '음향시설, 연습실, 주차장', '서울 동작구', '피아노, 앰프, 마이크, 키보드, 베이스'),
            ('흑석교회', '서울시 동작구 흑석로 987', '흑석동에 위치한 친근한 분위기의 교회입니다. 조용한 환경에서 연습할 수 있습니다.', 10, 10000, 'church6', '02-6789-0123', 'heukseok@church.com', '음향시설, 연습실, 주차장', '서울 동작구', '드럼세트, 기타앰프, 베이스앰프, 마이크, 믹서'),
            
            # 서울 노원구
            ('노원교회', '서울시 노원구 노원로 147', '노원구 중심에 위치한 교회입니다. 대규모 밴드 연습에 적합합니다.', 25, 15000, 'church7', '02-7890-1234', 'nowon@church.com', '음향시설, 다목적실, 주차장, 녹음실', '서울 노원구', '드럼세트, 베이스앰프, 키보드, 현악기, 마이크, PA시스템, 이펙터'),
            ('월계교회', '서울시 노원구 월계로 258', '월계동에 위치한 전통과 현대가 조화로운 교회입니다. 클래식 연주에 적합합니다.', 18, 15000, 'church8', '02-8901-2345', 'wolgye@church.com', '음향시설, 오르간, 연습실, 주차장', '서울 노원구', '오르간, 피아노, 현악기, 마이크, 키보드'),
            ('공릉교회', '서울시 노원구 공릉로 369', '공릉동에 위치한 미래지향적인 교회입니다. 다양한 악기 연습이 가능합니다.', 15, 10000, 'church9', '02-9012-3456', 'gongneung@church.com', '음향시설, 연습실, 주차장, 휴게공간', '서울 노원구', '드럼세트, 기타, 베이스, 키보드, 마이크, 믹서'),
            
            # 대전
            ('대전중앙교회', '대전시 중구 중앙로 741', '대전 중구에 위치한 현대적인 교회입니다. 최신 음향장비를 구비했습니다.', 20, 10000, 'church10', '042-1234-5678', 'daejeon@church.com', '음향시설, 다목적실, 주차장, 녹음실', '대전', '드럼세트, 베이스앰프, 기타앰프, 마이크, PA시스템, 이펙터'),
            ('유성교회', '대전시 유성구 유성로 852', '유성구에 위치한 평화로운 교회입니다. 소규모 밴드 연습에 최적입니다.', 8, 5000, 'church11', '042-2345-6789', 'yuseong@church.com', '음향시설, 연습실, 주차장', '대전', '피아노, 앰프, 마이크, 키보드, 베이스'),
            ('서구교회', '대전시 서구 서구로 963', '서구에 위치한 친근한 분위기의 교회입니다. 조용한 환경에서 연습할 수 있습니다.', 12, 10000, 'church12', '042-3456-7890', 'seogu@church.com', '음향시설, 연습실, 주차장, 휴게공간', '대전', '드럼세트, 기타앰프, 베이스앰프, 마이크, 믹서')
        ]
        cursor.executemany('INSERT INTO churches (name, address, description, capacity, hourly_rate, image_url, contact_phone, contact_email, facilities, location_tag, equipment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_churches)
    
    # 관리자 계정 생성
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)', ('admin', 'admin', 'admin123', 1))
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # 필터 파라미터 가져오기
    location_filter = request.args.get('location', '')
    capacity_filter = request.args.get('capacity', '')
    equipment_filter = request.args.getlist('equipment')
    
    # 기본 쿼리
    query = 'SELECT * FROM churches'
    params = []
    conditions = []
    
    # 필터 적용
    if location_filter:
        conditions.append('location_tag = ?')
        params.append(location_filter)
    
    if capacity_filter:
        conditions.append('capacity <= ?')
        params.append(int(capacity_filter))
    
    # 여러 장비가 모두 포함된 교회만 검색
    for eq in equipment_filter:
        conditions.append('equipment LIKE ?')
        params.append(f'%{eq}%')
    
    # 조건이 있으면 WHERE 절 추가
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    cursor.execute(query, params)
    churches = cursor.fetchall()
    
    # 위치 태그 목록 가져오기 (고정된 옵션)
    locations = ['서울 관악구', '서울 동작구', '서울 노원구', '대전']
    
    conn.close()
    
    church_list = []
    for church in churches:
        church_list.append({
            'id': church[0],
            'name': church[1],
            'address': church[2],
            'description': church[3],
            'capacity': church[4],
            'hourly_rate': church[5],
            'image_url': church[6],
            'facilities': church[9],
            'location_tag': church[10],
            'equipment': church[11]
        })
    
    return render_template('home.html', churches=church_list, locations=locations, 
                         selected_location=location_filter, selected_capacity=capacity_filter,
                         selected_equipment=equipment_filter)

@app.route('/church/<int:church_id>')
def church_detail(church_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM churches WHERE id = ?', (church_id,))
    church_data = cursor.fetchone()
    conn.close()
    
    if church_data:
        church = {
            'id': church_data[0],
            'name': church_data[1],
            'address': church_data[2],
            'description': church_data[3],
            'capacity': church_data[4],
            'hourly_rate': church_data[5],
            'image_url': church_data[6],
            'contact_phone': church_data[7],
            'contact_email': church_data[8],
            'facilities': church_data[9],
            'location_tag': church_data[10],
            'equipment': church_data[11]
        }
        return render_template('church_detail.html', church=church)
    else:
        flash('교회를 찾을 수 없습니다.')
        return redirect(url_for('home'))

@app.route('/book/<int:church_id>', methods=['GET', 'POST'])
def book_church(church_id):
    if 'user_id' not in session:
        flash('예약하려면 로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        purpose = request.form['purpose']
        member_count = request.form['member_count']
        payment_method = request.form['payment_method']
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # 중복 예약 확인
        cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE church_id = ? AND date = ? 
            AND status != 'cancelled'
            AND (
                (start_time <= ? AND end_time > ?) OR
                (start_time < ? AND end_time >= ?) OR
                (start_time >= ? AND end_time <= ?)
            )
        ''', (church_id, date, start_time, start_time, end_time, end_time, start_time, end_time))
        
        conflict_count = cursor.fetchone()[0]
        
        if conflict_count > 0:
            conn.close()
            flash('해당 시간대에 이미 예약이 있습니다. 다른 시간을 선택해주세요.')
            return redirect(url_for('book_church', church_id=church_id))
        
        # 예약 생성
        cursor.execute('''
            INSERT INTO bookings (user_id, church_id, date, start_time, end_time, purpose, member_count, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], church_id, date, start_time, end_time, purpose, member_count, payment_method))
        conn.commit()
        conn.close()
        
        flash('예약이 성공적으로 완료되었습니다!')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM churches WHERE id = ?', (church_id,))
    church_data = cursor.fetchone()
    conn.close()
    
    church = {
        'id': church_data[0],
        'name': church_data[1],
        'hourly_rate': church_data[5]
    }
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('booking.html', church=church, today=today)

@app.route('/api/bookings/<int:church_id>/<date>')
def get_bookings_for_date(church_id, date):
    """특정 교회의 특정 날짜 예약 정보를 가져옵니다."""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT start_time, end_time, status
        FROM bookings 
        WHERE church_id = ? AND date = ?
        ORDER BY start_time
    ''', (church_id, date))
    
    bookings = cursor.fetchall()
    conn.close()
    
    booking_times = []
    for booking in bookings:
        booking_times.append({
            'start_time': booking[0],
            'end_time': booking[1],
            'status': booking[2]
        })
    
    return jsonify(booking_times)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]  # username은 여전히 세션에 저장 (표시용)
            session['email'] = user[2]     # email도 세션에 저장
            session['is_admin'] = user[4]
            flash('로그인되었습니다!')
            return redirect(url_for('dashboard'))
        else:
            flash('잘못된 이메일 또는 비밀번호입니다.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        other_type_text = request.form.get('other_type_text', '')
        
        # 기타 선택 시 입력된 텍스트를 user_type으로 사용
        if user_type == 'other' and other_type_text:
            user_type = other_type_text
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, email, password, user_type) VALUES (?, ?, ?, ?)', (username, email, password, user_type))
            conn.commit()
            flash('회원가입이 완료되었습니다! 로그인해주세요.')
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('이미 존재하는 사용자명 또는 이메일입니다.')
            conn.close()
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # 내 정보 쿼리
    cursor.execute('SELECT username, email, user_type FROM users WHERE id = ?', (session['user_id'],))
    user_row = cursor.fetchone()
    user_info = None
    if user_row:
        user_info = {
            'username': user_row[0],
            'email': user_row[1],
            'user_type': get_user_type_display(user_row[2])
        }
    
    if session.get('is_admin'):
        cursor.execute('''
            SELECT b.*, c.name as church_name, u.email
            FROM bookings b
            JOIN churches c ON b.church_id = c.id
            JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC
        ''')
    else:
        cursor.execute('''
            SELECT b.*, c.name as church_name
            FROM bookings b
            JOIN churches c ON b.church_id = c.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        ''', (session['user_id'],))
    
    bookings = cursor.fetchall()
    conn.close()
    
    booking_list = []
    for booking in bookings:
        if session.get('is_admin'):
            church_name = booking[11]
            user_email = booking[12] if len(booking) > 12 else None
        else:
            church_name = booking[-1]
            user_email = None
        booking_list.append({
            'id': booking[0],
            'church_name': church_name,
            'date': booking[3],
            'start_time': booking[4],
            'end_time': booking[5],
            'purpose': booking[6],
            'member_count': booking[7],
            'payment_method': booking[8],
            'status': booking[9],
            'user_email': user_email
        })
    
    return render_template('dashboard.html', bookings=booking_list, is_admin=session.get('is_admin'), user_info=user_info)

@app.route('/dashboard/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    username = request.form['username']
    email = request.form['email']
    user_type = request.form['user_type']
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET username=?, email=?, user_type=? WHERE id=?', (username, email, user_type, session['user_id']))
    conn.commit()
    conn.close()
    # 세션 정보도 갱신
    session['username'] = username
    session['email'] = email
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # 통계 데이터 수집
    cursor.execute('SELECT COUNT(*) FROM bookings WHERE date >= date("now", "-7 days")')
    weekly_bookings = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_type != "admin" AND is_admin = 0')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM churches')
    total_churches = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT AVG(CAST((julianday(b.end_time) - julianday(b.start_time)) * 24 AS REAL)) as avg_hours
        FROM bookings b
        WHERE b.date >= date("now", "-30 days")
    ''')
    avg_hours_result = cursor.fetchone()
    avg_hours = avg_hours_result[0] if avg_hours_result[0] else 0
    
    # 월별 예약 추이
    cursor.execute('''
        SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
        FROM bookings
        WHERE date >= date("now", "-6 months")
        GROUP BY month
        ORDER BY month
    ''')
    monthly_bookings = cursor.fetchall()
    
    # 월 예상 수익 계산
    cursor.execute('''
        SELECT SUM(c.hourly_rate * CAST((julianday(b.end_time) - julianday(b.start_time)) * 24 AS REAL)) / 10000
        FROM bookings b
        JOIN churches c ON b.church_id = c.id
        WHERE b.date >= date("now", "-30 days")
    ''')
    monthly_revenue_result = cursor.fetchone()
    monthly_revenue = round(monthly_revenue_result[0], 1) if monthly_revenue_result[0] else 0
    
    # 활성 사용자 수 (최근 30일 내 예약한 사용자)
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) FROM bookings 
        WHERE date >= date("now", "-30 days")
    ''')
    active_users = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT c.name, COUNT(b.id) as booking_count
        FROM churches c
        LEFT JOIN bookings b ON c.id = b.church_id
        GROUP BY c.id, c.name
        ORDER BY booking_count DESC
        LIMIT 5
    ''')
    popular_churches = cursor.fetchall()
    
    # 교회 목록 (예약 횟수 포함)
    cursor.execute('''
        SELECT c.*, COUNT(b.id) as booking_count
        FROM churches c
        LEFT JOIN bookings b ON c.id = b.church_id
        GROUP BY c.id
        ORDER BY c.name
    ''')
    churches_data = cursor.fetchall()
    
    churches = []
    for church in churches_data:
        churches.append({
            'id': church[0],
            'name': church[1],
            'address': church[2],
            'description': church[3],
            'capacity': church[4],
            'hourly_rate': church[5],
            'image_url': church[6],
            'contact_phone': church[7],
            'contact_email': church[8],
            'facilities': church[9],
            'location_tag': church[10],
            'equipment': church[11],
            'booking_count': church[12]
        })
    
    # 전체 예약 목록
    cursor.execute('''
        SELECT b.*, c.name as church_name, u.email
        FROM bookings b
        JOIN churches c ON b.church_id = c.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
    ''')
    all_bookings_data = cursor.fetchall()
    
    all_bookings = []
    for booking in all_bookings_data:
        all_bookings.append({
            'id': booking[0],
            'user_id': booking[1],
            'church_id': booking[2],
            'date': booking[3],
            'start_time': booking[4],
            'end_time': booking[5],
            'purpose': booking[6],
            'member_count': booking[7],
            'payment_method': booking[8],
            'status': booking[9],
            'church_name': booking[11],
            'user_email': booking[12]
        })
    
    # 사용자 목록 (예약 횟수 포함)
    cursor.execute('''
        SELECT u.*, COUNT(b.id) as booking_count
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id
        ORDER BY u.username
    ''')
    users_data = cursor.fetchall()
    
    users = []
    for user in users_data:
        users.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'user_type': get_user_type_display(user[5]),
            'created_at': user[6] if len(user) > 6 else 'N/A',
            'booking_count': user[7] if len(user) > 7 else 0
        })
    
    conn.close()
    
    stats = {
        'weekly_bookings': weekly_bookings,
        'total_users': total_users,
        'total_churches': total_churches,
        'avg_hours': round(avg_hours, 1),
        'monthly_revenue': monthly_revenue,
        'active_users': active_users,
        'popular_churches': popular_churches,
        'monthly_bookings': monthly_bookings
    }
    
    return render_template('admin.html', stats=stats, churches=churches, all_bookings=all_bookings, users=users)

@app.route('/admin/church/add', methods=['POST'])
def add_church():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        description = request.form['description']
        capacity = request.form['capacity']
        hourly_rate = request.form['hourly_rate']
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        location_tag = request.form['location_tag']
        image_url = request.form['image_url']
        facilities = request.form['facilities']
        equipment = request.form['equipment']
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO churches (name, address, description, capacity, hourly_rate, image_url, contact_phone, contact_email, facilities, location_tag, equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, description, capacity, hourly_rate, image_url, contact_phone, contact_email, facilities, location_tag, equipment))
        conn.commit()
        conn.close()
        
        flash('교회가 성공적으로 추가되었습니다!')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/church/<int:church_id>/delete', methods=['DELETE'])
def delete_church(church_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM churches WHERE id = ?', (church_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/booking/<int:booking_id>/confirm', methods=['POST'])
def confirm_booking(booking_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', ('confirmed', booking_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', ('cancelled', booking_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/user/<int:user_id>/delete', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ? AND is_admin = 0', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
