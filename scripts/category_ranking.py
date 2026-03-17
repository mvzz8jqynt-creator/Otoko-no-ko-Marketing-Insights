"""
category_ranking.py - カテゴリ別ランキングシステム
個人利用目的のみ

再生数・いいね数・コメント数でジャンルをランキング化し、
カテゴリ別・プラットフォーム別のTOP動画リストを生成する。
"""

import json
from datetime import datetime
from pathlib import Path


def generate_category_ranking(data: list, metric: str) -> list:
    """
    指定メトリクスでカテゴリ別ランキングを生成する。

    Args:
        data: 動画データのリスト
        metric: ランキング基準（"views", "likes", "comments"）

    Returns:
        ランキングリスト [{"rank": int, "title": str, "category": str, metric: int}, ...]
    """
    # メトリクスの有効性を確認
    valid_metrics = ["views", "likes", "comments"]
    if metric not in valid_metrics:
        raise ValueError(f"無効なメトリクス: {metric}。有効値: {valid_metrics}")

    # データをメトリクスでソート
    sorted_data = sorted(
        data,
        key=lambda x: x.get(metric, 0),
        reverse=True
    )

    # ランキングリストを生成
    ranking = []
    for i, item in enumerate(sorted_data):
        ranking.append({
            "rank": i + 1,
            "title": item.get("title", "不明"),
            "category": item.get("category", "不明"),
            "platform": item.get("platform", "不明"),
            metric: item.get(metric, 0),
            "url": item.get("url", "")
        })

    return ranking


def get_top_videos(data: list, category: str, limit: int = 10) -> list:
    """
    カテゴリ別のTOP動画リストを取得する。

    Args:
        data: 動画データのリスト
        category: カテゴリ名（例: "ソロ", "femboy×femboy", "femboy×male"）
        limit: 取得件数（デフォルト10）

    Returns:
        TOP動画リスト
    """
    # カテゴリでフィルタリング
    filtered = [item for item in data if item.get("category", "") == category]

    # 再生数でソートしてTOP N を返す
    top_videos = sorted(
        filtered,
        key=lambda x: x.get("views", 0),
        reverse=True
    )[:limit]

    # ランク番号を付与
    for i, video in enumerate(top_videos):
        video["rank"] = i + 1

    return top_videos


def compare_platform_rankings(data: list) -> dict:
    """
    プラットフォーム別ランキングを比較する。

    Args:
        data: 動画データのリスト（platformフィールドを含む）

    Returns:
        プラットフォーム別ランキング辞書
    """
    # プラットフォームリスト（主要サイト）
    platforms = ["Pornhub", "XVideos", "xHamster"]
    comparison = {}

    for platform in platforms:
        # プラットフォームでフィルタリング
        platform_data = [
            item for item in data
            if item.get("platform", "").lower() == platform.lower()
        ]

        if platform_data:
            # 再生数TOP5を取得
            top5 = sorted(
                platform_data,
                key=lambda x: x.get("views", 0),
                reverse=True
            )[:5]

            comparison[platform] = {
                "total_videos": len(platform_data),
                "top5": [
                    {
                        "rank": i + 1,
                        "title": v.get("title", "不明"),
                        "views": v.get("views", 0),
                        "category": v.get("category", "不明")
                    }
                    for i, v in enumerate(top5)
                ]
            }
        else:
            comparison[platform] = {"total_videos": 0, "top5": []}

    return comparison


def save_category_rankings(data: dict, output_file: str) -> None:
    """
    カテゴリランキングをJSONとMarkdownに保存する。

    Args:
        data: ランキングデータ
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"カテゴリランキングデータを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "category_ranking_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# カテゴリ別ランキングレポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        # 再生数ランキング
        f.write("## 🎬 再生数ランキング TOP 10\n\n")
        f.write("| ランク | タイトル | カテゴリ | プラットフォーム | 再生数 |\n")
        f.write("|--------|----------|----------|------------------|--------|\n")
        for item in data.get("rankings", {}).get("by_views", [])[:10]:
            f.write(
                f"| {item['rank']} | {item['title']} | "
                f"{item['category']} | {item['platform']} | "
                f"{item.get('views', 0):,} |\n"
            )

        # プラットフォーム比較
        f.write("\n## 📊 プラットフォーム別比較\n\n")
        for platform, pdata in data.get("platform_comparison", {}).items():
            f.write(f"### {platform} ({pdata['total_videos']}件)\n\n")
            f.write("| ランク | タイトル | 再生数 |\n")
            f.write("|--------|----------|--------|\n")
            for v in pdata.get("top5", []):
                f.write(f"| {v['rank']} | {v['title']} | {v.get('views', 0):,} |\n")
            f.write("\n")

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: カテゴリ別ランキングを生成"""
    project_root = Path(__file__).parent.parent
    output_file = str(project_root / "data" / "category_rankings.json")

    print("カテゴリ別ランキング生成を開始します...")

    # サンプルデータ（実際のデータはfetch_video_data.pyで収集）
    sample_data = []

    # カテゴリリスト
    categories = ["ソロ", "femboy×femboy", "femboy×male"]

    # ランキングを生成
    rankings = {
        "by_views": generate_category_ranking(sample_data, "views"),
        "by_likes": generate_category_ranking(sample_data, "likes"),
        "by_comments": generate_category_ranking(sample_data, "comments")
    }

    # カテゴリ別TOP10を生成
    category_tops = {}
    for category in categories:
        category_tops[category] = get_top_videos(sample_data, category, limit=10)

    # プラットフォーム比較
    platform_comparison = compare_platform_rankings(sample_data)

    # 結果をまとめる
    result = {
        "last_updated": datetime.now().isoformat(),
        "rankings": rankings,
        "category_tops": category_tops,
        "platform_comparison": platform_comparison
    }

    # 保存
    save_category_rankings(result, output_file)
    print("カテゴリ別ランキング生成が完了しました！")


if __name__ == "__main__":
    main()
