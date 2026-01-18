import feedparser
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_total_blog_views(blog_url):
    """티스토리 메인에서 전체 조회수 가져오기"""
    try:
        print(f"📊 전체 조회수 가져오는 중: {blog_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        counter = soup.find('li', id='counter')
        if counter:
            total_div = counter.find('div', class_='total')
            if total_div:
                cnt_div = total_div.find('div', class_='cnt')
                if cnt_div:
                    cnt_text = cnt_div.text.strip()
                    total = int(cnt_text.replace(',', ''))
                    print(f"✅ 전체 조회수: {total:,}")
                    return total
        
        print("⚠️  전체 조회수를 찾을 수 없습니다.")
        return None
    
    except Exception as e:
        print(f"❌ 전체 조회수 가져오기 실패: {e}")
        return None

def get_daily_stats(blog_url):
    """티스토리 메인에서 오늘/어제 방문자 수 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stats = {'today': None, 'yesterday': None}
        
        counter = soup.find('li', id='counter')
        if counter:
            today_div = counter.find('div', class_='today')
            if today_div:
                cnt_div = today_div.find('div', class_='cnt')
                if cnt_div:
                    stats['today'] = int(cnt_div.text.strip().replace(',', ''))
            
            yesterday_div = counter.find('div', class_='yesterday')
            if yesterday_div:
                cnt_div = yesterday_div.find('div', class_='cnt')
                if cnt_div:
                    stats['yesterday'] = int(cnt_div.text.strip().replace(',', ''))
        
        if stats['today'] is not None:
            print(f"📅 오늘: {stats['today']:,} | 어제: {stats['yesterday']:,}")
        
        return stats
    
    except Exception as e:
        print(f"❌ 일별 통계 가져오기 실패: {e}")
        return {'today': None, 'yesterday': None}

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
        for i, entry in enumerate(feed.entries[:max_posts], 1):
            print(f"📄 [{i}/{max_posts}] {entry.title}")
            
            post = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
            }
            posts.append(post)
        
        print(f"\n✅ 총 {len(posts)}개의 게시글을 찾았습니다.\n")
        return posts
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []

def parse_date(date_str):
    """날짜 파싱"""
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
    ]
    for fmt in formats:
        try:
            date = datetime.strptime(date_str, fmt)
            return date.strftime('%Y.%m.%d')
        except:
            continue
    return date_str[:10] if date_str else ''

def format_number(num):
    """숫자 포맷팅"""
    if num is None:
        return '-'
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 10000:
        return f"{num//1000}K"
    elif num >= 1000:
        return f"{num:,}"
    else:
        return str(num)

def generate_markdown(posts, total_views=None, daily_stats=None):
    """README용 마크다운 생성"""
    
    # markdown = "## 📚 Latest Blog Posts\n\n"
    markdown = ""
    
    # 통계 정보를 테이블 위에 오른쪽 정렬로 표시
    if total_views is not None or (daily_stats and daily_stats['today'] is not None):
        stats_parts = []
        if daily_stats and daily_stats['today'] is not None:
            stats_parts.append(f"Today: {daily_stats['today']}")
        if daily_stats and daily_stats['yesterday'] is not None:
            stats_parts.append(f"Yesterday: {daily_stats['yesterday']}")
        if total_views is not None:
            stats_parts.append(f"Total: {format_number(total_views)}")
        
        markdown += "<div align='right'>\n\n"
        markdown += " | ".join(stats_parts) + "\n\n"
        markdown += "</div>\n\n"
    
    # HTML 테이블 (가로 꽉 차게)
    markdown += '<table width="100%">\n'
    markdown += '  <thead>\n'
    markdown += '    <tr>\n'
    markdown += '      <th align="left">Title</th>\n'
    markdown += '      <th align="center" width="120">Date</th>\n'
    markdown += '    </tr>\n'
    markdown += '  </thead>\n'
    markdown += '  <tbody>\n'
    
    for post in posts:
        date_str = parse_date(post['published'])
        markdown += '    <tr>\n'
        markdown += f'      <td><a href="{post["link"]}">{post["title"]}</a></td>\n'
        markdown += f'      <td align="center"><code>{date_str}</code></td>\n'
        markdown += '    </tr>\n'
    
    markdown += '  </tbody>\n'
    markdown += '</table>\n\n'
    
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
    
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    new_content = f"{start_marker}\n{markdown_content}{end_marker}"
    updated_readme = re.sub(pattern, new_content, readme, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_readme)
    
    print("✅ README.md 업데이트 완료!")
    return True

def main():
    # ========== 설정 ==========
    BLOG_URL = "https://woojjam.tistory.com"
    MAX_POSTS = 5
    SHOW_DAILY_STATS = True  # 오늘/어제 통계 표시
    # =========================
    
    print("=" * 70)
    print("🚀 티스토리 블로그 게시글 자동 업데이트")
    print("=" * 70)
    print(f"📍 블로그: {BLOG_URL}")
    print(f"📝 게시글 수: {MAX_POSTS}")
    print(f"📊 일별 통계: {'포함' if SHOW_DAILY_STATS else '미포함'}")
    print("=" * 70)
    print()
    
    # 전체 조회수 가져오기
    total_views = get_total_blog_views(BLOG_URL)
    
    # 오늘/어제 통계 가져오기
    daily_stats = None
    if SHOW_DAILY_STATS:
        daily_stats = get_daily_stats(BLOG_URL)
    
    print()
    
    # 게시글 가져오기
    posts = fetch_tistory_posts(BLOG_URL, MAX_POSTS)
    
    if not posts:
        print("\n❌ 게시글을 가져올 수 없습니다.")
        print("   - 블로그 URL이 올바른지 확인해주세요")
        print("   - RSS 피드가 활성화되어 있는지 확인해주세요")
        return False
    
    # 마크다운 생성
    print("🎨 마크다운 생성 중...")
    markdown = generate_markdown(posts, total_views, daily_stats)
    
    # README 업데이트
    print("📝 README.md 업데이트 중...")
    success = update_readme(markdown)
    
    print("\n" + "=" * 70)
    if success:
        print("✨ 성공적으로 완료되었습니다!")
        print("=" * 70)
        print("\n📊 블로그 통계:")
        if total_views:
            print(f"   - 전체 조회수: {total_views:,}")
        if daily_stats and daily_stats['today'] is not None:
            print(f"   - 오늘: {daily_stats['today']:,}")
            print(f"   - 어제: {daily_stats['yesterday']:,}")
        print(f"   - 최근 게시글: {len(posts)}개")
    else:
        print("❌ 업데이트에 실패했습니다.")
        print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
