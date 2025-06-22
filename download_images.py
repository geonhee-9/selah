import requests
import os

# 교회 이미지 URL 목록
church_images = [
    {
        'filename': 'church1.jpg',
        'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church2.jpg',
        'url': 'https://images.unsplash.com/photo-1542810634-71277d95dcbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church3.jpg',
        'url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church4.jpg',
        'url': 'https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church5.jpg',
        'url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church6.jpg',
        'url': 'https://images.unsplash.com/photo-1542810634-71277d95dcbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church7.jpg',
        'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church8.jpg',
        'url': 'https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church9.jpg',
        'url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church10.jpg',
        'url': 'https://images.unsplash.com/photo-1542810634-71277d95dcbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church11.jpg',
        'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    },
    {
        'filename': 'church12.jpg',
        'url': 'https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    }
]

def download_image(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(f'static/{filename}', 'wb') as f:
            f.write(response.content)
        print(f'✅ {filename} 다운로드 완료')
        return True
    except Exception as e:
        print(f'❌ {filename} 다운로드 실패: {e}')
        return False

def main():
    # static 폴더가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print('교회 이미지 다운로드를 시작합니다...')
    
    success_count = 0
    for image in church_images:
        if download_image(image['url'], image['filename']):
            success_count += 1
    
    print(f'\n다운로드 완료: {success_count}/{len(church_images)} 개 파일')

if __name__ == '__main__':
    main() 