#!/usr/bin/env python3
"""
把指定目錄內的檔名由簡體轉繁體（台灣用語 s2twp）。

預設目標：./1/

使用方式：
  # 預覽（不真正改名）
  python rename_s2t_filenames.py

  # 真正執行改名
  python rename_s2t_filenames.py --apply

  # 指定其他目錄
  python rename_s2t_filenames.py --dir data/images/home --apply
"""

import os
import sys
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

DEFAULT_DIR = Path("1")


def main():
    parser = argparse.ArgumentParser(description="檔名簡體 → 繁體（s2twp）")
    parser.add_argument("--apply", action="store_true", help="真正改名（預設只預覽）")
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="目標目錄（預設 1）")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"找不到目錄：{root.resolve()}")
        sys.exit(1)

    files = sorted([p for p in root.iterdir() if p.is_file()])
    print(f"目錄：{root.resolve()}")
    print(f"共找到 {len(files)} 個檔案")
    if not args.apply:
        print("※ 預覽模式，不會真正改名。加上 --apply 才會執行。")
    print("-" * 60)

    renamed = 0
    skipped = 0
    conflicts = 0
    errors = 0

    for i, fp in enumerate(files, 1):
        old_name = fp.name
        new_name = cc.convert(old_name)

        if old_name == new_name:
            skipped += 1
            if i <= 3 or i == len(files):
                print(f"  · 無需變更：{old_name}")
            elif i == 4:
                print(f"  · ...")
            continue

        new_path = fp.with_name(new_name)

        if new_path.exists() and new_path != fp:
            print(f"  ✗ 衝突跳過：{old_name}  →  {new_name}（目標已存在）")
            conflicts += 1
            continue

        if args.apply:
            try:
                fp.rename(new_path)
                print(f"  ✓ [{i}/{len(files)}] {old_name}  →  {new_name}")
                renamed += 1
            except Exception as e:
                print(f"  ✗ 失敗 {old_name}：{e}")
                errors += 1
        else:
            if renamed + skipped < 12 or i == len(files):
                print(f"  · 將改名：{old_name}  →  {new_name}")
            elif renamed + skipped == 12:
                print(f"  · ...")
            renamed += 1  # 預覽計數

    print("-" * 60)
    if args.apply:
        print(f"完成：成功改名 {renamed}，跳過（已是繁體）{skipped}，衝突 {conflicts}，失敗 {errors}")
    else:
        print(f"預覽：將改名 {renamed} 個，無需變更 {skipped} 個，潛在衝突 {conflicts} 個")
        print()
        print("確認後執行：")
        print(f"  python rename_s2t_filenames.py --dir {args.dir} --apply")


if __name__ == "__main__":
    main()
