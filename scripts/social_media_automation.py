"""
social_media_automation.py - SNS投稿自動化スクリプト
個人利用目的のみ

X（旧Twitter）への動画リンク自動投稿テンプレート生成、
シャドウバンされにくいハッシュタグの自動選定、
投稿最適タイミングの提案、露骨なワードの安全表現への変換を行う。
"""

import json
from datetime import datetime, time
from pathlib import Path


# シャドウバンされにくい安全なハッシュタグ候補リスト
# 露骨な表現を避けた汎用・創作系タグを使用
SAFE_HASHTAGS = [
    "#femboy", "#crossdressing", "#otokonoko", "#anime", "#cosplay",
    "#cute", "#girlyboy", "#jpop", "#kawaii", "#fashion",
    "#创作", "#アニメ", "#コスプレ", "#かわいい", "#男の娘",
    "#イラスト", "#art", "#creative", "#style", "#lgbt"
]

# 露骨なワードと安全な代替表現の対応辞書
SAFE_EXPRESSIONS = {
    # 英語ワード
    "sex": "love",
    "xxx": "content",
    "porn": "video",
    "nsfw": "18+",
    "nude": "natural",
    "explicit": "mature",
    "adult": "mature",
    # 日本語ワード
    "エロ": "大人向け",
    "18禁": "成人向け",
    "アダルト": "大人向け",
    "ＡＶ": "動画",
    "援交": "出会い",
}

# エンゲージメントが高い時間帯（日本時間）
# 一般的なSNSの最適投稿時間帯に基づく
OPTIMAL_POSTING_HOURS = {
    "月曜日": [8, 12, 18, 21],
    "火曜日": [8, 12, 18, 21],
    "水曜日": [8, 12, 18, 21],
    "木曜日": [8, 12, 18, 21],
    "金曜日": [8, 12, 18, 20, 22],
    "土曜日": [10, 14, 18, 21, 23],
    "日曜日": [10, 14, 18, 21, 23],
}


def generate_post_template(video_info: dict) -> str:
    """
    動画情報からX（Twitter）投稿テンプレートを生成する。

    Args:
        video_info: 動画情報辞書
            {
                "title": str,        # 動画タイトル
                "url": str,          # 動画URL
                "category": str,     # カテゴリ
                "tags": list[str]    # タグリスト
            }

    Returns:
        投稿テンプレート文字列
    """
    title = video_info.get("title", "新着動画")
    url = video_info.get("url", "")
    tags = video_info.get("tags", [])

    # タイトルを安全表現に変換
    safe_title = convert_to_safe_expression(title)

    # 安全なハッシュタグを選定（最大5件）
    selected_hashtags = select_safe_hashtags(tags)[:5]
    hashtag_str = " ".join(selected_hashtags)

    # 投稿テンプレートを生成
    template = f"✨ {safe_title}\n\n{url}\n\n{hashtag_str}"

    # X（Twitter）の文字数制限（280文字）に収める
    if len(template) > 280:
        # タイトルを短縮
        max_title_len = 280 - len(url) - len(hashtag_str) - 10
        safe_title = safe_title[:max_title_len] + "..."
        template = f"✨ {safe_title}\n\n{url}\n\n{hashtag_str}"

    return template


def select_safe_hashtags(tags: list) -> list:
    """
    シャドウバンされにくい安全なハッシュタグを選定する。

    Args:
        tags: タグのリスト

    Returns:
        安全なハッシュタグのリスト（#付き）
    """
    selected = []

    for tag in tags:
        # タグを正規化
        normalized = tag.lower().strip()

        # 安全なハッシュタグリストに含まれるか確認
        hashtag = f"#{normalized}" if not normalized.startswith("#") else normalized
        if hashtag in SAFE_HASHTAGS:
            selected.append(hashtag)

    # 既存リストから足りない分を補充
    for safe_tag in SAFE_HASHTAGS:
        if safe_tag not in selected:
            selected.append(safe_tag)
        if len(selected) >= 10:
            break

    return selected


