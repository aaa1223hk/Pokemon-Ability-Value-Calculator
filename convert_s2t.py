import os
import json
from opencc import OpenCC

# 初始化轉換器：簡體 → 繁體（台灣標準）
cc = OpenCC('s2twp')  # 如果想用更通用的可改成 's2t'

def convert_value(value):
    """遞迴處理字串、list、dict"""
    if isinstance(value, str):
        return cc.convert(value)
    elif isinstance(value, list):
        return [convert_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: convert_value(v) for k, v in value.items()}
    else:
        return value

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        converted = convert_value(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(converted, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已轉換：{os.path.basename(filepath)}")
    except Exception as e:
        print(f"✗ 失敗 {filepath}：{e}")

def main():
    abilities_dir = r"data/1"  # 確認這個路徑是否正確
    
    if not os.path.isdir(abilities_dir):
        print(f"找不到資料夾：{abilities_dir}")
        print("請確認 data/1 資料夾是否存在於目前目錄下")
        return
    
    files = [f for f in os.listdir(abilities_dir) if f.endswith('.json')]
    print(f"共找到 {len(files)} 個 JSON 檔，開始轉換...")
    
    for filename in files:
        filepath = os.path.join(abilities_dir, filename)
        process_file(filepath)
    
    print("全部完成。")

if __name__ == "__main__":
    main()