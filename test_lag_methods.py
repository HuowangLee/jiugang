"""
测试滞后特征构造方法
验证 direct 和 statistical 两种方法的正确性
"""

import pandas as pd
import numpy as np
from src.config_manager import ConfigManager
from src.feature_engineering import FeatureEngineer


def test_lag_methods():
    """测试两种滞后特征方法"""
    
    # 创建测试数据
    np.random.seed(42)
    n_samples = 10
    test_data = pd.DataFrame({
        'feature1': np.arange(n_samples, dtype=float),
        'feature2': np.random.randn(n_samples) * 10,
        'info_date': pd.date_range('2024-01-01', periods=n_samples),
        'info_hour': [i % 24 for i in range(n_samples)]
    })
    
    print("=" * 80)
    print("原始数据:")
    print("=" * 80)
    print(test_data)
    print()
    
    # 测试1: Direct方法
    print("=" * 80)
    print("测试1: Direct方法 (lag_length=3)")
    print("=" * 80)
    
    # 创建配置（模拟）
    config_dict = {
        'feature_engineering': {
            'lag_length': 3,
            'group_key': None,
            'lag_method': 'direct',
            'reserved_columns': ['info_date', 'info_hour']
        },
        'sample_weight': {
            'enabled': False
        }
    }
    
    class MockConfigManager:
        def __init__(self, config):
            self.config = config
        
        def get_feature_config(self):
            return self.config['feature_engineering']
        
        def get_sample_weight_config(self):
            return self.config['sample_weight']
    
    config_manager = MockConfigManager(config_dict)
    engineer = FeatureEngineer(config_manager)
    
    # 应用direct方法
    df_direct = engineer.build_lag_features(test_data.copy(), ['feature1', 'feature2'])
    
    print("\nDirect方法生成的特征列:")
    lag_cols = [col for col in df_direct.columns if 'lag' in col]
    print(lag_cols)
    
    print("\nDirect方法结果 (前5行):")
    print(df_direct[['feature1', 'feature1_lag1', 'feature1_lag2', 'feature1_lag3']].head())
    print()
    
    # 验证direct方法的正确性
    print("验证 Direct 方法:")
    print(f"  feature1[3] = {test_data['feature1'].iloc[3]}")
    print(f"  feature1_lag1[3] = {df_direct['feature1_lag1'].iloc[3]} (应该等于 feature1[2] = {test_data['feature1'].iloc[2]})")
    print(f"  feature1_lag2[3] = {df_direct['feature1_lag2'].iloc[3]} (应该等于 feature1[1] = {test_data['feature1'].iloc[1]})")
    print(f"  feature1_lag3[3] = {df_direct['feature1_lag3'].iloc[3]} (应该等于 feature1[0] = {test_data['feature1'].iloc[0]})")
    
    assert df_direct['feature1_lag1'].iloc[3] == test_data['feature1'].iloc[2], "lag1验证失败"
    assert df_direct['feature1_lag2'].iloc[3] == test_data['feature1'].iloc[1], "lag2验证失败"
    assert df_direct['feature1_lag3'].iloc[3] == test_data['feature1'].iloc[0], "lag3验证失败"
    print("✓ Direct方法验证通过!\n")
    
    # 测试2: Statistical方法
    print("=" * 80)
    print("测试2: Statistical方法 (lag_length=3)")
    print("=" * 80)
    
    config_dict['feature_engineering']['lag_method'] = 'statistical'
    config_manager = MockConfigManager(config_dict)
    engineer = FeatureEngineer(config_manager)
    
    # 应用statistical方法
    df_stat = engineer.build_lag_features(test_data.copy(), ['feature1', 'feature2'])
    
    print("\nStatistical方法生成的特征列:")
    stat_cols = [col for col in df_stat.columns if any(x in col for x in ['lag', 'diff', 'rolling'])]
    print(stat_cols)
    
    print("\nStatistical方法结果 (前7行):")
    display_cols = ['feature1', 'feature1_lag1', 'feature1_diff1', 
                    'feature1_rolling_mean', 'feature1_rolling_std', 'feature1_diff3']
    print(df_stat[display_cols].head(7))
    print()
    
    # 验证statistical方法的正确性
    print("验证 Statistical 方法:")
    
    # 验证lag1
    idx = 4
    print(f"\n对于索引 {idx}:")
    print(f"  feature1[{idx}] = {test_data['feature1'].iloc[idx]}")
    print(f"  feature1_lag1[{idx}] = {df_stat['feature1_lag1'].iloc[idx]} (应该等于 feature1[{idx-1}] = {test_data['feature1'].iloc[idx-1]})")
    assert df_stat['feature1_lag1'].iloc[idx] == test_data['feature1'].iloc[idx-1], "lag1验证失败"
    print("  ✓ lag1 正确")
    
    # 验证diff1
    expected_diff1 = test_data['feature1'].iloc[idx] - test_data['feature1'].iloc[idx-1]
    print(f"  feature1_diff1[{idx}] = {df_stat['feature1_diff1'].iloc[idx]} (应该等于 {expected_diff1})")
    assert abs(df_stat['feature1_diff1'].iloc[idx] - expected_diff1) < 1e-10, "diff1验证失败"
    print("  ✓ diff1 正确")
    
    # 验证rolling_mean (窗口大小为3，从lag1往前看3个值)
    # 对于索引4，rolling_mean应该是feature1[1], feature1[2], feature1[3]的平均
    expected_mean = test_data['feature1'].iloc[1:4].mean()
    print(f"  feature1_rolling_mean[{idx}] = {df_stat['feature1_rolling_mean'].iloc[idx]} (应该约等于 {expected_mean})")
    assert abs(df_stat['feature1_rolling_mean'].iloc[idx] - expected_mean) < 1e-10, "rolling_mean验证失败"
    print("  ✓ rolling_mean 正确")
    
    # 验证rolling_std
    expected_std = test_data['feature1'].iloc[1:4].std()
    print(f"  feature1_rolling_std[{idx}] = {df_stat['feature1_rolling_std'].iloc[idx]} (应该约等于 {expected_std})")
    assert abs(df_stat['feature1_rolling_std'].iloc[idx] - expected_std) < 1e-10, "rolling_std验证失败"
    print("  ✓ rolling_std 正确")
    
    # 验证diff3
    expected_diff3 = test_data['feature1'].iloc[idx] - test_data['feature1'].iloc[idx-3]
    print(f"  feature1_diff3[{idx}] = {df_stat['feature1_diff3'].iloc[idx]} (应该等于 {expected_diff3})")
    assert abs(df_stat['feature1_diff3'].iloc[idx] - expected_diff3) < 1e-10, "diff3验证失败"
    print("  ✓ diff3 正确")
    
    print("\n✓ Statistical方法验证通过!\n")
    
    # 特征数量对比
    print("=" * 80)
    print("特征数量对比")
    print("=" * 80)
    
    direct_lag_features = [col for col in df_direct.columns if 'lag' in col]
    stat_features = [col for col in df_stat.columns if any(x in col for x in ['lag', 'diff', 'rolling'])]
    
    print(f"原始特征数: 2 (feature1, feature2)")
    print(f"Direct方法生成特征数: {len(direct_lag_features)} ({len(direct_lag_features)//2} per feature)")
    print(f"  特征列表: {direct_lag_features}")
    print(f"\nStatistical方法生成特征数: {len(stat_features)} ({len(stat_features)//2} per feature)")
    print(f"  特征列表: {stat_features}")
    
    print("\n" + "=" * 80)
    print("所有测试通过! ✓")
    print("=" * 80)


if __name__ == '__main__':
    test_lag_methods()

