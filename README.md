# Otoko-no-ko-Marketing-Insights
男の娘・ニューハーフ向けマーケティング分析ツール
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
import re

# --- マイファンズの投稿データの例 ---
data = {
    "投稿内容": [
        "クーポン配布！期間限定セール開始",
        "新商品リリース！今だけポイント還元",
        "リピーター大歓迎、特別ギフトをプレゼント中",
        "口コミキャンペーン実施中。商品が当たる！",
        "再入荷商品のお知らせ。早い者勝ち！"
    ],
    "フォロワー数": [1000, 1200, 1500, 1100, 1400],
    "いいね数": [200, 350, 400, 220, 300],
    "クリック数": [50, 100, 120, 60, 90],
    "購入数": [20, 35, 45, 15, 30]
}

# データをデータフレームに変換
df = pd.DataFrame(data)

# --- ステップ1: 投稿データの整理 ---
# 基本的な情報を計算
df["いいね率 (%)"] = (df["いいね数"] / df["フォロワー数"]) * 100
df["クリック率 (%)"] = (df["クリック数"] / df["フォロワー数"]) * 100
df["購入率 (%)"] = (df["購入数"] / df["フォロワー数"]) * 100

print("投稿データ:")
print(df)

# --- ステップ2: 投稿パフォーマンスの可視化 ---
# 各投稿のパフォーマンス（いいね率、購入率）を可視化
plt.figure(figsize=(12, 6))
sns.barplot(x="投稿内容", y="いいね率 (%)", data=df, label="いいね率", color="skyblue")
sns.barplot(x="投稿内容", y="購入率 (%)", data=df, label="購入率", color="orange", alpha=0.7)
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.title("投稿データのパフォーマンス分析")
plt.ylabel("率 (%)")
plt.xlabel("投稿内容")
plt.tight_layout()
plt.show()

# --- ステップ3: 評価の高い投稿キーワード分析 ---
# 評価の高い投稿を抽出（購入率が平均以上の場合）
high_performance_df = df[df["購入率 (%)"] > df["購入率 (%)"].mean()]

# 本文から単語を抽出して頻出単語を分析
all_words = []
for text in high_performance_df["投稿内容"]:
    words = re.findall(r'\w+', text)  # 単語を抽出（英語 + 日本語）
    all_words.extend(words)

# 単語頻度をカウント
word_counts = Counter(all_words)
most_common_words = word_counts.most_common(10)

# 頻出単語を表示
print("\n評価の高い投稿で頻出する単語トップ10:")
for word, count in most_common_words:
    print(f"{word}: {count}回")

# --- ステップ4: 購入ファネルの分析 ---
# 各投稿のコンバージョンに至るまでのファネルを可視化
df[["いいね数", "クリック数", "購入数"]].sum().plot(kind="bar", color=["blue", "green", "orange"], figsize=(10, 6))
plt.title("全投稿のマーケティングファネル分析")
plt.ylabel("人数")
plt.xticks(ticks=[0, 1, 2], labels=["いいね数", "クリック数", "購入数"])
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# --- ステップ5: 改善戦略の提案 ---
print("\n【改善アクションプラン】:")
# 頻出単語を基に次回投稿の提案
top_word = most_common_words[0][0] if most_common_words else "特典"
print(f"- 頻出単語『{top_word}』を活用した投稿を試してください。")
# パフォーマンス指標に基づくアクション
if df["購入率 (%)"].mean() < 5:
    print("- 全体的な購入率が低いため、購入までの流れをシンプルにして、クリック率を上げる工夫を。")
elif df["購入率 (%)"].mean() >= 5:
    print("- 購入率が平均以上です。現在の投稿戦略を元に、特定の要素（例: キーワード/タイミング）の効果を深掘りしてください。")
