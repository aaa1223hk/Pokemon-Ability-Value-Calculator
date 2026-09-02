#!/usr/bin/env python3
"""
把 data/pokemon/ 下的 JSON 簡化命名。

規則：
  0001-妙蛙种子.json  →  0001.json
  0002-妙蛙草.json    →  0002.json
  ...

每個編號預期只有一個檔案。若有多個，取檔名最短的那個，其餘刪除。

使用方式：
  # 先預覽
  python rename_pokemon_json.py

  # 確認後真正執行
  python rename_pokemon_json.py --apply
"""

import sys
import argparse
from collections import defaultdict
from pathlib import Path

POKE_DIR = Path("data/pokemon")


def main():
    parser = argparse.ArgumentParser(description="簡化 pokemon JSON 檔名")
    parser.add_argument("--apply", action="store_true", help="真正執行改名／刪除（預設只預覽）")
    parser.add_argument("--dir", default=str(POKE_DIR), help="目錄（預設 data/pokemon）")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"找不到目錄：{root}")
        sys.exit(1)

    groups = defaultdict(list)
    for p in root.iterdir():
        if p.suffix.lower() != ".json":
            continue
        name = p.name
        if len(name) < 4 or not name[:4].isdigit():
            print(f"[略過] 無法辨識編號：{name}")
            continue
        idx = name[:4]
        groups[idx].append(p)

    if not groups:
        print("沒有找到任何 json 檔。")
        return

    plan_rename = []
    plan_delete = []

    for idx in sorted(groups.keys()):
        files = groups[idx]
        # 選檔名最短的作為主檔（通常是基本型）
        files.sort(key=lambda p: (len(p.name), p.name))
        main = files[0]
        dst = root / f"{idx}.json"

        if main.resolve() != dst.resolve():
            plan_rename.append((main, dst))

        for extra in files[1:]:
            plan_delete.append(extra)

    print(f"目錄：{root}")
    print(f"共 {len(groups)} 個編號，{sum(len(v) for v in groups.values())} 個檔案")
    print(f"預計改名：{len(plan_rename)} 個")
    print(f"預計刪除：{len(plan_delete)} 個")
    print("-" * 50)

    show = 12
    for src, dst in plan_rename[:show]:
        print(f"  改名  {src.name}  →  {dst.name}")
    if len(plan_rename) > show:
        print(f"  ... 還有 {len(plan_rename) - show} 個改名")

    if plan_delete:
        print()
        for p in plan_delete[:6]:
            print(f"  刪除  {p.name}")
        if len(plan_delete) > 6:
            print(f"  ... 還有 {len(plan_delete) - 6} 個刪除")

    if not args.apply:
        print()
        print("※ 目前是預覽模式，沒有任何檔案被更動。")
        print("  確認沒問題後請加上 --apply 再執行一次：")
        print("  python .\\rename_pokemon_json.py --apply")
        return

    print()
    print("開始執行…")

    # 兩階段暫存，避免衝突
    temp_pairs = []
    for i, (src, dst) in enumerate(plan_rename):
        temp = root / f"__tmp_poke_{i:04d}_{dst.name}"
        try:
            src.rename(temp)
            temp_pairs.append((temp, dst))
        except Exception as e:
            print(f"  [失敗] {src.name} → 暫存：{e}")

    for temp, dst in temp_pairs:
        try:
            if dst.exists():
                dst.unlink()
            temp.rename(dst)
            print(f"  ✓ {dst.name}")
        except Exception as e:
            print(f"  [失敗] {temp.name} → {dst.name}：{e}")

    for p in plan_delete:
        try:
            p.unlink()
            print(f"  ✗ 已刪 {p.name}")
        except Exception as e:
            print(f"  [失敗] 刪除 {p.name}：{e}")

    print()
    print("完成。")
    print("提醒：改完後記得更新 index_to_pokemon.json（或讓前端直接用 0001.json）。")


if __name__ == "__main__":
    main()
