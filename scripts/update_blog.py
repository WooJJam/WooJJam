import feedparser
import re
from datetime import datetime
from html import unescape
import json

def fetch_tistory_posts(blog_url, max_posts=5):
    """티스토리 RSS 피드에서 최근 게시글 가져오기"""
    rss_url = f"{blog_url.rstrip('/')}/rss"
    
    try:
        print(f"📡 RSS 피드 가져오는 중: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print("❌ RSS 피드에 게시글이 없습니다.")
            return []
        
        posts = []
        for entry in feed.entries[:max_posts]:
            # HTML 태그 제거
            summary = unescape(re.sub('<[^<]+?>', '', entry.get('summary', '')))
            summary = summary.strip()[:100] + '...' if len(summary) > 100 else summary
            
            # 카테고리 추출
            categories = [tag.term for tag in entry.get('tags', [])]
            
            post = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
                'summary': summary,
                'categories': categories
            }
            posts.append(post)
        
        print(f"✅ {len(posts)}개의 게시글을 찾았습니다.")
        return posts
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []

def parse_date(date_str):
    """날짜 파싱 및 포맷팅"""
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z'
    ]
    
    for fmt in formats:
        try:
            date = datetime.strptime(date_str, fmt)
            return date.strftime('%Y.%m.%d')
        except:
            continue
    
    return date_str[:10] if date_str else ''

def generate_list_style(posts):
    """리스트 스타일 마크다운"""
    markdown = "## 📝 Latest Blog Posts\n\n"
    
    for i, post in enumerate(posts, 1):
        date_str = parse_date(post['published'])
        categories = ' · '.join([f'`{cat}`' for cat in post['categories'][:3]]) if post['categories'] else ''
        
        markdown += f"### {i}. [{post['title']}]({post['link']})\n\n"
        markdown += f"> {post['summary']}\n\n"
        markdown += f"📅 {date_str}"
        
        if categories:
            markdown += f" | 🏷️ {categories}"
        
        markdown += "\n\n---\n\n"
    
    return markdown

def generate_table_style(posts):
    """테이블 스타일 마크다운"""
    markdown = "## 📖 Latest Blog Posts\n\n"
    markdown += "| 📌 | Title | Date | Tags |\n"
    markdown += "|:--:|:------|:----:|:-----|\n"
    
    for i, post in enumerate(posts, 1):
        date_str = parse_date(post['published'])
        categories = ', '.join([f'`{cat}`' for cat in post['categories'][:2]]) if post['categories'] else '-'
        title_link = f"[{post['title']}]({post['link']})"
        
        markdown += f"| {i} | {title_link} | {date_str} | {categories} |\n"
    
    markdown += "\n"
    return markdown

def generate_card_style(posts):
    """카드 스타일 마크다운"""
    markdown = "## 📚 Latest Blog Posts\n\n"
    
    for i, post in enumerate(posts):
        date_str = parse_date(post['published'])
        categories = ' · '.join(post['categories'][:3]) if post['categories'] else ''
        
        # 배경색 번갈아가며
        bg_emoji = "🔵" if i % 2 == 0 else "🟣"
        
        markdown += f"{bg_emoji} **[{post['title']}]({post['link']})**\n\n"
        markdown += f"   {post['summary']}\n\n"
        markdown += f"   📅 {date_str}"
        
        if categories:
            markdown += f" | 🏷️ {categories}"
        
        markdown += "\n\n"
    
    return markdown

def generate_minimal_style(posts):
    """미니멀 스타일 마크다운"""
    markdown = "## ✍️ Recent Posts\n\n"
    
    for post in posts:
        date_str = parse_date(post['published'])
        markdown += f"- **[{post['title']}]({post['link']})** · `{date_str}`\n"
    
    markdown += "\n"
    return markdown

def generate_badge_style(posts):
    """뱃지 스타일 마크다운"""
    markdown = "## 📝 Latest Blog Posts\n\n"
    markdown += '<p align="center">\n\n'
    
    for post in posts:
        date_str = parse_date(post['published'])
        # 제목을 URL 인코딩 형식으로 변환
        title_encoded = post['title'].replace(' ', '%20').replace('-', '--')
        
        markdown += f'[![Blog Post]'
        markdown += f'(https://img.shields.io/badge/{title_encoded[:40]}-20C997?style=for-the-badge&logo=Tistory&logoColor=white)]'
        markdown += f'({post["link"]})\n\n'
    
    markdown += '</p>\n\n'
    return markdown

def update_readme(markdown_content, readme_path='README.md'):
    """README 파일 업데이트"""
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()
        
        print(f"📄 README.md 파일을 읽었습니다.")
    except FileNotFoundError:
        print("❌ README.md 파일을 찾을 수 없습니다.")
        return False
    
    start_marker = "<!-- BLOG-POST-LIST:START -->"
    end_marker = "<!-- BLOG-POST-LIST:END -->"
    
    if start_marker not in readme or end_marker not in readme:
        print(f"❌ README.md에 마커가 없습니다.")
        print(f"다음 마커를 추가해주세요:\n{start_marker}\n{end_marker}")
        return False
    
    # 정규표현식으로 마커 사이 내용 교체
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    new_content = f"{start_marker}\n{markdown_content}{end_marker}"
    updated_readme = re.sub(pattern, new_content, readme, flags=re.DOTALL)
    
    # 파일 저장
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_readme)
    
    print("✅ README.md 업데이트 완료!")
    return True

def main():
    # ========== 설정 ==========
    BLOG_URL = "https://woojjam.tistory.com"  # 티스토리 블로그 URL
    MAX_POSTS = 5  # 표시할 게시글 수
    STYLE = 'table'  # 스타일: list, table, card, minimal, badge
    # =========================
    
    print("=" * 60)
    print("🚀 티스토리 블로그 게시글 자동 업데이트")
    print("=" * 60)
    print(f"📍 블로그: {BLOG_URL}")
    print(f"📊 스타일: {STYLE}")
    print(f"📝 게시글 수: {MAX_POSTS}")
    print("=" * 60)
    
    # 게시글 가져오기
    posts = fetch_tistory_posts(BLOG_URL, MAX_POSTS)
    
    if not posts:
        print("\n❌ 게시글을 가져올 수 없습니다.")
        print("블로그 URL과 RSS 피드 설정을 확인해주세요.")
        return False
    
    # 게시글 목록 출력
    print("\n📋 가져온 게시글:")
    for i, post in enumerate(posts, 1):
        print(f"  {i}. {post['title']}")
    
    # 스타일에 따른 마크다운 생성
    print(f"\n🎨 '{STYLE}' 스타일로 마크다운 생성 중...")
    
    if STYLE == 'table':
        markdown = generate_table_style(posts)
    elif STYLE == 'card':
        markdown = generate_card_style(posts)
    elif STYLE == 'minimal':
        markdown = generate_minimal_style(posts)
    elif STYLE == 'badge':
        markdown = generate_badge_style(posts)
    else:  # list (기본)
        markdown = generate_list_style(posts)
    
    # README 업데이트
    print("\n📝 README.md 업데이트 중...")
    success = update_readme(markdown)
    
    print("\n" + "=" * 60)
    if success:
        print("✨ 성공적으로 완료되었습니다!")
    else:
        print("❌ 업데이트에 실패했습니다.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
