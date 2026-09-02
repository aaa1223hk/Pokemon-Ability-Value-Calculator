#!/usr/bin/env python3
"""
寶可夢資料庫 簡體 → 繁體（台灣用語）批次轉換腳本

涵蓋：
  - data/pokemon/*.json          （招式表主要來源：learnable_moves / machine_moves / egg_moves）
  - data/moves/*.json            （招式詳細資料）
  - data/abilities/*.json        （特性詳細資料）
  - data/move_list.json
  - data/ability_list.json
  - data/item_list.json
  - data/simple_pokedex.json

使用 OpenCC s2twp（簡體 → 繁體台灣）。

使用方式：
  # 預覽（不寫入）
  python convert_all_s2t.py

  # 真正轉換並覆寫
  python convert_all_s2t.py --apply

  # 只處理指定目錄
  python convert_all_s2t.py --apply --only pokemon
  python convert_all_s2t.py --apply --only moves,abilities,lists
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

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

TARGETS = {
    "pokemon": DATA / "pokemon",
    "moves": DATA / "moves",
    "abilities": DATA / "abilities",
    "lists": [
        DATA / "move_list.json",
        DATA / "ability_list.json",
        DATA / "item_list.json",
        DATA / "simple_pokedex.json",
    ],
}


def convert_value(value):
    """遞迴轉換字串、list、dict"""
    if isinstance(value, str):
        return cc.convert(value)
    elif isinstance(value, list):
        return [convert_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: convert_value(v) for k, v in value.items()}
    else:
        return value


def process_json_file(filepath: Path, apply: bool) -> tuple[bool, str]:
    """處理單一 JSON 檔，回傳 (成功, 訊息)"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        converted = convert_value(data)

        # 簡單檢查是否有實際變更
        original_text = json.dumps(data, ensure_ascii=False)
        new_text = json.dumps(converted, ensure_ascii=False)
        changed = original_text != new_text

        if apply and changed:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(converted, f, ensure_ascii=False, indent=2)

        return True, "changed" if changed else "unchanged"
    except Exception as e:
        return False, str(e)


def collect_files(only: set[str] | None) -> list[Path]:
    files = []
    for key, target in TARGETS.items():
        if only and key not in only:
            continue
        if isinstance(target, list):
            for p in target:
                if p.is_file():
                    files.append(p)
        elif target.is_dir():
            files.extend(sorted(p for p in target.glob("*.json")))
    return files


def main():
    parser = argparse.ArgumentParser(description="寶可夢資料 簡轉繁（s2twp）")
    parser.add_argument("--apply", action="store_true", help="真正寫入（預設只預覽）")
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="只處理指定目標，逗號分隔：pokemon,moves,abilities,lists",
    )
    args = parser.parse_args()

    only = set(x.strip() for x in args.only.split(",") if x.strip()) or None

    files = collect_files(only)
    if not files:
        print("找不到任何目標檔案。")
        sys.exit(1)

    print(f"目標：{', '.join(only) if only else '全部'}")
    print(f"共找到 {len(files)} 個 JSON 檔")
    if not args.apply:
        print("※ 預覽模式，不會寫入檔案。加上 --apply 才會真正轉換。")
    print("-" * 50)

    ok = 0
    changed_count = 0
    fail = 0
    samples = []

    for i, fp in enumerate(files, 1):
        success, status = process_json_file(fp, args.apply)
        if success:
            ok += 1
            if status == "changed":
                changed_count += 1
                if len(samples) < 8:
                    samples.append(fp.relative_to(ROOT))
            if args.apply and status == "changed":
                print(f"  ✓ [{i}/{len(files)}] {fp.relative_to(ROOT)}")
            elif not args.apply and (i <= 3 or i == len(files)):
                print(f"  · 將檢查 {fp.relative_to(ROOT)}")
            elif not args.apply and i == 4:
                print(f"  · ...")
        else:
            fail += 1
            print(f"  ✗ {fp.relative_to(ROOT)}：{status}")

    print("-" * 50)
    print(f"完成：成功 {ok}/{len(files)}，有變更 {changed_count}，失敗 {fail}")
    if samples:
        print("範例有變更的檔案：")
        for s in samples:
            print(f"  - {s}")
    if not args.apply:
        print()
        print("確認後執行：")
        print("  python convert_all_s2t.py --apply")
        print("或只處理 pokemon：")
        print("  python convert_all_s2t.py --apply --only pokemon")


if __name__ == "__main__":
    main()