def suggest_optimal_posting_time() -> dict:
    """
    エンゲージメントが高い投稿最適タイミングを提案する。

    Returns:
        最適投稿時間の提案辞書
    """
    # 現在の曜日を取得
    weekday_names = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    now = datetime.now()
    current_weekday = weekday_names[now.weekday()]

    # 本日の最適投稿時間
    today_optimal = OPTIMAL_POSTING_HOURS.get(current_weekday, [21])

    # 次の最適投稿時間を計算
    current_hour = now.hour
    next_optimal_hour = None
    for hour in sorted(today_optimal):
        if hour > current_hour:
            next_optimal_hour = hour
            break

    # 当日に最適時間がない場合は翌日の最初の時間
    if next_optimal_hour is None:
        next_weekday = weekday_names[(now.weekday() + 1) % 7]
        next_day_hours = OPTIMAL_POSTING_HOURS.get(next_weekday, [8])
        next_optimal_hour = next_day_hours[0]
        next_day = "明日"
    else:
        next_day = "本日"

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M"),
        "current_weekday": current_weekday,
        "today_optimal_hours": [f"{h:02d}:00" for h in today_optimal],
        "next_optimal": f"{next_day} {next_optimal_hour:02d}:00",
        "weekly_schedule": {
            day: [f"{h:02d}:00" for h in hours]
            for day, hours in OPTIMAL_POSTING_HOURS.items()
        },
        "recommendation": "土日の夜（21〜23時）が最もエンゲージメントが高い傾向があります"
    }


def convert_to_safe_expression(text: str) -> str:
    """
    露骨なワードを安全な表現に変換する。

    Args:
        text: 変換対象のテキスト

    Returns:
        変換後のテキスト
    """
    result = text

    # 露骨なワードを順番に置換
    for unsafe_word, safe_word in SAFE_EXPRESSIONS.items():
        # 大文字小文字を区別せずに置換（英語のみ）
        if unsafe_word.isascii():
            import re
            result = re.sub(
                re.escape(unsafe_word),
                safe_word,
                result,
                flags=re.IGNORECASE
            )
        else:
            # 日本語はそのまま置換
            result = result.replace(unsafe_word, safe_word)

    return result


def save_social_media_report(data: dict, output_file: str) -> None:
    """
    SNS投稿データをJSONとMarkdownに保存する。

    Args:
        data: SNS投稿データ
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"SNS投稿データを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "social_media_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# SNS投稿自動化レポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        # 最適投稿時間
        f.write("## ⏰ 最適投稿タイミング\n\n")
        timing = data.get("optimal_times", {})
        f.write(f"**現在**: {timing.get('current_time', '不明')}\n\n")
        f.write(f"**次の最適投稿**: {timing.get('next_optimal', '不明')}\n\n")
        f.write(f"💡 {timing.get('recommendation', '')}\n\n")

        # 週間スケジュール
        f.write("### 週間最適投稿スケジュール\n\n")
        f.write("| 曜日 | 最適投稿時間 |\n")
        f.write("|------|-------------|\n")
        for day, hours in timing.get("weekly_schedule", {}).items():
            f.write(f"| {day} | {', '.join(hours)} |\n")

        # 安全なハッシュタグ
        f.write("\n## 🏷️ 安全なハッシュタグ一覧\n\n")
        safe_tags = data.get("safe_hashtags", [])
        if safe_tags:
            f.write(" ".join(safe_tags) + "\n")

        # 投稿テンプレート例
        f.write("\n## 📝 投稿テンプレート例\n\n")
        for i, template in enumerate(data.get("schedule", [])[:3], 1):
            f.write(f"### テンプレート {i}\n\n")
            f.write(f"```\n{template.get('template', '')}\n```\n\n")

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: SNS投稿自動化データを生成"""
    project_root = Path(__file__).parent.parent
    output_file = str(project_root / "data" / "posting_schedule.json")

    print("SNS投稿自動化データの生成を開始します...")

    # 投稿最適タイミングを取得
    optimal_times = suggest_optimal_posting_time()

    # サンプル動画で投稿テンプレートを生成
    sample_videos = [
        {
            "title": "男の娘 かわいい コスプレ動画",
            "url": "https://example.com/video/1",
            "category": "男の娘",
            "tags": ["femboy", "cosplay", "cute", "otokonoko"]
        }
    ]

    schedule = []
    for video in sample_videos:
        template = generate_post_template(video)
        schedule.append({
            "video_title": video["title"],
            "template": template,
            "recommended_time": optimal_times["next_optimal"]
        })

    # 結果をまとめる
    result = {
        "last_updated": datetime.now().isoformat(),
        "schedule": schedule,
        "optimal_times": optimal_times,
        "safe_hashtags": SAFE_HASHTAGS[:15]
    }

    # 保存
    save_social_media_report(result, output_file)
    print("SNS投稿自動化データの生成が完了しました！")


if __name__ == "__main__":
    main()
