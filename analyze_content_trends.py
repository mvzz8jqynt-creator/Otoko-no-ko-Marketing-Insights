#!/usr/bin/env python3
"""
マイファンズ 男の娘・ニューハーフ 投稿コンテンツトレンド分析
MyFans Content Trend Analysis for Otoko-no-ko / Newhalfs
"""

import json
import re
from collections import Counter
from pathlib import Path


def load_data(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)["posts"]


def extract_all_words(texts: list[str]) -> list[str]:
    """日本語・英語の単語を抽出（助詞・記号を除く）"""
    stop_words = {
        "を", "は", "が", "に", "で", "と", "の", "も", "な", "や",
        "て", "し", "い", "た", "ます", "です", "ため", "から", "まで",
        "ない", "する", "れる", "られる", "など", "こと", "もの",
        "の", "a", "the", "and", "or", "for", "to", "in", "on",
    }
    words = []
    for text in texts:
        # 日本語：2文字以上の連続した日本語文字
        jp_words = re.findall(r'[\u3040-\u9faf\u30a0-\u30ff]{2,}', text)
        # 英数字
        en_words = re.findall(r'[a-zA-Z]{3,}', text)
        all_w = jp_words + [w.lower() for w in en_words]
        words.extend([w for w in all_w if w not in stop_words])
    return words


def compute_metrics(posts: list[dict]) -> list[dict]:
    for p in posts:
        p["like_rate"] = round(p["likes"] / p["followers"] * 100, 2)
        p["comment_rate"] = round(p["comments"] / p["followers"] * 100, 2)
        p["purchase_rate"] = round(p["purchases"] / p["followers"] * 100, 2)
        p["engagement_index"] = round(
            (p["likes"] + p["comments"] * 3 + p["purchases"] * 5) / p["followers"] * 100, 2
        )
    return posts


def analyze_by_category(posts: list[dict]) -> dict:
    categories = {}
    for p in posts:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)
    return categories


def top_posts(posts: list[dict], n: int = 5, key: str = "engagement_index") -> list[dict]:
    return sorted(posts, key=lambda x: x[key], reverse=True)[:n]


def word_frequency(posts: list[dict], source: str = "all") -> Counter:
    """source: 'tags' | 'content' | 'all'"""
    texts = []
    for p in posts:
        if source in ("tags", "all"):
            texts.append(" ".join(p["tags"]))
        if source in ("content", "all"):
            texts.append(p["title"] + " " + p["content"])
    words = extract_all_words(texts)
    return Counter(words)


def content_pattern_analysis(posts: list[dict]) -> dict:
    """コンテンツパターンを分類・集計"""
    patterns = {
        "プレゼント・特典系": 0,
        "配信・ライブ系": 0,
        "ビフォーアフター・変化記録": 0,
        "Q&A・本音トーク": 0,
        "コスプレ・衣装コーデ": 0,
        "日常・ルーティン": 0,
        "チャレンジ・企画系": 0,
        "ストーリー・体験談": 0,
    }
    keywords_map = {
        "プレゼント・特典系": ["プレゼント", "特典", "割引", "クーポン", "抽選", "サイン"],
        "配信・ライブ系": ["配信", "ライブ", "生配信"],
        "ビフォーアフター・変化記録": ["ビフォーアフター", "変化", "記録", "成果", "報告"],
        "Q&A・本音トーク": ["Q&A", "本音", "質問", "ガチ回答", "トーク"],
        "コスプレ・衣装コーデ": ["コスプレ", "コーデ", "衣装", "ドレス", "ランジェリー", "制服", "浴衣", "ロリータ"],
        "日常・ルーティン": ["ルーティン", "日常", "密着", "モーニング"],
        "チャレンジ・企画系": ["チャレンジ", "100日", "企画", "初挑戦", "初めて"],
        "ストーリー・体験談": ["経験談", "決断", "告白", "記録", "体験", "卒業"],
    }
    for p in posts:
        text = p["title"] + " " + p["content"] + " " + " ".join(p["tags"])
        for pattern_name, kw_list in keywords_map.items():
            for kw in kw_list:
                if kw in text:
                    patterns[pattern_name] += 1
                    break
    return patterns


