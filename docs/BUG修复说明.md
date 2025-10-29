# Bug 修复说明 - 特征重要性保存

## 问题描述

在保存特征重要性时出现错误：
```
保存特征重要性失败: 'NoneType' object is not iterable
TypeError: 'NoneType' object is not iterable
```

## 根本原因

1. **特征名称未传递**: 在训练最终模型时，没有将特征名称传递给 XGBoost 模型
2. **特征名称获取逻辑不完善**: `booster.feature_names` 可能为 `None`，导致迭代失败

## 修复内容

### 1️⃣ 修复 `evaluator.py` - 更稳健的特征名称获取

```python
# 修复前
feature_names = booster.feature_names if hasattr(booster, 'feature_names') else list(imp_dict.keys())

# 修复后
feature_names = None
if hasattr(booster, 'feature_names') and booster.feature_names is not None:
    feature_names = booster.feature_names

# 如果feature_names仍然为None，从imp_dict的keys获取
if feature_names is None:
    feature_names = list(imp_dict.keys())

if not feature_names:
    print("警告: 无法获取特征名称列表")
    return
```

**改进点：**
- ✅ 显式检查 `feature_names` 是否为 `None`
- ✅ 多层防护，确保总能获取到有效的特征名称
- ✅ 增加空列表检查，避免后续错误

### 2️⃣ 修复 `model_trainer.py` - 设置特征名称

```python
def train_final_model(
    self,
    X_train: np.ndarray,
    y_train: np.ndarray,
    sample_weights: np.ndarray = None,
    feature_names: list = None  # 新增参数
):
    # ... 创建模型 ...
    
    # 训练模型
    self.best_model.fit(X_train, y_train, sample_weight=sample_weights)
    
    # 训练后设置特征名称（XGBoost sklearn API 不支持在fit时传递feature_names）
    if feature_names is not None:
        try:
            self.best_model.get_booster().feature_names = feature_names  # 关键修改
            print(f'已设置 {len(feature_names)} 个特征名称')
        except Exception as e:
            print(f'设置特征名称时出现警告: {e}')
```

**改进点：**
- ✅ 新增 `feature_names` 参数
- ✅ 训练完成后直接设置 booster 的 `feature_names` 属性
- ✅ XGBoost sklearn API 不支持在 `fit()` 时传递 `feature_names`
- ✅ 使用 try-except 确保即使设置失败也不影响训练
- ✅ 保持向后兼容（参数可选）

### 3️⃣ 修复 `main.py` - 调用时传递特征名称

```python
# 修复前
trainer.train_final_model(X_train, y_train, sample_weights)

# 修复后
trainer.train_final_model(X_train, y_train, sample_weights, feat_cols)
```

**改进点：**
- ✅ 将特征名称列表 `feat_cols` 传递给训练器
- ✅ 确保模型训练时保存特征名称信息

## 修复效果

修复后，训练流程将：
1. ✅ 正确保存所有特征名称
2. ✅ 生成 `feature_importance.csv` 文件
3. ✅ 生成 `feature_importance.png` 可视化图表
4. ✅ 特征名称与训练数据列名完全对应

## 验证方法

### 运行训练
```bash
python main.py --config config_ahead.yaml
```

### 检查输出
训练完成后，在输出目录中应该看到：
```
output-ahead-YYYYMMDD_HHMMSS/
├── feature_importance.csv    ← 应该存在
├── feature_importance.png    ← 应该存在
├── best_params.json
├── ...
```

### 查看特征重要性
```python
import pandas as pd
fi = pd.read_csv('output-ahead-YYYYMMDD_HHMMSS/feature_importance.csv')
print(fi.head(20))
```

应该看到包含特征名称和重要性得分的表格。

## 技术细节

### XGBoost 特征名称处理

**重要**: XGBoost 的 sklearn API **不支持**在 `fit()` 时传递 `feature_names` 参数！

正确的方式是训练后直接设置：

```python
# 训练模型
model.fit(X, y, sample_weight=weights)

# 训练后设置特征名称
model.get_booster().feature_names = ['feat1', 'feat2', ...]
```

设置后：
- ✅ `model.get_booster().feature_names` 将包含特征名称
- ✅ 特征重要性字典的 key 将使用特征名称而非索引
- ✅ 模型保存时会包含特征名称信息

**替代方案**：使用 pandas DataFrame 作为输入，列名会自动作为特征名称（但我们使用 numpy array，所以需要手动设置）

### 特征重要性获取优先级

1. **优先**: 使用 `booster.feature_names`（如果存在且不为 None）
2. **备用**: 从 `imp_dict.keys()` 获取（从重要性字典的键）

## 相关文件

修改的文件：
- ✅ `evaluator.py` - 行 279-313
- ✅ `model_trainer.py` - 行 271-324
- ✅ `main.py` - 行 109-110

## 测试建议

### 快速测试
```bash
# 使用少量试验快速测试
python main.py --config config_regression.yaml
# （config_regression.yaml 中 n_random_trials=10）
```

### 完整测试
```bash
# 使用完整配置测试
python main.py --config config_ahead.yaml
# （config_ahead.yaml 中 n_random_trials=100）
```

## 注意事项

1. ✅ 确保 `feat_cols` 是有效的特征名称列表
2. ✅ 特征名称应为字符串类型
3. ✅ 特征名称数量应与训练数据的列数匹配
4. ✅ 滞后特征会自动命名为 `原特征名_lag_N`

## 总结

此次修复确保：
- ✅ 特征名称在整个训练流程中正确传递
- ✅ 特征重要性保存功能稳健可靠
- ✅ 即使特征名称获取失败，也有备用方案
- ✅ 所有边界情况都有妥善处理

**现在可以重新运行训练，特征重要性将正确保存！** 🎉

