#!/usr/bin/env python3
"""
把 data/images/home/ 下的圖檔簡化命名。

規則（修正版）：
  每個編號（0001, 0002, …）只保留兩個檔案：
    - 優先選「沒有 shiny」的圖 → 0001.png
    - 優先選「有 shiny」的圖   → 0001-shiny.png
  其餘全部刪除

使用方式：
  # 先預覽（不會改任何檔案）
  python rename_home_images.py

  # 確認無誤後真正執行
  python rename_home_images.py --apply
"""

import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path

HOME_DIR = Path("data/images/home")


def is_shiny(name: str) -> bool:
    return "-shiny" in name.lower()


def pick_best(files, prefer_shiny: bool):
    """從候選中挑一個最合適的。prefer_shiny=True 時優先 shiny，否則優先非 shiny。"""
    if not files:
        return None
    preferred = [p for p in files if is_shiny(p.name) == prefer_shiny]
    candidates = preferred if preferred else files
    # 在符合的裡面選檔名最短的（通常是最基本的型態）
    candidates.sort(key=lambda p: (len(p.name), p.name))
    return candidates[0]


def main():
    parser = argparse.ArgumentParser(description="簡化 home 圖檔命名")
    parser.add_argument("--apply", action="store_true", help="真正執行改名／刪除（預設只預覽）")
    parser.add_argument("--dir", default=str(HOME_DIR), help="圖檔目錄（預設 data/images/home）")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"找不到目錄：{root}")
        sys.exit(1)

    # 收集所有 png，依 4 位編號分組
    groups = defaultdict(list)
    for p in root.iterdir():
        if p.suffix.lower() != ".png":
            continue
        name = p.name
        if len(name) < 4 or not name[:4].isdigit():
            print(f"[略過] 無法辨識編號：{name}")
            continue
        idx = name[:4]
        groups[idx].append(p)

    if not groups:
        print("沒有找到任何 png 檔。")
        return

    plan_rename = []  # (src, dst)
    plan_delete = []  # path
    used = set()

    for idx in sorted(groups.keys()):
        files = groups[idx]

        normal = pick_best(files, prefer_shiny=False)
        shiny = pick_best(files, prefer_shiny=True)

        # 避免同一個檔被選兩次（例如該編號只有 shiny）
        if normal and shiny and normal.resolve() == shiny.resolve():
            shiny = None

        if normal:
            dst = root / f"{idx}.png"
            if normal.resolve() != dst.resolve():
                plan_rename.append((normal, dst))
            used.add(normal.resolve())

        if shiny:
            dst = root / f"{idx}-shiny.png"
            if shiny.resolve() != dst.resolve():
                plan_rename.append((shiny, dst))
            used.add(shiny.resolve())

        for p in files:
            if p.resolve() not in used:
                plan_delete.append(p)

    # 輸出計畫
    print(f"目錄：{root}")
    print(f"共 {len(groups)} 個編號，{sum(len(v) for v in groups.values())} 個檔案")
    print(f"預計改名：{len(plan_rename)} 個")
    print(f"預計刪除：{len(plan_delete)} 個")
    print("-" * 50)

    show = 14
    for src, dst in plan_rename[:show]:
        print(f"  改名  {src.name}  →  {dst.name}")
    if len(plan_rename) > show:
        print(f"  ... 還有 {len(plan_rename) - show} 個改名")

    if plan_delete:
        print()
        for p in plan_delete[:8]:
            print(f"  刪除  {p.name}")
        if len(plan_delete) > 8:
            print(f"  ... 還有 {len(plan_delete) - 8} 個刪除")

    if not args.apply:
        print()
        print("※ 目前是預覽模式，沒有任何檔案被更動。")
        print("  確認沒問題後請加上 --apply 再執行一次：")
        print("  python .\\rename_home_images.py --apply")
        return

    # 真正執行（兩階段暫存，避免名稱衝突）
    print()
    print("開始執行…")

    temp_pairs = []
    for i, (src, dst) in enumerate(plan_rename):
        temp = root / f"__tmp_rename_{i:04d}_{dst.name}"
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


if __name__ == "__main__":
    main()
