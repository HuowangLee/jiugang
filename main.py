"""
XGBoost训练主流程
重构版：模块化设计，配置文件驱动

使用方法:
    python main.py [--config CONFIG_PATH]

示例:
    python main.py
    python main.py --config my_config.yaml
"""
import os
import sys
import random
import argparse
import numpy as np

from config_manager import ConfigManager
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from model_trainer import ModelTrainer
from evaluator import ModelEvaluator


def set_random_seed(seed: int):
    """设置随机种子"""
    random.seed(seed)
    np.random.seed(seed)
    print(f'随机种子设置为: {seed}')


def main(config_path: str = 'config.yaml'):
    """
    主训练流程
    
    Args:
        config_path: 配置文件路径
    """
    print('=' * 80)
    print('XGBoost 训练流程')
    print('=' * 80)
    
    # 1. 加载配置
    print('\n[1/7] 加载配置...')
    config = ConfigManager(config_path)
    print(f'配置文件: {config_path}')
    print(f'模式: {config.get("model.mode")}')
    
    # 设置随机种子
    seed = config.get('model.random_seed', 42)
    set_random_seed(seed)
    
    # 2. 加载数据
    print('\n[2/7] 加载数据...')
    data_loader = DataLoader(config)
    train_df = data_loader.load_train_data()
    test_df = data_loader.load_test_data()
    
    # 获取特征列
    feat_cols = data_loader.get_feature_columns(train_df)
    
    # 3. 特征工程
    print('\n[3/7] 特征工程...')
    feature_engineer = FeatureEngineer(config)
    train_df, test_df, feat_cols = feature_engineer.process_train_test_features(
        train_df,
        test_df,
        feat_cols,
        DataLoader.make_datetime_index
    )
    
    # 准备训练数据
    print('\n准备训练和测试数据...')
    X_train = train_df[feat_cols].values
    y_train = train_df['price_diff'].values
    X_test = test_df[feat_cols].values
    y_test = test_df['price_diff'].values
    test_dates = test_df['info_date']
    
    print(f'训练样本数: {len(X_train)}')
    print(f'测试样本数: {len(X_test)}')
    print(f'特征数量: {len(feat_cols)}')
    
    # 4. 模型训练
    print('\n[4/7] 模型训练...')
    trainer = ModelTrainer(config)
    
    # 准备数据（分类任务会转换标签）
    X_train, y_train, feat_cols = trainer.prepare_data(X_train, y_train, feat_cols)
    
    # 超参数搜索
    trainer.hyperparameter_search(X_train, y_train, feat_cols)
    
    # 训练最终模型
    trainer.train_final_model(X_train, y_train)
    
    # 获取最佳模型和参数
    best_model = trainer.get_best_model()
    best_params_info = trainer.get_best_params()
    
    # 5. 模型评估
    print('\n[5/7] 模型评估...')
    evaluator = ModelEvaluator(config)
    
    # 预测
    res_df = evaluator.predict(best_model, X_test, y_test, test_dates)
    
    # 计算指标
    metrics = evaluator.calculate_metrics(res_df)
    
    # 6. 保存结果
    print('\n[6/7] 保存结果...')
    evaluator.create_output_directory()
    
    # 准备训练配置信息
    train_config = {
        'mode': config.get('model.mode'),
        'random_seed': seed,
        'lag_length': config.get('feature_engineering.lag_length'),
        'validation_ratio': config.get('model.validation_ratio'),
        'n_random_trials': config.get('model.n_random_trials'),
        **best_params_info
    }
    
    evaluator.save_results(
        best_model,
        res_df,
        metrics,
        best_params_info,
        train_config
    )
    
    # 7. 可视化
    print('\n[7/7] 可视化...')
    evaluator.visualize(res_df, metrics)
    
    print('\n' + '=' * 80)
    print('训练完成!')
    print(f'输出目录: {evaluator.output_dir}')
    print('=' * 80)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='XGBoost训练脚本')
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f'错误: 配置文件不存在: {args.config}')
        sys.exit(1)
    
    try:
        main(args.config)
    except KeyboardInterrupt:
        print('\n\n用户中断训练')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n训练过程中出现错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

