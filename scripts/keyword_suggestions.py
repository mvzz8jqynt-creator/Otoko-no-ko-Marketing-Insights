"""
keyword_suggestions.py - 関連キーワード提案スクリプト
個人利用目的のみ

人気検索ワードから関連キーワードを自動生成し、
SEO最適化のためのタグ・キーワードを推薦する。
Google Trends連携（pytrends）でトレンドキーワードを取得。
"""

import json
from datetime import datetime
from pathlib import Path


# 男の娘・ニューハーフ関連のシード・キーワード辞書
SEED_KEYWORDS = {
    "男の娘": ["otokonoko", "男の娘", "femboy", "trap", "crossdresser"],
    "ニューハーフ": ["ニューハーフ", "newhalf", "shemale", "ladyboy"],
    "femboy": ["femboy", "femboys", "フェムボーイ", "girly boy"],
    "trap": ["trap", "トラップ", "anime trap", "cute boy"],
}

# SEO最適化用の安全なタグセット
SAFE_TAGS = [
    "femboy", "crossdressing", "anime", "cute", "otokonoko",
    "newhalf", "girlyboy", "japanese", "cosplay", "amateur"
]


def fetch_related_keywords(keyword: str) -> dict:
    """
    キーワードの関連語・類似語を取得する。

    Args:
        keyword: 検索キーワード

    Returns:
        関連キーワード辞書
    """
    print(f"「{keyword}」の関連キーワードを取得中...")

    # シード辞書から関連語を取得
    related = SEED_KEYWORDS.get(keyword, [keyword])

    # Google Trends連携（pytrendsが利用可能な場合）
    google_trends_related = []
    try:
        from pytrends.request import TrendReq  # type: ignore

        pytrends = TrendReq(hl="ja-JP", tz=540)
        pytrends.build_payload([keyword], timeframe="today 3-m")
        related_queries = pytrends.related_queries()

        if keyword in related_queries and related_queries[keyword]["top"] is not None:
            top_queries = related_queries[keyword]["top"]
            google_trends_related = top_queries["query"].tolist()[:10]

    except ImportError:
        print("pytrendsが未インストールです。Google Trends連携をスキップします。")
    except Exception as e:
        print(f"Google Trends取得エラー: {e}")

    return {
        "keyword": keyword,
        "seed_related": related,
        "google_trends_related": google_trends_related,
        "all_related": list(set(related + google_trends_related))
    }


def generate_seo_tags(video_title: str) -> list:
    """
    動画タイトルからSEO最適化タグを生成する。

    Args:
        video_title: 動画タイトル

    Returns:
        SEOタグのリスト
    """
    title_lower = video_title.lower()
    selected_tags = list(SAFE_TAGS)  # 基本タグをコピー

    # タイトルに含まれるキーワードに応じてタグを追加
    keyword_tag_map = {
        "男の娘": ["otokonoko", "japanese femboy"],
        "otokonoko": ["otokonoko", "japanese femboy"],
        "ニューハーフ": ["newhalf", "japanese ladyboy"],
        "newhalf": ["newhalf", "japanese ladyboy"],
        "femboy": ["femboy", "girlyboy"],
        "crossdress": ["crossdressing", "crossdresser"],
        "anime": ["anime", "hentai style"],
        "cosplay": ["cosplay", "costume"]
    }

    for keyword, tags in keyword_tag_map.items():
        if keyword in title_lower or keyword in video_title:
            selected_tags.extend(tags)

    # 重複を除去して最大20件
    unique_tags = list(dict.fromkeys(selected_tags))[:20]

    return unique_tags


def get_trending_keywords(category: str) -> list:
    """
    カテゴリのトレンドキーワードを取得する。

    Args:
        category: カテゴリ名（例: "男の娘", "ニューハーフ"）

    Returns:
        トレンドキーワードリスト
    """
    print(f"{category} カテゴリのトレンドキーワードを取得中...")

    # Google Trends連携
    trending = []
    try:
        from pytrends.request import TrendReq  # type: ignore

        pytrends = TrendReq(hl="ja-JP", tz=540)

        # カテゴリに応じたキーワードでトレンドを取得
        seed = SEED_KEYWORDS.get(category, [category])
        # Google Trendsは最大5キーワードまで
        keywords_to_check = seed[:5]

        if keywords_to_check:
            pytrends.build_payload(keywords_to_check, timeframe="today 1-m")
            interest = pytrends.interest_over_time()

            if not interest.empty:
                # 最新の値で人気順にソート
                latest_values = interest.iloc[-1].drop("isPartial", errors="ignore")
                trending = latest_values.sort_values(ascending=False).index.tolist()

    except ImportError:
        print("pytrendsが未インストールです。デフォルトキーワードを使用します。")
        trending = SEED_KEYWORDS.get(category, [category])
    except Exception as e:
        print(f"トレンドキーワード取得エラー: {e}")
        trending = SEED_KEYWORDS.get(category, [category])

    return trending


def save_keyword_report(data: dict, output_file: str) -> None:
    """
    キーワードデータをJSONとMarkdownに保存する。

    Args:
        data: キーワードデータ
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"キーワードデータを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "keyword_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 関連キーワード提案レポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        # 関連キーワード
        f.write("## 🔑 関連キーワード一覧\n\n")
        for keyword, kw_data in data.get("related_keywords", {}).items():
            f.write(f"### 「{keyword}」の関連語\n\n")
            all_related = kw_data.get("all_related", [])
            if all_related:
                f.write(", ".join(f"`{k}`" for k in all_related) + "\n\n")

        # SEOタグ推薦
        f.write("## 🎯 SEO最適化推薦タグ\n\n")
        seo_tags = data.get("seo_tags", [])
        if seo_tags:
            f.write(", ".join(f"`{t}`" for t in seo_tags) + "\n\n")

        # トレンドキーワード
        f.write("## 📈 トレンドキーワード\n\n")
        for item in data.get("trending", []):
            f.write(f"- **{item['category']}**: {', '.join(item['keywords'])}\n")

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: 関連キーワード提案を実行"""
    project_root = Path(__file__).parent.parent
    output_file = str(project_root / "data" / "keywords.json")

    print("関連キーワード提案を開始します...")

    # 関連キーワードを取得
    target_keywords = list(SEED_KEYWORDS.keys())
    related_keywords = {}
    for keyword in target_keywords:
        related_keywords[keyword] = fetch_related_keywords(keyword)

    # SEOタグを生成（サンプルタイトルで）
    sample_titles = ["男の娘 femboy 動画", "ニューハーフ newhalf"]
    all_seo_tags = []
    for title in sample_titles:
        tags = generate_seo_tags(title)
        all_seo_tags.extend(tags)

    # 重複除去
    all_seo_tags = list(dict.fromkeys(all_seo_tags))

    # トレンドキーワードを取得
    trending = []
    categories = ["男の娘", "ニューハーフ"]
    for category in categories:
        trending_kw = get_trending_keywords(category)
        trending.append({
            "category": category,
            "keywords": trending_kw
        })

    # 結果をまとめる
    result = {
        "last_updated": datetime.now().isoformat(),
        "related_keywords": related_keywords,
        "seo_tags": all_seo_tags,
        "trending": trending
    }

    # 保存
    save_keyword_report(result, output_file)
    print("関連キーワード提案が完了しました！")


if __name__ == "__main__":
    main()
