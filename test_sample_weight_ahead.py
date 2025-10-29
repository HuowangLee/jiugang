"""
测试ahead配置下的样本权重功能
"""
import sys
sys.path.insert(0, '.')

from src.config_manager import ConfigManager
from src.data_loader import DataLoader
from src.feature_engineering import FeatureEngineer

def test_ahead_sample_weight():
    """测试ahead配置能否正确加载price_diff并计算样本权重"""
    
    print('=' * 80)
    print('测试ahead配置的样本权重功能')
    print('=' * 80)
    
    # 1. 加载配置
    print('\n[1] 加载配置...')
    config = ConfigManager('config/config_ahead.yaml')
    print(f'  data_type: {config.get("data.data_type")}')
    print(f'  sample_weight.enabled: {config.get("sample_weight.enabled")}')
    
    # 2. 加载数据
    print('\n[2] 加载训练数据...')
    data_loader = DataLoader(config)
    train_df = data_loader.load_train_data()
    
    # 3. 检查price_diff列是否存在
    print(f'\n[3] 检查数据列...')
    print(f'  数据shape: {train_df.shape}')
    print(f'  列名: {train_df.columns.tolist()}')
    
    if 'price_diff' in train_df.columns:
        print('  ✅ price_diff列已保留')
        print(f'  price_diff统计: min={train_df["price_diff"].min():.4f}, '
              f'max={train_df["price_diff"].max():.4f}, '
              f'mean={train_df["price_diff"].mean():.4f}')
    else:
        print('  ❌ price_diff列缺失')
        return False
    
    # 4. 计算样本权重
    print('\n[4] 计算样本权重...')
    feature_engineer = FeatureEngineer(config)
    sample_weights = feature_engineer.compute_sample_weights(train_df)
    
    if sample_weights is not None:
        print(f'  ✅ 样本权重计算成功')
        print(f'  权重shape: {sample_weights.shape}')
        print(f'  权重与样本数匹配: {len(sample_weights) == len(train_df)}')
        return True
    else:
        print('  ❌ 样本权重计算失败')
        return False

if __name__ == '__main__':
    success = test_ahead_sample_weight()
    print('\n' + '=' * 80)
    if success:
        print('✅ 测试通过！ahead配置可以正确使用样本权重功能')
    else:
        print('❌ 测试失败！请检查配置或数据')
    print('=' * 80)

