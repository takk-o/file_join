"""フォルダ内の CSV・Excel ファイルを 1 つのファイルに結合する"""

import argparse
import sys
from pathlib import Path

import pandas as pd

ENCODINGS = ("utf-8-sig", "cp932")  # 自動判定で試す順（cp932 は Shift_JIS の Windows 拡張）


def find_files(folder: Path) -> list[Path]:
    files = [
        p for p in sorted(folder.iterdir())
        if p.suffix.lower() in (".csv", ".xlsx") and not p.name.startswith(("~$", "."))
    ]
    if not files:
        sys.exit(f"{folder} に CSV・Excel（.xlsx）ファイルがありません。")
    return files


def read_csv(path: Path, encoding: str, **kwargs) -> pd.DataFrame:
    if encoding != "auto":
        return pd.read_csv(path, encoding=encoding, **kwargs)
    for enc in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"{path.name} の文字コードを判定できません。--encoding で指定してください。")


def read_table(path: Path, args: argparse.Namespace, header_only: bool = False) -> pd.DataFrame:
    nrows = 0 if header_only else None
    if path.suffix.lower() == ".csv":
        # 文字列として読む（001 のような先頭の 0 を残す）
        return read_csv(path, args.encoding, dtype=str, keep_default_na=False,
                        skiprows=args.skiprows, nrows=nrows)
    return pd.read_excel(path, sheet_name=args.sheet, skiprows=args.skiprows, nrows=nrows)


def filename_values(path: Path, names: list[str], sep: str) -> list[str]:
    parts = path.stem.split(sep)
    if len(parts) < len(names):
        print(f"  注意：{path.name} は「{sep}」で {len(names)} つに分けられません。足りない列は空欄にします。",
              file=sys.stderr)
    return (parts + [""] * len(names))[: len(names)]


def join(files: list[Path], args: argparse.Namespace) -> pd.DataFrame:
    names = args.filename_columns.split(",") if args.filename_columns else []
    frames = []
    for path in files:
        df = read_table(path, args)
        for name, value in zip(names, filename_values(path, names, args.sep)):
            df[name] = value
        if args.add_filename:
            df.insert(0, "ファイル名", path.name)
        print(f"{path.name}: {len(df)} 行")
        frames.append(df)
    return pd.concat(frames, axis=0, ignore_index=True, sort=False)


def list_columns(files: list[Path], args: argparse.Namespace) -> pd.DataFrame:
    rows = [[path.name, *map(str, read_table(path, args, header_only=True).columns)] for path in files]
    width = max(len(r) for r in rows)
    header = ["ファイル名"] + [f"列{i}" for i in range(1, width)]
    return pd.DataFrame([r + [""] * (width - len(r)) for r in rows], columns=header)


def save(df: pd.DataFrame, path: Path, output_encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".xlsx":
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False, encoding=output_encoding)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="input", type=Path,
                        help="結合するファイルを置いたフォルダ（既定：input）")
    parser.add_argument("-o", "--output", type=Path, default=Path("output/join.csv"),
                        help="出力先。拡張子 .xlsx なら Excel、それ以外は CSV（既定：output/join.csv）")
    parser.add_argument("--columns", action="store_true",
                        help="結合せず、ファイルごとの列名（見出し）だけを一覧にする")
    parser.add_argument("--add-filename", action="store_true",
                        help="先頭に「ファイル名」の列を追加する")
    parser.add_argument("--filename-columns", metavar="列名,列名,...",
                        help="ファイル名を --sep で分けた値を、指定した名前の列として追加する（例：年次,部署,役職）")
    parser.add_argument("--sep", default="_", help="--filename-columns で使う区切り文字（既定：_）")
    parser.add_argument("--encoding", default="auto",
                        help="CSV の文字コード。auto は UTF-8 と Shift_JIS を自動判定（既定：auto）")
    parser.add_argument("--output-encoding", default="utf-8-sig",
                        help="出力する CSV の文字コード（既定：utf-8-sig。Excel で開いても文字化けしない）")
    parser.add_argument("--sheet", default=0,
                        help="Excel で読むシート。名前か 0 から数えた番号（既定：0 = 最初のシート）")
    parser.add_argument("--skiprows", type=int, default=0,
                        help="見出しの前にある、読み飛ばす行の数（タイトル行がある表など。既定：0）")
    args = parser.parse_args()
    if isinstance(args.sheet, str) and args.sheet.isdigit():
        args.sheet = int(args.sheet)

    if not args.input.is_dir():
        sys.exit(f"フォルダが見つかりません：{args.input}")
    files = find_files(args.input)

    try:
        df = list_columns(files, args) if args.columns else join(files, args)
    except (ValueError, KeyError) as e:
        sys.exit(f"読み込みに失敗しました：{e}")

    save(df, args.output, args.output_encoding)
    what = f"{len(files)} ファイル分の列名" if args.columns else f"合計 {len(df)} 行"
    print(f"{what}を {args.output} に出力しました")


if __name__ == "__main__":
    main()
