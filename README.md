# file_join

フォルダに置いた複数の CSV・Excel ファイルを、1 つのファイルに結合するコマンドラインツールです。

```
$ uv run file_join.py --filename-columns 年次,部署,役職
2024_営業部_課長.csv: 2 行
2025_総務部_部長.csv: 1 行
合計 3 行を output/join.csv に出力しました
```

## 特徴

- CSV（`.csv`）と Excel（`.xlsx`）に対応し、混在していても結合できます
- 列名が違うファイルが混ざっても、すべての列を並べて結合します（ない値は空欄）
- CSV の文字コード（UTF-8 / Shift_JIS）を自動で判定します
- CSV はすべて文字列として読むので、`001` のような先頭の 0 が消えません
- ファイル名に含まれる情報（年度や部署など）を列として追加できます
- 出力する CSV は、Excel で開いても文字化けしない BOM 付き UTF-8 です

## セットアップ

[uv](https://docs.astral.sh/uv/) を使います。

```sh
git clone https://github.com/takk-o/file_join.git
cd file_join
uv sync
```

## 使い方

結合したいファイルを `input/` に置いて実行します。結果は `output/join.csv` に保存されます（上書き）。

```sh
uv run file_join.py
```

フォルダや出力先を変えるときは、次のように指定します。出力先の拡張子が `.xlsx` なら Excel で保存します。

```sh
uv run file_join.py ~/Downloads/monthly -o output/monthly.xlsx
```

### よく使うオプション

| オプション | 内容 |
|---|---|
| `--columns` | 結合せず、ファイルごとの列名（見出し）だけを一覧にする。結合の前に見出しの違いを確かめるのに使う |
| `--add-filename` | 先頭に「ファイル名」の列を追加する |
| `--filename-columns 年次,部署,役職` | ファイル名を `_` で分けた値を、指定した名前の列として追加する（例：`2024_営業部_課長.csv`）。区切り文字は `--sep` で変更 |
| `--encoding shift_jis` | CSV の文字コードを指定する（既定は自動判定） |
| `--sheet 売上` | Excel で読むシートを名前か番号で指定する（既定は最初のシート） |
| `--skiprows 2` | 見出しの前のタイトル行などを読み飛ばす |

すべてのオプションは `uv run file_join.py -h` で確認できます。

## 注意

- 各ファイルの 1 行目（`--skiprows` で読み飛ばした後の最初の行）を見出しとして扱います。
- 列名の綴りが少しでも違うと、別の列として並びます。先に `--columns` で確かめると確実です。
- Excel の書式（色や罫線）は引き継ぎません。`.xls` や `.xlsm` は対象外です。
- `input/` と `output/` は Git の対象外にしてあります。

## ライセンス

[MIT](LICENSE)
