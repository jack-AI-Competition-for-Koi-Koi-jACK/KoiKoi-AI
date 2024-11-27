import csv

# 入力CSVファイル名
input_file = "yaku_results.csv"
# 出力CSVファイル名
output_file = "yaku_results_sum.csv"

# CSVを処理する
with open(input_file, mode="r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)  # ヘッダーを取得
    rows = list(reader)  # データをリストとして取得

# 各列の和を計算
column_sums = [
    sum(float(row[i]) for row in rows if row[i])  # 空セルを無視
    for i in range(len(header))
]

# 結果を新しいCSVに保存
with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)  # ヘッダーを書き込み
    writer.writerow(column_sums)  # 列方向の和を書き込み

print(f"処理が完了しました。結果は '{output_file}' に保存されています。")
