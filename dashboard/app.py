"""
dashboard/app.py - Webダッシュボード（Flask）
個人利用目的のみ

トレンドランキング・タグ分析・次回ネタ提案を一画面で表示する
シンプルなWebUIを提供する。Bootstrap使用のレスポンシブデザイン。
"""

import json
import os
from pathlib import Path

from flask import Flask, render_template

# Flaskアプリを初期化
app = Flask(__name__)

# データディレクトリのパス
DATA_DIR = Path(__file__).parent.parent / "data"


def load_json_data(filename: str) -> dict:
    """
    JSONファイルを読み込む共通関数。

    Args:
        filename: データファイル名

    Returns:
        JSONデータ（読み込み失敗時は空辞書）
    """
    file_path = DATA_DIR / filename
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"データ読み込みエラー {filename}: {e}")
    return {}


@app.route("/")
def index():
    """
    メイン画面: ダッシュボードのトップページを表示する。
    トレンドサマリー・タグTOP5・カテゴリランキングを一覧表示。
    """
    # 各データを読み込む
    tags_data = load_json_data("tags_analysis.json")
    ranking_data = load_json_data("category_rankings.json")
    forecast_data = load_json_data("trend_forecast.json")
    creators_data = load_json_data("creators.json")

    # テンプレートに渡すデータを整形
    context = {
        "top_tags": tags_data.get("top_tags", [])[:5],
        "top_videos": ranking_data.get("rankings", {}).get("by_views", [])[:5],
        "growing_genres": forecast_data.get("top5_growing_genres", []),
        "creator_count": len(creators_data.get("creators", [])),
        "last_updated": tags_data.get("last_updated", "データなし")
    }

    return render_template("index.html", **context)


@app.route("/trends")
def trends():
    """
    トレンド画面: 詳細なトレンド分析と予測を表示する。
    """
    forecast_data = load_json_data("trend_forecast.json")
    ranking_data = load_json_data("category_rankings.json")

    context = {
        "top5_growing": forecast_data.get("top5_growing_genres", []),
        "all_predictions": forecast_data.get("all_predictions", [])[:20],
        "platform_comparison": ranking_data.get("platform_comparison", {}),
        "forecast_date": forecast_data.get("forecast_date", ""),
        "last_updated": forecast_data.get("last_updated", "データなし")
    }

    return render_template("trends.html", **context)


@app.route("/tags")
def tags():
    """
    タグ分析画面: タグの頻度ランキングと共起分析を表示する。
    """
    tags_data = load_json_data("tags_analysis.json")
    keywords_data = load_json_data("keywords.json")

    # 共起ペアを見やすい形式に変換
    cooccurrence_list = [
        {"pair": pair, "count": count}
        for pair, count in list(tags_data.get("cooccurrence", {}).items())[:10]
    ]

    context = {
        "top_tags": tags_data.get("top_tags", []),
        "cooccurrence": cooccurrence_list,
        "seo_tags": keywords_data.get("seo_tags", []),
        "total_tags": tags_data.get("total_tags_collected", 0),
        "last_updated": tags_data.get("last_updated", "データなし")
    }

    return render_template("tags.html", **context)


@app.route("/suggest")
def suggest():
    """
    次回ネタ提案画面: AI分析に基づく動画制作ネタを提案する。
    """
    tags_data = load_json_data("tags_analysis.json")
    forecast_data = load_json_data("trend_forecast.json")
    keywords_data = load_json_data("keywords.json")
    social_data = load_json_data("posting_schedule.json")

    # 上昇トレンドのタグからネタ候補を生成
    growing = forecast_data.get("top5_growing_genres", [])
    top_tags = tags_data.get("top_tags", [])[:10]

    # ネタ候補を組み合わせで生成
    suggestions = []
    for i, genre in enumerate(growing[:3]):
        suggestions.append({
            "rank": i + 1,
            "title_idea": f"{genre.get('tag', '不明')} テーマの動画",
            "reason": f"成長率 {genre.get('growth_rate', 0):.1f}% の上昇トレンド",
            "tags": top_tags[:5]
        })

    context = {
        "suggestions": suggestions,
        "optimal_time": social_data.get("optimal_times", {}).get("next_optimal", "不明"),
        "trending_keywords": keywords_data.get("trending", []),
        "last_updated": forecast_data.get("last_updated", "データなし")
    }

    return render_template("index.html", suggest_mode=True, **context)


if __name__ == "__main__":
    # 開発サーバーを起動（本番環境では gunicorn 等を使用）
    # デバッグモードはローカル開発時のみ使用
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
