"""
测试脚本：验证数据加载是否正常工作
"""
import sys
from config_manager import ConfigManager
from data_loader import DataLoader


def test_config(config_file):
    """测试配置文件和数据加载"""
    print('=' * 80)
    print(f'测试配置文件: {config_file}')
    print('=' * 80)
    
    try:
        # 加载配置
        config = ConfigManager(config_file)
        data_type = config.get('data.data_type')
        mode = config.get('model.mode')
        print(f'✓ 配置加载成功')
        print(f'  - 数据类型: {data_type}')
        print(f'  - 模式: {mode}')
        
        # 初始化数据加载器
        data_loader = DataLoader(config)
        print(f'✓ 数据加载器初始化成功')
        print(f'  - 特征数据目录: {data_loader.feat_data_dir}')
        print(f'  - 标签数据目录: {data_loader.label_data_dir}')
        print(f'  - 目标标签列: {data_loader.label_column}')
        
        # 加载训练数据
        print('\n加载训练数据...')
        train_df = data_loader.load_train_data()
        print(f'✓ 训练数据加载成功')
        print(f'  - 数据形状: {train_df.shape}')
        print(f'  - 列数: {len(train_df.columns)}')
        
        # 检查标签列是否存在
        if data_loader.label_column in train_df.columns:
            print(f'✓ 标签列 [{data_loader.label_column}] 存在于数据中')
            print(f'  - 标签统计: min={train_df[data_loader.label_column].min():.2f}, '
                  f'max={train_df[data_loader.label_column].max():.2f}, '
                  f'mean={train_df[data_loader.label_column].mean():.2f}')
        else:
            print(f'✗ 标签列 [{data_loader.label_column}] 不存在于数据中')
            print(f'  - 可用列: {train_df.columns.tolist()}')
            return False
        
        # 加载测试数据
        print('\n加载测试数据...')
        test_df = data_loader.load_test_data()
        print(f'✓ 测试数据加载成功')
        print(f'  - 数据形状: {test_df.shape}')
        print(f'  - 列数: {len(test_df.columns)}')
        
        # 检查标签列是否存在
        if data_loader.label_column in test_df.columns:
            print(f'✓ 标签列 [{data_loader.label_column}] 存在于测试数据中')
            print(f'  - 标签统计: min={test_df[data_loader.label_column].min():.2f}, '
                  f'max={test_df[data_loader.label_column].max():.2f}, '
                  f'mean={test_df[data_loader.label_column].mean():.2f}')
        else:
            print(f'✗ 标签列 [{data_loader.label_column}] 不存在于测试数据中')
            return False
        
        # 获取特征列
        feat_cols = data_loader.get_feature_columns(train_df)
        print(f'\n✓ 特征列提取成功')
        print(f'  - 特征数量: {len(feat_cols)}')
        
        print('\n' + '=' * 80)
        print(f'✓✓✓ 配置文件 {config_file} 测试通过！')
        print('=' * 80)
        print()
        return True
        
    except Exception as e:
        print('\n' + '=' * 80)
        print(f'✗✗✗ 配置文件 {config_file} 测试失败！')
        print(f'错误: {e}')
        print('=' * 80)
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # 测试所有配置文件
    config_files = [
        'config_realtime.yaml',
        'config_ahead.yaml',
        'config_price_diff.yaml',
        'config_price_diff_classification.yaml'
    ]
    
    results = {}
    for config_file in config_files:
        results[config_file] = test_config(config_file)
    
    # 输出汇总
    print('\n' + '=' * 80)
    print('测试汇总')
    print('=' * 80)
    for config_file, result in results.items():
        status = '✓ 通过' if result else '✗ 失败'
        print(f'{status}: {config_file}')
    
    # 检查是否全部通过
    all_passed = all(results.values())
    if all_passed:
        print('\n🎉 所有测试通过！')
        sys.exit(0)
    else:
        print('\n⚠️ 部分测试失败！')
        sys.exit(1)

