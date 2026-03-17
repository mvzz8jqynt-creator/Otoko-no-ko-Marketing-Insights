"""
demographics.py - 視聴者デモグラフィック調査スクリプト
個人利用目的のみ

視聴者の地域別分布・デバイス別視聴傾向を調査し、
男の娘・ニューハーフコンテンツの主要視聴者層を特定する。
"""

import json
from datetime import datetime
from pathlib import Path


def fetch_viewer_demographics(category: str) -> dict:
    """
    カテゴリの視聴者デモグラフィックデータを取得する。

    Args:
        category: カテゴリ名（例: "男の娘", "ニューハーフ"）

    Returns:
        デモグラフィックデータ辞書
    """
    print(f"{category} カテゴリのデモグラフィックデータを取得中...")

    # 実際のAPI連携時はここでデータを取得する
    # 現在はプレースホルダーとして空の構造を返す
    demographics = {
        "category": category,
        "regional": {},
        "device": {},
        "age_groups": {}
    }

    return demographics


def analyze_regional_data(data: dict) -> dict:
    """
    地域別視聴データを分析する。

    Args:
        data: デモグラフィックデータ（regional フィールドを含む）

    Returns:
        地域別分析結果
    """
    regional_data = data.get("regional", {})

    if not regional_data:
        return {"top_regions": [], "total_countries": 0}

    # 視聴数で地域をソート
    sorted_regions = sorted(
        regional_data.items(),
        key=lambda x: x[1].get("views", 0),
        reverse=True
    )

    # TOP10地域を返す
    top_regions = [
        {
            "rank": i + 1,
            "country": country,
            "views": info.get("views", 0),
            "percentage": info.get("percentage", 0.0)
        }
        for i, (country, info) in enumerate(sorted_regions[:10])
    ]

    return {
        "top_regions": top_regions,
        "total_countries": len(regional_data)
    }


def analyze_device_data(data: dict) -> dict:
    """
    デバイス別視聴データを分析する。

    Args:
        data: デモグラフィックデータ（device フィールドを含む）

    Returns:
        デバイス別分析結果
    """
    device_data = data.get("device", {})

    if not device_data:
        return {
            "mobile_percentage": 0.0,
            "desktop_percentage": 0.0,
            "tablet_percentage": 0.0,
            "dominant_device": "データなし"
        }

    total_views = sum(
        info.get("views", 0)
        for info in device_data.values()
    )

    if total_views == 0:
        return {
            "mobile_percentage": 0.0,
            "desktop_percentage": 0.0,
            "tablet_percentage": 0.0,
            "dominant_device": "データなし"
        }

    # デバイス別パーセンテージを計算
    device_percentages = {}
    for device, info in device_data.items():
        views = info.get("views", 0)
        device_percentages[device] = round(views / total_views * 100, 1)

    # 最も多いデバイスを特定
    dominant_device = max(device_percentages, key=device_percentages.get)

    return {
        "device_percentages": device_percentages,
        "mobile_percentage": device_percentages.get("mobile", 0.0),
        "desktop_percentage": device_percentages.get("desktop", 0.0),
        "tablet_percentage": device_percentages.get("tablet", 0.0),
        "dominant_device": dominant_device
    }


def save_demographics_report(data: dict, output_file: str) -> None:
    """
    デモグラフィックデータをJSONとMarkdownに保存する。

    Args:
        data: デモグラフィック分析データ
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"デモグラフィックデータを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "demographics_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 視聴者デモグラフィックレポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        # 地域別分析
        f.write("## 🌍 地域別視聴分布 TOP 10\n\n")
        f.write("| ランク | 国・地域 | 視聴数 | 割合 |\n")
        f.write("|--------|----------|--------|------|\n")
        for item in data.get("regional_analysis", {}).get("top_regions", []):
            f.write(
                f"| {item['rank']} | {item['country']} | "
                f"{item['views']:,} | {item['percentage']:.1f}% |\n"
            )

        # デバイス別分析
        f.write("\n## 📱 デバイス別視聴傾向\n\n")
        device = data.get("device_analysis", {})
        f.write(f"- **モバイル**: {device.get('mobile_percentage', 0)}%\n")
        f.write(f"- **デスクトップ**: {device.get('desktop_percentage', 0)}%\n")
        f.write(f"- **タブレット**: {device.get('tablet_percentage', 0)}%\n")
        f.write(f"\n**主要デバイス**: {device.get('dominant_device', 'データなし')}\n")

    print(f"Markdownレポートを保存しました: {report_file}")


def main():
    """メイン処理: デモグラフィック調査を実行"""
    project_root = Path(__file__).parent.parent
    output_file = str(project_root / "data" / "demographics.json")

    print("視聴者デモグラフィック調査を開始します...")

    # 各カテゴリのデモグラフィックを取得
    categories = ["男の娘", "ニューハーフ"]
    all_demographics = []

    for category in categories:
        demo_data = fetch_viewer_demographics(category)

        # 地域別・デバイス別分析を実行
        regional_analysis = analyze_regional_data(demo_data)
        device_analysis = analyze_device_data(demo_data)

        all_demographics.append({
            "category": category,
            "regional_analysis": regional_analysis,
            "device_analysis": device_analysis
        })

    # 結果をまとめる
    result = {
        "last_updated": datetime.now().isoformat(),
        "categories": all_demographics,
        "regional": {},
        "device": {},
        "age_groups": {}
    }

    # 保存
    save_demographics_report(result, output_file)
    print("視聴者デモグラフィック調査が完了しました！")


if __name__ == "__main__":
    main()
