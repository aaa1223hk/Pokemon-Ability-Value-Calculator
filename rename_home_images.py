#!/usr/bin/env python3
"""
把 data/images/home/ 下的圖檔簡化命名。

規則（依 sorted 排序，近似 ls）：
  每個編號（0001, 0002, …）只保留前兩個檔案：
    第 1 個 → 0001.png
    第 2 個 → 0001-shiny.png
  第 3 個以後 → 刪除

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

    for idx in sorted(groups.keys()):
        files = sorted(groups[idx], key=lambda p: p.name)  # 近似 ls 排序

        for i, src in enumerate(files):
            if i == 0:
                dst = root / f"{idx}.png"
                if src.resolve() != dst.resolve():
                    plan_rename.append((src, dst))
            elif i == 1:
                dst = root / f"{idx}-shiny.png"
                if src.resolve() != dst.resolve():
                    plan_rename.append((src, dst))
            else:
                plan_delete.append(src)

    # 輸出計畫
    print(f"目錄：{root}")
    print(f"共 {len(groups)} 個編號，{sum(len(v) for v in groups.values())} 個檔案")
    print(f"預計改名：{len(plan_rename)} 個")
    print(f"預計刪除：{len(plan_delete)} 個")
    print("-" * 50)

    # 顯示前幾個範例
    show = 12
    for src, dst in plan_rename[:show]:
        print(f"  改名  {src.name}  →  {dst.name}")
    if len(plan_rename) > show:
        print(f"  ... 還有 {len(plan_rename) - show} 個改名")

    if plan_delete:
        print()
        for p in plan_delete[:show]:
            print(f"  刪除  {p.name}")
        if len(plan_delete) > show:
            print(f"  ... 還有 {len(plan_delete) - show} 個刪除")

    if not args.apply:
        print()
        print("※ 目前是預覽模式，沒有任何檔案被更動。")
        print("  確認沒問題後請加上 --apply 再執行一次：")
        print("  python rename_home_images.py --apply")
        return

    # 真正執行
    print()
    print("開始執行…")

    # 先處理可能的目標檔名衝突：若目標已存在且不是來源本身，先刪除或改暫名
    # 為了安全，用兩階段：先全部改成暫名，再改成最終名
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
                dst.unlink()  # 覆蓋舊的同名檔（極少見）
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
