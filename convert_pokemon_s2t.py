#!/usr/bin/env python3
"""
把 data/pokemon/ 下所有 JSON 的字串從簡體轉繁體（台灣用語 s2twp）。

使用 OpenCC：
  pip install opencc-python-reimplemented
  或  pip install opencc

使用方式：
  # 預覽會轉哪些檔（不寫入）
  python convert_pokemon_s2t.py

  # 真正轉換並覆寫
  python convert_pokemon_s2t.py --apply
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from opencc import OpenCC
except ImportError:
    print("請先安裝 OpenCC：")
    print("  pip install opencc-python-reimplemented")
    print("  或  pip install opencc")
    sys.exit(1)

cc = OpenCC("s2twp")  # 簡體 → 繁體（台灣）

POKE_DIR = Path("data/pokemon")


def convert_value(value):
    if isinstance(value, str):
        return cc.convert(value)
    elif isinstance(value, list):
        return [convert_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: convert_value(v) for k, v in value.items()}
    else:
        return value


def process_file(filepath: Path, apply: bool) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        converted = convert_value(data)
        if apply:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(converted, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ✗ 失敗 {filepath.name}：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="pokemon JSON 簡轉繁")
    parser.add_argument("--apply", action="store_true", help="真正寫入（預設只預覽）")
    parser.add_argument("--dir", default=str(POKE_DIR), help="目錄（預設 data/pokemon）")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"找不到目錄：{root}")
        sys.exit(1)

    files = sorted([p for p in root.iterdir() if p.suffix.lower() == ".json"])
    print(f"目錄：{root}")
    print(f"共找到 {len(files)} 個 JSON 檔")
    if not args.apply:
        print("※ 預覽模式，不會寫入檔案。加上 --apply 才會真正轉換。")
    print("-" * 40)

    ok = 0
    for i, fp in enumerate(files, 1):
        success = process_file(fp, args.apply)
        if success:
            ok += 1
            if args.apply:
                print(f"  ✓ [{i}/{len(files)}] {fp.name}")
            elif i <= 5 or i == len(files):
                print(f"  · 將轉換 {fp.name}")
            elif i == 6:
                print(f"  · ...")

    print("-" * 40)
    print(f"完成：{ok}/{len(files)}")
    if not args.apply:
        print()
        print("確認後執行：")
        print("  python .\\convert_pokemon_s2t.py --apply")


if __name__ == "__main__":
    main()