def print_section(title: str, width: int = 60):
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def run_analysis():
    data_path = Path(__file__).parent / "data" / "sample_posts.json"
    posts = load_data(str(data_path))
    posts = compute_metrics(posts)
    categories = analyze_by_category(posts)

    print_section("マイファンズ コンテンツトレンド分析レポート")
    print(f"  分析対象投稿数: {len(posts)} 件")
    for cat, cat_posts in categories.items():
        print(f"  - {cat}: {len(cat_posts)} 件")

    # ─── 全体エンゲージメント指標 ────────────────────────
    print_section("全体パフォーマンス指標")
    avg_like = sum(p["like_rate"] for p in posts) / len(posts)
    avg_comment = sum(p["comment_rate"] for p in posts) / len(posts)
    avg_purchase = sum(p["purchase_rate"] for p in posts) / len(posts)
    avg_ei = sum(p["engagement_index"] for p in posts) / len(posts)
    print(f"  平均いいね率       : {avg_like:.2f}%")
    print(f"  平均コメント率     : {avg_comment:.2f}%")
    print(f"  平均購入率         : {avg_purchase:.2f}%")
    print(f"  平均エンゲージ指数 : {avg_ei:.2f}")

    # ─── カテゴリ別比較 ──────────────────────────────────
    print_section("カテゴリ別平均エンゲージメント比較")
    for cat, cat_posts in categories.items():
        ei = sum(p["engagement_index"] for p in cat_posts) / len(cat_posts)
        pr = sum(p["purchase_rate"] for p in cat_posts) / len(cat_posts)
        print(f"  [{cat}]")
        print(f"    エンゲージ指数: {ei:.2f} / 購入率: {pr:.2f}%")

    # ─── TOP5 投稿（全体） ───────────────────────────────
    print_section("エンゲージメント上位 TOP5 投稿")
    for i, p in enumerate(top_posts(posts, n=5), 1):
        print(f"  {i}. [{p['category']}] {p['title'][:35]}...")
        print(f"     EI={p['engagement_index']}  いいね={p['likes']}  "
              f"購入={p['purchases']}  購入率={p['purchase_rate']}%")

    # ─── 頻出タグ（全体） ────────────────────────────────
    print_section("頻出タグ TOP20（全投稿）")
    tag_counter = Counter()
    for p in posts:
        tag_counter.update(p["tags"])
    for rank, (tag, count) in enumerate(tag_counter.most_common(20), 1):
        bar = "█" * count
        print(f"  {rank:2d}. #{tag:<14} {count:2d}回  {bar}")

    # ─── カテゴリ別 頻出単語 ────────────────────────────
    for cat, cat_posts in categories.items():
        print_section(f"頻出単語 TOP15：【{cat}】")
        freq = word_frequency(cat_posts, source="all")
        for rank, (word, count) in enumerate(freq.most_common(15), 1):
            bar = "▪" * count
            print(f"  {rank:2d}. {word:<12} {count:2d}回  {bar}")

    # ─── コンテンツパターン分布 ──────────────────────────
    print_section("コンテンツパターン分類（全投稿）")
    patterns = content_pattern_analysis(posts)
    total_matched = sum(patterns.values())
    for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
        pct = count / len(posts) * 100
        bar = "█" * count
        print(f"  {pattern:<20} {count:2d}件 ({pct:4.0f}%)  {bar}")

    # ─── 高購入率投稿の特徴分析 ──────────────────────────
    print_section("高購入率投稿（購入率3%以上）の特徴分析")
    high_purchase = [p for p in posts if p["purchase_rate"] >= 3.0]
    print(f"  対象投稿数: {len(high_purchase)} 件")
    freq_hp = word_frequency(high_purchase, source="all")
    print("  頻出単語 TOP10:")
    for rank, (word, count) in enumerate(freq_hp.most_common(10), 1):
        print(f"    {rank:2d}. {word} ({count}回)")

    # ─── インサイト & 提言 ───────────────────────────────
    print_section("マーケティングインサイト & 提言")
    top_tag = tag_counter.most_common(1)[0][0]
    top_pattern = max(patterns.items(), key=lambda x: x[1])[0]
    best_cat = max(categories.keys(),
                   key=lambda c: sum(p["engagement_index"] for p in categories[c]) / len(categories[c]))

    print(f"""
  1. 最も頻出するタグは「#{top_tag}」── 投稿タイトルや説明文に積極的に活用を

  2. 最も多いコンテンツパターンは「{top_pattern}」
     ─ プレゼント・特典・割引を絡めた投稿がエンゲージを最大化する傾向

  3. カテゴリ別では「{best_cat}」が平均エンゲージ指数が高い
     ─ よりパーソナルなストーリー・体験談が共感を呼ぶ

  4. 高購入率投稿の共通要素:
     ─ 限定感（限定・今だけ・特別）を明示
     ─ プレゼント・特典の具体的な内容を記載
     ─ 感情的なエピソード（本音・告白・変化）と組み合わせ

  5. 推奨アクション:
     ─ 投稿に「限定特典 + 個人ストーリー」の組み合わせを意識
     ─ コメント促進（質問・投票・返信保証）でコメント率を高める
     ─ 季節イベント（夏祭り・コミケ・バレンタイン）との連動を計画
""")

    # ─── 結果をファイル保存 ──────────────────────────────
    output_path = Path(__file__).parent / "data" / "analysis_results.json"
    results = {
        "summary": {
            "total_posts": len(posts),
            "avg_like_rate": round(avg_like, 2),
            "avg_comment_rate": round(avg_comment, 2),
            "avg_purchase_rate": round(avg_purchase, 2),
            "avg_engagement_index": round(avg_ei, 2),
        },
        "top5_posts": [
            {"title": p["title"], "category": p["category"],
             "engagement_index": p["engagement_index"],
             "purchase_rate": p["purchase_rate"]}
            for p in top_posts(posts, n=5)
        ],
        "top20_tags": tag_counter.most_common(20),
        "content_patterns": patterns,
        "category_comparison": {
            cat: {
                "avg_engagement_index": round(
                    sum(p["engagement_index"] for p in cat_posts) / len(cat_posts), 2),
                "avg_purchase_rate": round(
                    sum(p["purchase_rate"] for p in cat_posts) / len(cat_posts), 2),
            }
            for cat, cat_posts in categories.items()
        },
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  分析結果を保存しました: {output_path}")


if __name__ == "__main__":
    run_analysis()
