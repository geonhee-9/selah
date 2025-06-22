from PIL import Image, ImageDraw, ImageFont
import os

def create_church_image(filename, church_name, color):
    # 800x600 크기의 이미지 생성
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # 교회 이름 텍스트 추가
    try:
        # 기본 폰트 사용
        font = ImageFont.load_default()
    except:
        font = None
    
    # 텍스트 크기 계산
    text = church_name
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 20
        text_height = 30
    
    # 텍스트를 중앙에 배치
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 텍스트 그리기
    draw.text((x, y), text, fill='white', font=font)
    
    # static 폴더가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # 이미지 저장
    image.save(f'static/{filename}')
    print(f'✅ {filename} 생성 완료')

def main():
    # 교회별 이미지 생성
    churches = [
        ('church1.jpg', '관악교회', '#667eea'),
        ('church2.jpg', '봉천교회', '#764ba2'),
        ('church3.jpg', '신림교회', '#667eea'),
        ('church4.jpg', '동작교회', '#764ba2'),
        ('church5.jpg', '상도교회', '#667eea'),
        ('church6.jpg', '흑석교회', '#764ba2'),
        ('church7.jpg', '노원교회', '#667eea'),
        ('church8.jpg', '월계교회', '#764ba2'),
        ('church9.jpg', '공릉교회', '#667eea'),
        ('church10.jpg', '대전중앙교회', '#764ba2'),
        ('church11.jpg', '유성교회', '#667eea'),
        ('church12.jpg', '서구교회', '#764ba2')
    ]
    
    print('교회 이미지 생성을 시작합니다...')
    
    for filename, church_name, color in churches:
        create_church_image(filename, church_name, color)
    
    print(f'\n이미지 생성 완료: {len(churches)} 개 파일')

if __name__ == '__main__':
    main() 