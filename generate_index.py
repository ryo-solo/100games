#!/usr/bin/env python3
"""
generate_index.py
=================
meta.json を読み込み、100日ゲームチャレンジの index.html を自動生成するスクリプト

使用方法:
    python generate_index.py

※ このスクリプトは 100games リポジトリのルートで実行してください。
   meta.json を更新するだけで index.html が自動的に再生成されます。
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_meta(meta_path):
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_stats(meta):
    start_date = datetime.fromisoformat(meta['challenge']['start_date'])
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    days_passed = (today - start_date).days
    games_made = sum(1 for g in meta['games'] if g['status'] == 'published')
    days_left = max(0, meta['challenge']['total_days'] - days_passed)
    return games_made, days_left


def generate_game_cards(games):
    cards = []
    for game in games:
        if game['status'] == 'coming_soon':
            cards.append(f'''      <div class="game-card soon">
        <div class="card-day">DAY {game["day"]:03d}</div>
        <div class="card-title">{game["title"]}</div>
        <div class="card-desc">{game["description"]}</div>
      </div>''')
        else:
            tags_html = ''.join(
                f'<span class="tag">{t}</span>' for t in game['tags']
            )
            cards.append(f'''      <a class="game-card" href="{game["filename"]}">
        <div class="card-day">DAY {game["day"]:03d}</div>
        <div class="card-title">{game["title"]}</div>
        <div class="card-desc">{game["description"]}</div>
        <div class="card-tags">{tags_html}</div>
        <div class="card-play">&#9654; 今すぐ遊ぶ</div>
      </a>''')
    return '\n'.join(cards)


def generate_html(meta, games_made, days_left):
    c = meta['challenge']
    s = meta['social']
    cards = generate_game_cards(meta['games'])
    twitter_handle = s['twitter'].lstrip('@')

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{c["title"]} | AIが全部作った</title>
  <meta property="og:title" content="AIが全部作った{c["title"]}">
  <meta property="og:description" content="{c["subtitle"]}">
  <meta property="og:url" content="https://ryo-solo.github.io/100games/">
  <meta property="og:image" content="{s["og_image"]}">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:creator" content="{s["twitter"]}">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #080812; min-height: 100vh; font-family: 'Hiragino Kaku Gothic ProN','Noto Sans JP',monospace; color: #fff; }}
    header {{ text-align: center; padding: 60px 20px 40px; border-bottom: 1px solid #1e1e3a; }}
    .header-tag {{ color: #4f46e5; font-size: 12px; letter-spacing: 0.25em; font-weight: 700; margin-bottom: 14px; }}
    header h1 {{ font-size: clamp(24px,5vw,40px); font-weight: 900; margin-bottom: 10px; }}
    header h1 span {{ color: #a78bfa; }}
    header p {{ color: #555; font-size: 13px; line-height: 1.8; }}
    .header-links {{ margin-top: 20px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
    .header-links a {{ padding: 8px 18px; border-radius: 6px; font-size: 12px; font-weight: 700; text-decoration: none; transition: all 0.2s; display: inline-block; }}
    .link-note {{ background: rgba(79,70,229,0.15); border: 1px solid rgba(79,70,229,0.4); color: #a78bfa; }}
    .link-x {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #ccc; }}
    .header-links a:hover {{ opacity: 0.75; transform: translateY(-1px); }}
    .counter {{ display: flex; justify-content: center; gap: 40px; padding: 30px 20px; border-bottom: 1px solid #1e1e3a; }}
    .counter-item {{ text-align: center; }}
    .counter-num {{ font-size: 36px; font-weight: 900; color: #4f46e5; line-height: 1; }}
    .counter-label {{ font-size: 11px; color: #555; margin-top: 4px; letter-spacing: 0.1em; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 40px 20px 80px; }}
    .section-title {{ font-size: 12px; color: #4f46e5; letter-spacing: 0.2em; font-weight: 700; margin-bottom: 24px; }}
    .games-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
    .game-card {{ background: rgba(255,255,255,0.04); border: 1px solid #1e1e3a; border-radius: 14px; padding: 20px; text-decoration: none; color: inherit; transition: all 0.2s; display: block; }}
    .game-card:hover {{ border-color: #4f46e5; background: rgba(79,70,229,0.08); transform: translateY(-3px); box-shadow: 0 8px 30px rgba(79,70,229,0.15); }}
    .card-day {{ font-size: 10px; color: #4f46e5; letter-spacing: 0.15em; font-weight: 700; margin-bottom: 8px; }}
    .card-title {{ font-size: 18px; font-weight: 900; margin-bottom: 6px; }}
    .card-desc {{ font-size: 11px; color: #555; line-height: 1.7; margin-bottom: 14px; }}
    .card-tags {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .tag {{ font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; background: rgba(79,70,229,0.12); border: 1px solid rgba(79,70,229,0.25); color: #818cf8; }}
    .card-play {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 14px; font-size: 11px; font-weight: 700; color: #4f46e5; }}
    .game-card.soon {{ opacity: 0.3; pointer-events: none; cursor: default; }}
    .game-card.soon:hover {{ transform: none; box-shadow: none; }}
    footer {{ text-align: center; padding: 30px; border-top: 1px solid #1e1e3a; color: #333; font-size: 11px; }}
    footer span {{ color: #4f46e5; }}
  </style>
</head>
<body>
  <header>
    <div class="header-tag">100 DAYS CHALLENGE</div>
    <h1><span>AI</span>が全部作った<br>{c["title"]}</h1>
    <p>{c["subtitle"]}</p>
    <div class="header-links">
      <a class="link-note" href="{s["note"]}" target="_blank">&#128221; noteで記録を読む</a>
      <a class="link-x" href="https://x.com/intent/tweet?text=AIが全部作った{c["title"]}%20%23100日ゲームチャレンジ%20%23Claude&url=https%3A%2F%2Fryo-solo.github.io%2F100games%2F" target="_blank">&#120143; シェアする</a>
    </div>
  </header>
  <div class="counter">
    <div class="counter-item"><div class="counter-num" id="gamesMade">{games_made}</div><div class="counter-label">GAMES MADE</div></div>
    <div class="counter-item"><div class="counter-num" id="daysLeft">{days_left}</div><div class="counter-label">DAYS LEFT</div></div>
    <div class="counter-item"><div class="counter-num">100%</div><div class="counter-label">BY AI</div></div>
  </div>
  <main>
    <div class="section-title">GAMES</div>
    <div class="games-grid">
{cards}
    </div>
  </main>
  <footer>Made by <span>AI</span> x りょうすけ — Strategy · Code · Design · All automated</footer>
  <script>
    (function(){{
      // GAMES MADE: .soon以外のgame-cardを動的カウント
      var made = document.querySelectorAll('.game-card:not(.soon)').length;
      document.getElementById('gamesMade').textContent = made;
      // DAYS LEFT: 開始日から動的計算
      var start = new Date('{c["start_date"]}');
      var today = new Date(); today.setHours(0,0,0,0);
      var daysPassed = Math.floor((today - start) / 86400000);
      var left = {meta['challenge']['total_days']} - daysPassed;
      document.getElementById('daysLeft').textContent = left < 0 ? 0 : left;
    }})();
  </script>
</body>
</html>'''


def main():
    script_dir = Path(__file__).parent
    meta_path = script_dir / 'meta.json'
    output_path = script_dir / 'index.html'

    if not meta_path.exists():
        print(f"ERROR: {meta_path} が見つかりません")
        sys.exit(1)

    meta = load_meta(meta_path)
    games_made, days_left = calculate_stats(meta)
    html = generate_html(meta, games_made, days_left)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ index.html を生成しました")
    print(f"   GAMES MADE : {games_made}")
    print(f"   DAYS LEFT  : {days_left}")
    print(f"   出力先     : {output_path}")


if __name__ == '__main__':
    main()