from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

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
            ('관악교회', '서울시 관악구 관악로 123', '관악구 중심에 위치한 현대적인 교회입니다. 음악 연습에 최적화된 공간을 제공합니다.', 15, 10000, 'church1', '02-1234-5678', 'gwanak@church.com', '음향시설, 악기보관함, 주차장, 휴게공간', '서울 관악구', '드럼세트, 베이스앰프, 기타앰프, 마이크'),
            ('봉천교회', '서울시 관악구 봉천로 456', '봉천동에 위치한 따뜻한 분위기의 교회입니다. 조용한 연습 환경을 제공합니다.', 8, 5000, 'church2', '02-2345-6789', 'bongcheon@church.com', '음향시설, 연습실, 휴게공간, 주차장', '서울 관악구', '피아노, 앰프, 마이크, 건반'),
            ('신림교회', '서울시 관악구 신림로 789', '신림동의 중심에 위치한 교회입니다. 다양한 악기 연습이 가능합니다.', 20, 15000, 'church3', '02-3456-7890', 'sinrim@church.com', '음향시설, 다목적실, 주차장, 녹음실', '서울 관악구', '드럼세트, 베이스앰프, 건반, 현악기'),
            
            # 서울 동작구
            ('동작교회', '서울시 동작구 동작대로 321', '동작구에 위치한 현대적인 교회입니다. 최신 음향장비를 구비했습니다.', 12, 10000, 'church4', '02-4567-8901', 'dongjak@church.com', '음향시설, 연습실, 주차장, 휴게공간', '서울 동작구', '드럼세트, 기타, 베이스, 건반, 마이크'),
            ('상도교회', '서울시 동작구 상도로 654', '상도동에 위치한 평화로운 교회입니다. 소규모 밴드 연습에 최적입니다.', 6, 5000, 'church5', '02-5678-9012', 'sangdo@church.com', '음향시설, 연습실, 주차장', '서울 동작구', '피아노, 앰프, 마이크, 건반'),
            ('흑석교회', '서울시 동작구 흑석로 987', '흑석동에 위치한 친근한 분위기의 교회입니다. 조용한 환경에서 연습할 수 있습니다.', 10, 10000, 'church6', '02-6789-0123', 'heukseok@church.com', '음향시설, 연습실, 주차장', '서울 동작구', '드럼세트, 기타앰프, 베이스앰프, 마이크'),
            
            # 서울 노원구
            ('노원교회', '서울시 노원구 노원로 147', '노원구 중심에 위치한 교회입니다. 대규모 밴드 연습에 적합합니다.', 25, 15000, 'church7', '02-7890-1234', 'nowon@church.com', '음향시설, 다목적실, 주차장, 녹음실', '서울 노원구', '드럼세트, 베이스앰프, 건반, 현악기, 마이크'),
            ('월계교회', '서울시 노원구 월계로 258', '월계동에 위치한 전통과 현대가 조화로운 교회입니다. 클래식 연주에 적합합니다.', 18, 15000, 'church8', '02-8901-2345', 'wolgye@church.com', '음향시설, 오르간, 연습실, 주차장', '서울 노원구', '오르간, 피아노, 현악기, 마이크'),
            ('공릉교회', '서울시 노원구 공릉로 369', '공릉동에 위치한 미래지향적인 교회입니다. 다양한 악기 연습이 가능합니다.', 15, 10000, 'church9', '02-9012-3456', 'gongneung@church.com', '음향시설, 연습실, 주차장, 휴게공간', '서울 노원구', '드럼세트, 기타, 베이스, 건반, 마이크'),
            
            # 대전
            ('대전중앙교회', '대전시 중구 중앙로 741', '대전 중구에 위치한 현대적인 교회입니다. 최신 음향장비를 구비했습니다.', 20, 10000, 'church10', '042-1234-5678', 'daejeon@church.com', '음향시설, 다목적실, 주차장, 녹음실', '대전', '드럼세트, 베이스앰프, 기타앰프, 마이크'),
            ('유성교회', '대전시 유성구 유성로 852', '유성구에 위치한 평화로운 교회입니다. 소규모 밴드 연습에 최적입니다.', 8, 5000, 'church11', '042-2345-6789', 'yuseong@church.com', '음향시설, 연습실, 주차장', '대전', '피아노, 앰프, 마이크, 건반'),
            ('서구교회', '대전시 서구 서구로 963', '서구에 위치한 친근한 분위기의 교회입니다. 조용한 환경에서 연습할 수 있습니다.', 12, 10000, 'church12', '042-3456-7890', 'seogu@church.com', '음향시설, 연습실, 주차장, 휴게공간', '대전', '드럼세트, 기타앰프, 베이스앰프, 마이크')
        ]
        cursor.executemany('INSERT INTO churches (name, address, description, capacity, hourly_rate, image_url, contact_phone, contact_email, facilities, location_tag, equipment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_churches)
    
    # 관리자 계정 생성
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)', ('admin', 'admin@selah.com', 'admin123', 1))
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # 필터 파라미터 가져오기
    location_filter = request.args.get('location', '')
    capacity_filter = request.args.get('capacity', '')
    
    # 기본 쿼리
    query = 'SELECT * FROM churches'
    params = []
    
    # 필터 적용
    if location_filter:
        query += ' WHERE location_tag = ?'
        params.append(location_filter)
    
    if capacity_filter:
        if location_filter:
            query += ' AND capacity <= ?'
        else:
            query += ' WHERE capacity <= ?'
        params.append(int(capacity_filter))
    
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
                         selected_location=location_filter, selected_capacity=capacity_filter)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            flash('로그인되었습니다!')
            return redirect(url_for('dashboard'))
        else:
            flash('잘못된 사용자명 또는 비밀번호입니다.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
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
    
    if session.get('is_admin'):
        cursor.execute('''
            SELECT b.*, c.name as church_name, u.username
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
        booking_list.append({
            'id': booking[0],
            'church_name': booking[8] if session.get('is_admin') else booking[8],
            'date': booking[3],
            'start_time': booking[4],
            'end_time': booking[5],
            'purpose': booking[6],
            'member_count': booking[7],
            'payment_method': booking[8] if len(booking) > 8 else None,
            'status': booking[9] if len(booking) > 9 else booking[8],
            'username': booking[10] if session.get('is_admin') and len(booking) > 10 else None
        })
    
    return render_template('dashboard.html', bookings=booking_list, is_admin=session.get('is_admin'))

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
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_type = "band"')
    total_bands = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM churches')
    total_churches = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT c.name, COUNT(b.id) as booking_count
        FROM churches c
        LEFT JOIN bookings b ON c.id = b.church_id
        GROUP BY c.id, c.name
        ORDER BY booking_count DESC
        LIMIT 5
    ''')
    popular_churches = cursor.fetchall()
    
    cursor.execute('''
        SELECT AVG(CAST((julianday(b.end_time) - julianday(b.start_time)) * 24 AS REAL)) as avg_hours
        FROM bookings b
        WHERE b.date >= date("now", "-30 days")
    ''')
    avg_hours_result = cursor.fetchone()
    avg_hours = avg_hours_result[0] if avg_hours_result[0] else 0
    
    conn.close()
    
    stats = {
        'weekly_bookings': weekly_bookings,
        'total_bands': total_bands,
        'total_churches': total_churches,
        'avg_hours': round(avg_hours, 1),
        'popular_churches': popular_churches
    }
    
    return render_template('admin.html', stats=stats)

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=False)
