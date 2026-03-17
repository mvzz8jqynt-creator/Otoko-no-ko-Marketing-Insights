"""
track_creators.py - 人気クリエイター追跡スクリプト
個人利用目的のみ

男の娘・ニューハーフジャンルのトップクリエイターを収集し、
投稿頻度・平均再生数・アップロードタイミングを分析する。
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path


# 曜日名（日本語）
WEEKDAY_NAMES = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]


def fetch_top_creators(platform: str, category: str) -> list:
    """
    プラットフォームとカテゴリからトップクリエイターを取得する。

    Args:
        platform: プラットフォーム名（例: "Pornhub", "XVideos"）
        category: カテゴリ名（例: "男の娘", "ニューハーフ"）

    Returns:
        クリエイター情報のリスト
    """
    print(f"{platform} の {category} カテゴリからクリエイターを取得中...")

    # 実際のAPI連携時はここでデータを取得する
    # 現在はプレースホルダーとして空リストを返す
    creators = []

    return creators


def analyze_creator_activity(creator: dict) -> dict:
    """
    クリエイターの活動を分析する（投稿頻度・平均再生数・人気ジャンル）。

    Args:
        creator: クリエイター情報辞書
            {
                "name": str,
                "videos": [{"title": str, "views": int, "likes": int,
                            "category": str, "upload_date": str}, ...]
            }

    Returns:
        活動分析結果
    """
    videos = creator.get("videos", [])

    if not videos:
        return {
            "name": creator.get("name", "不明"),
            "total_videos": 0,
            "avg_views": 0,
            "avg_likes": 0,
            "popular_genres": [],
            "post_frequency": "データなし"
        }

    # 平均再生数・いいね数を計算
    total_views = sum(v.get("views", 0) for v in videos)
    total_likes = sum(v.get("likes", 0) for v in videos)
    avg_views = total_views // len(videos)
    avg_likes = total_likes // len(videos)

    # 人気ジャンルを集計
    genres = [v.get("category", "不明") for v in videos]
    genre_counter = Counter(genres)
    popular_genres = [
        {"genre": genre, "count": count}
        for genre, count in genre_counter.most_common(5)
    ]

    # 投稿頻度を計算（月あたりの投稿数）
    upload_dates = []
    for v in videos:
        if "upload_date" in v:
            try:
                upload_dates.append(datetime.fromisoformat(v["upload_date"]))
            except ValueError:
                pass

    post_frequency = "データなし"
    if len(upload_dates) >= 2:
        upload_dates.sort()
        total_days = (upload_dates[-1] - upload_dates[0]).days
        if total_days > 0:
            monthly_posts = len(upload_dates) / (total_days / 30)
            post_frequency = f"月約{monthly_posts:.1f}件"

    return {
        "name": creator.get("name", "不明"),
        "platform": creator.get("platform", "不明"),
        "total_videos": len(videos),
        "total_views": total_views,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "popular_genres": popular_genres,
        "post_frequency": post_frequency
    }


def get_upload_timing(creator: dict) -> dict:
    """
    クリエイターのアップロードタイミング（曜日・時間帯）を分析する。

    Args:
        creator: クリエイター情報辞書（"videos"リストにupload_dateを含む）

    Returns:
        アップロードタイミング分析結果
    """
    videos = creator.get("videos", [])
    weekday_counts = Counter()
    hour_counts = Counter()

    for video in videos:
        upload_date_str = video.get("upload_date", "")
        if not upload_date_str:
            continue

        try:
            upload_dt = datetime.fromisoformat(upload_date_str)
            # 曜日をカウント（0=月曜、6=日曜）
            weekday_counts[upload_dt.weekday()] += 1
            # 時間帯をカウント
            hour_counts[upload_dt.hour] += 1
        except ValueError:
            continue

    # 最も多い曜日を特定
    most_common_weekday = None
    if weekday_counts:
        most_common_weekday_idx = weekday_counts.most_common(1)[0][0]
        most_common_weekday = WEEKDAY_NAMES[most_common_weekday_idx]

    # 最も多い時間帯を特定
    most_common_hour = None
    if hour_counts:
        most_common_hour = hour_counts.most_common(1)[0][0]

    return {
        "name": creator.get("name", "不明"),
        "weekday_distribution": {
            WEEKDAY_NAMES[k]: v
            for k, v in sorted(weekday_counts.items())
        },
        "hour_distribution": {
            f"{k:02d}時": v
            for k, v in sorted(hour_counts.items())
        },
        "best_weekday": most_common_weekday,
        "best_hour": f"{most_common_hour:02d}時" if most_common_hour is not None else "データなし"
    }


def save_creator_report(creators_data: list, output_file: str) -> None:
    """
    クリエイターデータをJSONとMarkdownに保存する。

    Args:
        creators_data: クリエイター分析データのリスト
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    result = {
        "last_updated": datetime.now().isoformat(),
        "creators": creators_data
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"クリエイターデータを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "creator_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 人気クリエイターレポート\n\n")
        f.write(f"生成日時: {result['last_updated']}\n\n")

        f.write("## 👤 クリエイター一覧\n\n")

        if not creators_data:
            f.write("データがありません。fetch_top_creators()でデータを収集してください。\n")
        else:
            f.write("| クリエイター名 | プラットフォーム | 総動画数 | 平均再生数 | 投稿頻度 |\n")
            f.write("|----------------|------------------|----------|------------|----------|\n")
            for creator in creators_data:
                f.write(
                    f"| {creator['name']} | {creator.get('platform', '不明')} | "
                    f"{creator['total_videos']} | {creator['avg_views']:,} | "
                    f"{creator['post_frequency']} |\n"
                )

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: クリエイター追跡を実行"""
    project_root = Path(__file__).parent.parent
    output_file = str(project_root / "data" / "creators.json")

    print("クリエイター追跡を開始します...")

    # プラットフォームとカテゴリからクリエイターを収集
    all_creators = []
    platforms = ["Pornhub", "XVideos", "xHamster"]
    categories = ["男の娘", "ニューハーフ"]

    for platform in platforms:
        for category in categories:
            creators = fetch_top_creators(platform, category)
            all_creators.extend(creators)

    # 各クリエイターの活動を分析
    analyzed_creators = []
    for creator in all_creators:
        activity = analyze_creator_activity(creator)
        timing = get_upload_timing(creator)
        activity["upload_timing"] = timing
        analyzed_creators.append(activity)

    # レポートを保存
    save_creator_report(analyzed_creators, output_file)
    print("クリエイター追跡が完了しました！")


if __name__ == "__main__":
    main()
