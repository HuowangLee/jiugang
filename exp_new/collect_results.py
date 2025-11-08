import os
import json
import pandas as pd
import shutil
from pathlib import Path

# 获取项目根目录
root_dir = Path(__file__).parent.parent
exp_new_dir = root_dir / "exp_new"

# 确保exp_new目录存在
exp_new_dir.mkdir(exist_ok=True)

# 存储所有实验结果
results = []

# 遍历所有output-price-diff开头的文件夹
for folder_name in os.listdir(root_dir):
    if folder_name.startswith("output-price-diff"):
        folder_path = root_dir / folder_name
        
        if not folder_path.is_dir():
            continue
        
        # 读取eval_summary.json
        eval_summary_path = folder_path / "eval_summary.json"
        if eval_summary_path.exists():
            with open(eval_summary_path, 'r', encoding='utf-8') as f:
                eval_data = json.load(f)
            
            # 添加文件夹名称作为实验标识
            eval_data['experiment_name'] = folder_name
            results.append(eval_data)
            
            # 复制agreement_by_date_bar.png
            agreement_img = folder_path / "agreement_by_date_bar.png"
            if agreement_img.exists():
                dest_path = exp_new_dir / f"{folder_name}_agreement_by_date_bar.png"
                shutil.copy2(agreement_img, dest_path)
                print(f"已复制: {folder_name}/agreement_by_date_bar.png")
            
            # 复制feature_importance.png
            feature_img = folder_path / "feature_importance.png"
            if feature_img.exists():
                dest_path = exp_new_dir / f"{folder_name}_feature_importance.png"
                shutil.copy2(feature_img, dest_path)
                print(f"已复制: {folder_name}/feature_importance.png")

# 将结果转换为DataFrame并保存为CSV
if results:
    df = pd.DataFrame(results)
    
    # 将experiment_name列移到第一列
    cols = ['experiment_name'] + [col for col in df.columns if col != 'experiment_name']
    df = df[cols]
    
    # 保存为CSV
    output_csv = exp_new_dir / "eval_summary_all.csv"
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n汇总结果已保存到: {output_csv}")
    print(f"共收集 {len(results)} 个实验结果")
else:
    print("未找到任何实验结果")

