"""
analyze_tags.py - タグ分析強化スクリプト
個人利用目的のみ

動画・漫画・X(Twitter)の全タグを横断的に収集・集計し、
出現頻度ランキングや共起分析を行う。
"""

import json
import os
from collections import Counter
from datetime import datetime
from itertools import combinations
from pathlib import Path


def collect_all_tags(data_dir: str) -> list:
    """
    指定ディレクトリ内の全JSONファイルからタグを収集する。

    Args:
        data_dir: データディレクトリのパス

    Returns:
        全タグのリスト（重複あり）
    """
    all_tags = []
    data_path = Path(data_dir)

    # 各JSONファイルを読み込んでタグを収集
    for json_file in data_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # データ構造に応じてタグを抽出
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "tags" in item:
                        all_tags.extend(item["tags"])
            elif isinstance(data, dict):
                # トップレベルのタグリスト
                if "tags" in data:
                    all_tags.extend(data["tags"])
                # ネストされたデータ内のタグ
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and "tags" in item:
                                all_tags.extend(item["tags"])

        except (json.JSONDecodeError, IOError) as e:
            print(f"ファイル読み込みエラー {json_file}: {e}")

    return all_tags


def rank_tags_by_frequency(tags: list, top_n: int = 20) -> list:
    """
    タグの出現頻度でランキングを生成する。

    Args:
        tags: タグのリスト
        top_n: 上位N件（デフォルト20）

    Returns:
        頻度順のタグランキングリスト [{"tag": str, "count": int}, ...]
    """
    # タグを正規化（小文字・前後空白除去）
    normalized_tags = [t.lower().strip() for t in tags if t.strip()]
    counter = Counter(normalized_tags)

    # TOP N のランキングリストを生成
    ranking = [
        {"rank": i + 1, "tag": tag, "count": count}
        for i, (tag, count) in enumerate(counter.most_common(top_n))
    ]

    return ranking


def analyze_tag_cooccurrence(tags_per_item: list, min_count: int = 2) -> dict:
    """
    タグの共起分析を行う（一緒によく使われるタグの組み合わせ）。

    Args:
        tags_per_item: アイテムごとのタグリスト [[tag1, tag2, ...], ...]
        min_count: 最小共起回数（デフォルト2）

    Returns:
        共起ペアと頻度の辞書 {"tag1,tag2": count, ...}
    """
    cooccurrence = Counter()

    for item_tags in tags_per_item:
        # 重複タグを除去して正規化
        unique_tags = list(set(t.lower().strip() for t in item_tags if t.strip()))

        # 全タグペアの組み合わせをカウント
        for pair in combinations(sorted(unique_tags), 2):
            cooccurrence[pair] += 1

    # 最小共起回数以上のペアのみ返す
    result = {
        f"{pair[0]},{pair[1]}": count
        for pair, count in cooccurrence.most_common()
        if count >= min_count
    }

    return result


def save_tag_report(data: dict, output_file: str) -> None:
    """
    タグ分析結果をJSONとMarkdownレポートに保存する。

    Args:
        data: タグ分析データ
        output_file: 出力JSONファイルのパス
    """
    # JSONデータを保存
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"タグ分析データを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "tag_statistics.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# タグ統計レポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        # TOP20タグランキング
        f.write("## 📊 タグ出現頻度 TOP 20\n\n")
        f.write("| ランク | タグ | 出現回数 |\n")
        f.write("|--------|------|----------|\n")
        for item in data.get("top_tags", []):
            f.write(f"| {item['rank']} | {item['tag']} | {item['count']} |\n")

        # 共起分析
        f.write("\n## 🔗 タグ共起分析（よく一緒に使われるタグ）\n\n")
        f.write("| タグペア | 共起回数 |\n")
        f.write("|----------|----------|\n")
        cooccurrence = data.get("cooccurrence", {})
        # 上位10件のみ表示
        for pair, count in list(cooccurrence.items())[:10]:
            f.write(f"| {pair} | {count} |\n")

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: タグ分析を実行してレポートを生成"""
    # プロジェクトルートのパスを設定
    project_root = Path(__file__).parent.parent
    data_dir = str(project_root / "data")
    output_file = str(project_root / "data" / "tags_analysis.json")

    print("タグ分析を開始します...")

    # 全タグを収集
    all_tags = collect_all_tags(data_dir)
    print(f"収集タグ数: {len(all_tags)}")

    # 頻度ランキングを生成
    ranking = rank_tags_by_frequency(all_tags, top_n=20)

    # 共起分析用のタググループを収集
    tags_per_item = []
    data_path = Path(data_dir)
    for json_file in data_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "tags" in item:
                        tags_per_item.append(item["tags"])
        except (json.JSONDecodeError, IOError):
            pass

    # 共起分析を実行
    cooccurrence = analyze_tag_cooccurrence(tags_per_item)

    # 分析結果をまとめる
    result = {
        "last_updated": datetime.now().isoformat(),
        "total_tags_collected": len(all_tags),
        "top_tags": ranking,
        "cooccurrence": cooccurrence,
        "time_series": {}
    }

    # レポートを保存
    save_tag_report(result, output_file)
    print("タグ分析が完了しました！")


if __name__ == "__main__":
    main()
