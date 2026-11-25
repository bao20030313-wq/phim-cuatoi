"""
Script tự động lấy phim mới từ KKPhim (phimapi.com)
và tạo file M3U để xem trên TVBox, VLC, Kodi, PickTV...
"""
import requests
import time
from datetime import datetime

BASE_URL = "https://phimapi.com"
PAGES_TO_FETCH = 5   # Số trang phim mới lấy mỗi lần (mỗi trang ~24 phim)
OUTPUT_FILE = "kkphim.m3u"

def get_latest_movies(pages=PAGES_TO_FETCH):
    """Lấy danh sách phim mới cập nhật"""
    movies = []
    for page in range(1, pages + 1):
        try:
            print(f"  Đang lấy trang {page}...")
            r = requests.get(
                f"{BASE_URL}/danh-sach/phim-moi-cap-nhat",
                params={"page": page},
                timeout=30
            )
            data = r.json()
            if data.get("status") and data.get("items"):
                movies.extend(data["items"])
            time.sleep(1)
        except Exception as e:
            print(f"  Lỗi trang {page}: {e}")
    return movies

def get_movie_details(slug):
    """Lấy chi tiết phim + link m3u8 các tập"""
    try:
        r = requests.get(f"{BASE_URL}/phim/{slug}", timeout=30)
        return r.json()
    except Exception as e:
        print(f"  Lỗi lấy chi tiết {slug}: {e}")
        return None

def generate_m3u(movies_data):
    """Tạo nội dung file M3U"""
    lines = ["#EXTM3U"]
    total_eps = 0
    
    for data in movies_data:
        if not data:
            continue
        movie = data.get("movie", {})
        name = movie.get("name", "Không tên")
        poster = movie.get("poster_url", "")
        year = movie.get("year", "")
        
        episodes = data.get("episodes", [])
        if not episodes:
            continue
        
        # Chỉ lấy server đầu tiên (thường là server ổn định nhất)
        server = episodes[0]
        for ep in server.get("server_data", []):
            m3u8 = ep.get("link_m3u8", "")
            if not m3u8:
                continue
            ep_name = ep.get("name", "?")
            display = f"{name} - Tập {ep_name}"
            lines.append(
                f'#EXTINF:-1 tvg-logo="{poster}" '
                f'group-title="KKPhim {year}", {display}'
            )
            lines.append(m3u8)
            total_eps += 1
    
    print(f"  Tổng cộng: {total_eps} tập phim")
    return "\n".join(lines)

def main():
    print(f"[{datetime.now()}] Bắt đầu cập nhật...")
    
    print("1. Lấy danh sách phim mới...")
    movies = get_latest_movies()
    print(f"   Tìm thấy {len(movies)} phim")
    
    print("2. Lấy chi tiết từng phim + link m3u8...")
    all_data = []
    for i, m in enumerate(movies):
        slug = m.get("slug")
        if not slug:
            continue
        if (i + 1) % 10 == 0:
            print(f"   Đã xử lý {i+1}/{len(movies)}")
        details = get_movie_details(slug)
        if details:
            all_data.append(details)
        time.sleep(0.3)  # tránh bị chặn
    
    print("3. Tạo file M3U...")
    m3u = generate_m3u(all_data)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)
    
    print(f"[{datetime.now()}] ✅ Xong! Đã tạo {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
