# 特征重要性功能 - 快速开始

## 功能说明

✅ **自动保存特征重要性** - 每次训练都会自动生成  
✅ **特征名称对应准确** - 与训练数据列名完全一致  
✅ **双重输出格式** - CSV文件 + 可视化图表  

## 输出文件

训练完成后，在输出目录中会生成：

### 1️⃣ feature_importance.csv
```csv
feature_name,importance_gain
price_ahead_clear_shift_1,15234.56
jingjiakongjian_shift_1,12987.34
feature_A_lag_1,8765.12
...
```

### 2️⃣ feature_importance.png
- Top 30 特征的水平柱状图
- 最重要的特征在顶部

## 使用方法

### 运行训练
```bash
python main.py --config config_ahead.yaml
```

训练完成后，自动在输出目录生成特征重要性文件

### 查看结果
```python
import pandas as pd

# 读取特征重要性
fi = pd.read_csv('output-ahead-20251027_083127/feature_importance.csv')

# 查看前10个最重要特征
print(fi.head(10))
```

### 分析重要性
```python
# 累积重要性贡献
total = fi['importance_gain'].sum()
fi['cumsum_pct'] = (fi['importance_gain'].cumsum() / total * 100)

# 查看前N个特征贡献多少
print(f"前10个特征贡献: {fi.iloc[9]['cumsum_pct']:.1f}%")
print(f"前20个特征贡献: {fi.iloc[19]['cumsum_pct']:.1f}%")
```

## 应用场景

1. **特征选择** - 去除重要性低的冗余特征
2. **业务理解** - 识别影响预测的关键因素  
3. **模型优化** - 基于重要性改进特征工程
4. **模型解释** - 向业务人员说明模型依据

## 特征重要性类型

- **Gain** (默认): 特征对模型性能提升的平均贡献
- **Weight** (备用): 特征在所有树中被使用的次数

系统优先使用 Gain，如果不可用则自动使用 Weight

## 配置

所有配置文件已默认启用：
```yaml
output:
  save_feature_importance: true
```

## 注意事项

✅ 滞后特征命名格式: `原特征名_lag_N`  
✅ 重要性为0说明特征未被使用  
✅ 完整特征列表请查看CSV文件  
✅ 可视化图表只显示Top 30特征  

## 示例输出目录结构

```
output-ahead-20251027_083127/
├── feature_importance.csv        ← 完整特征重要性列表
├── feature_importance.png        ← Top 30 特征可视化
├── best_params.json
├── eval_summary.json
├── test_predictions.csv
├── xgb_best_model.json
└── ...
```

## 测试

运行测试脚本验证功能：
```bash
python test_feature_importance.py
```

## 更多信息

- 详细说明: `特征重要性说明.md`
- 改进说明: `特征重要性功能改进说明.md`

---

**现在每次训练都会自动保存特征重要性，无需额外操作！**

