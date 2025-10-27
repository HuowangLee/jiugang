"""
数据加载模块
负责数据的读取、合并和预处理
"""
import pandas as pd
from typing import List, Tuple
from utils import safe_read_csv, quick_check_columns


class DataLoader:
    """数据加载器"""
    
    def __init__(self, config_manager):
        """
        初始化数据加载器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.data_config = config_manager.get_data_config()
    
    def load_train_data(self) -> pd.DataFrame:
        """
        加载训练数据
        
        Returns:
            训练DataFrame
        """
        print('加载训练数据...')
        return self._read_and_merge(
            self.data_config['feat_train'],
            self.data_config['label_train']
        )
    
    def load_test_data(self) -> pd.DataFrame:
        """
        加载测试数据
        
        Returns:
            测试DataFrame
        """
        print('加载测试数据...')
        return self._read_and_merge(
            self.data_config['feat_test'],
            self.data_config['label_test']
        )
    
    def _read_and_merge(self, feat_path: str, lab_path: str) -> pd.DataFrame:
        """
        读取并合并特征和标签数据
        
        Args:
            feat_path: 特征文件路径
            lab_path: 标签文件路径
        
        Returns:
            合并后的DataFrame
        """
        feat = safe_read_csv(feat_path)
        lab = safe_read_csv(lab_path)
        
        # 检查必要列
        quick_check_columns(feat, ['info_date', 'info_hour'], 'features')
        quick_check_columns(lab, ['info_date', 'info_hour'], 'label')
        
        # 合并
        df = feat.merge(lab, on=['info_date', 'info_hour'], how='inner')
        print(f"合并后 shape={df.shape}")
        print(df[['info_date', 'info_hour']].head(5))
        
        return df
    
    @staticmethod
    def make_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
        """
        创建时间索引
        
        Args:
            df: 输入DataFrame
        
        Returns:
            带时间戳的DataFrame
        """
        df = df.copy()
        if 'info_date' not in df.columns or 'info_hour' not in df.columns:
            raise KeyError('make_datetime_index 需要 info_date 与 info_hour 两列')
        
        # 解析日期
        df['info_date_dt'] = pd.to_datetime(df['info_date'], errors='coerce')
        
        # 将 "HH:MM" 转为 timedelta
        df['_time_delta'] = pd.to_timedelta(df['info_hour'] + ':00', errors='coerce')
        
        # 合成完整时间戳
        df['_timestamp'] = df['info_date_dt'] + df['_time_delta']
        
        # 按时间排序
        df = df.sort_values('_timestamp').reset_index(drop=True)
        
        return df
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        获取特征列（排除保留列）
        
        Args:
            df: DataFrame
        
        Returns:
            特征列名列表
        """
        reserved = set(self.config.get_feature_config().get('reserved_columns', []))
        feat_cols = [c for c in df.columns if c not in reserved]
        
        if len(feat_cols) == 0:
            raise ValueError('未找到任何特征列，请检查配置')
        
        print(f'发现 {len(feat_cols)} 个特征列')
        
        return feat_cols

