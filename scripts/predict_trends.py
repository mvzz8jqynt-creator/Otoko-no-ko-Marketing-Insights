"""
predict_trends.py - タイムベースのトレンド予測スクリプト
個人利用目的のみ

過去データから将来のトレンドを予測（線形回帰・移動平均）し、
ジャンル・タグの人気ピーク時期と「今後3ヶ月で伸びそうなジャンル」TOP5を提示する。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


def load_historical_data(data_dir: str) -> dict:
    """
    データディレクトリから履歴データを読み込む。

    Args:
        data_dir: データディレクトリのパス

    Returns:
        履歴データ辞書 {"tag/genre": [(date, count), ...], ...}
    """
    historical = {}
    data_path = Path(data_dir)

    # タグ分析データを読み込む
    tags_file = data_path / "tags_analysis.json"
    if tags_file.exists():
        try:
            with open(tags_file, "r", encoding="utf-8") as f:
                tags_data = json.load(f)

            # 時系列データを読み込む
            for tag, time_series in tags_data.get("time_series", {}).items():
                historical[tag] = [(entry["date"], entry["count"]) for entry in time_series]
        except (json.JSONDecodeError, IOError) as e:
            print(f"タグデータ読み込みエラー: {e}")

    return historical


def _calculate_moving_average(values: list, window: int = 3) -> list:
    """
    移動平均を計算する（内部関数）。

    Args:
        values: 数値リスト
        window: 移動平均のウィンドウサイズ

    Returns:
        移動平均リスト
    """
    if len(values) < window:
        return values

    moving_avg = []
    for i in range(len(values)):
        if i < window - 1:
            moving_avg.append(values[i])
        else:
            avg = sum(values[i - window + 1:i + 1]) / window
            moving_avg.append(avg)

    return moving_avg


def _linear_regression(x_values: list, y_values: list) -> tuple:
    """
    線形回帰を計算する（内部関数）。

    Args:
        x_values: X軸の値リスト
        y_values: Y軸の値リスト

    Returns:
        (傾き, 切片) のタプル
    """
    n = len(x_values)
    if n < 2:
        return 0.0, y_values[0] if y_values else 0.0

    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x ** 2 for x in x_values)

    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        return 0.0, sum_y / n

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n

    return slope, intercept


def predict_future_trends(data: dict, months: int = 3) -> list:
    """
    過去データから将来のトレンドを予測する（線形回帰使用）。

    Args:
        data: 履歴データ {"tag/genre": [(date_str, count), ...], ...}
        months: 予測する月数（デフォルト3）

    Returns:
        予測リスト [{"tag": str, "current_trend": float, "predicted_growth": float}, ...]
    """
    predictions = []

    for tag, time_series in data.items():
        if not time_series:
            continue

        # 数値のみ取り出す
        counts = [entry[1] for entry in time_series]

        if len(counts) < 2:
            continue

        # X軸は時間インデックス
        x_values = list(range(len(counts)))
        slope, intercept = _linear_regression(x_values, counts)

        # 移動平均でトレンドを平滑化
        moving_avg = _calculate_moving_average(counts)
        latest_avg = moving_avg[-1] if moving_avg else 0

        # 将来の予測値を計算
        future_x = len(counts) + months
        predicted_value = slope * future_x + intercept

        # 成長率を計算
        if latest_avg > 0:
            growth_rate = (predicted_value - latest_avg) / latest_avg * 100
        else:
            growth_rate = 0.0

        predictions.append({
            "tag": tag,
            "current_value": latest_avg,
            "predicted_value": max(0, predicted_value),
            "growth_rate": round(growth_rate, 2),
            "trend_direction": "上昇" if slope > 0 else "下降"
        })

    # 成長率でソート
    predictions.sort(key=lambda x: x["growth_rate"], reverse=True)

    return predictions


def identify_peak_periods(tag_data: dict) -> dict:
    """
    ジャンル・タグの人気ピーク時期を特定する。

    Args:
        tag_data: タグの時系列データ {"tag": [(date_str, count), ...], ...}

    Returns:
        ピーク時期辞書 {"tag": {"peak_date": str, "peak_count": int}, ...}
    """
    peak_periods = {}

    for tag, time_series in tag_data.items():
        if not time_series:
            continue

        # 最大値を持つ日付を特定
        max_entry = max(time_series, key=lambda x: x[1])
        peak_periods[tag] = {
            "peak_date": max_entry[0],
            "peak_count": max_entry[1]
        }

    return peak_periods


def generate_trend_forecast(data: dict) -> dict:
    """
    包括的なトレンド予測レポートを生成する。

    Args:
        data: 履歴データ

    Returns:
        トレンド予測データ
    """
    # 3ヶ月先を予測
    predictions = predict_future_trends(data, months=3)

    # TOP5の伸びそうなジャンルを特定
    top5_growing = [
        p for p in predictions if p["trend_direction"] == "上昇"
    ][:5]

    # ピーク時期を特定
    peak_periods = identify_peak_periods(data)

    return {
        "last_updated": datetime.now().isoformat(),
        "prediction_period": f"{months}ヶ月先",
        "all_predictions": predictions,
        "top5_growing_genres": top5_growing,
        "peak_periods": peak_periods,
        "forecast_date": (datetime.now() + timedelta(days=90)).isoformat()
    }


def save_trend_forecast(data: dict, output_file: str) -> None:
    """
    トレンド予測データをJSONとMarkdownに保存する。

    Args:
        data: トレンド予測データ
        output_file: 出力JSONファイルのパス
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSONを保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"トレンド予測データを保存しました: {output_file}")

    # Markdownレポートを生成
    report_dir = output_path.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "trend_forecast_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# トレンド予測レポート\n\n")
        f.write(f"生成日時: {data.get('last_updated', '不明')}\n\n")

        f.write("## 🔮 今後3ヶ月で伸びそうなジャンル TOP5\n\n")
        f.write("| ランク | ジャンル/タグ | 予測成長率 | トレンド |\n")
        f.write("|--------|--------------|------------|----------|\n")
        for i, genre in enumerate(data.get("top5_growing_genres", []), 1):
            f.write(
                f"| {i} | {genre['tag']} | "
                f"{genre['growth_rate']:.1f}% | {genre['trend_direction']} |\n"
            )

        f.write("\n## 📈 全体予測サマリー\n\n")
        all_pred = data.get("all_predictions", [])
        if all_pred:
            f.write(f"- 分析タグ数: {len(all_pred)}\n")
            rising = len([p for p in all_pred if p["trend_direction"] == "上昇"])
            f.write(f"- 上昇トレンド: {rising}件\n")
            f.write(f"- 下降トレンド: {len(all_pred) - rising}件\n")
        else:
            f.write("履歴データがありません。データ収集後に再実行してください。\n")

    print(f"Markdownレポートを保存しました: {report_file}")


# モジュールレベルでも使用できるように変数を定義
months = 3


def main():
    """メイン処理: トレンド予測を実行"""
    project_root = Path(__file__).parent.parent
    data_dir = str(project_root / "data")
    output_file = str(project_root / "data" / "trend_forecast.json")

    print("トレンド予測を開始します...")

    # 履歴データを読み込む
    historical_data = load_historical_data(data_dir)
    print(f"履歴データ件数: {len(historical_data)}")

    # トレンド予測を生成
    forecast = generate_trend_forecast(historical_data)

    # 保存
    save_trend_forecast(forecast, output_file)
    print("トレンド予測が完了しました！")


if __name__ == "__main__":
    main()
