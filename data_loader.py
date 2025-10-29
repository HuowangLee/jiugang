"""
数据加载模块
负责数据的读取、合并和预处理
"""
import os
import glob
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
        self.data_type = self.data_config.get('data_type', 'realtime')
        self.base_dir = self.data_config.get('base_dir', 'data1year/data')
        
        # 特征数据统一从ahead文件夹读取
        self.feat_data_dir = self._find_data_directory('ahead')
        # 标签数据统一从price_diff文件夹读取
        self.label_data_dir = self._find_data_directory('price_diff')
        
        # 根据data_type确定标签列名
        self.label_column = self._get_label_column()
    
    def _get_label_column(self) -> str:
        """
        根据data_type确定标签列名
        
        Returns:
            标签列名
        """
        label_mapping = {
            'realtime': 'price_real_clear',
            'ahead': 'price_ahead_clear',
            'price_diff': 'price_diff'
        }
        
        if self.data_type not in label_mapping:
            raise ValueError(
                f'不支持的data_type: {self.data_type}\n'
                f'支持的类型: {list(label_mapping.keys())}'
            )
        
        label_col = label_mapping[self.data_type]
        print(f'数据类型: {self.data_type}')
        print(f'目标标签列: {label_col}')
        
        return label_col
    
    def _find_data_directory(self, folder_type: str) -> str:
        """
        根据folder_type自动查找数据目录
        
        Args:
            folder_type: 文件夹类型 (ahead, price_diff, realtime)
        
        Returns:
            数据目录路径
        
        Raises:
            FileNotFoundError: 如果找不到匹配的数据目录
        """
        # 如果base_dir不存在，尝试使用旧的配置方式
        if not os.path.exists(self.base_dir):
            print(f'警告: 基础目录不存在 {self.base_dir}，尝试使用传统路径配置')
            return None
        
        # 查找匹配folder_type的目录
        pattern = os.path.join(self.base_dir, f'{folder_type}-*')
        matching_dirs = glob.glob(pattern)
        
        if not matching_dirs:
            raise FileNotFoundError(
                f'未找到匹配的数据目录: {pattern}\n'
                f'请确保 {self.base_dir} 下存在 {folder_type}-* 格式的子目录'
            )
        
        # 如果有多个匹配，选择最新的（按名称排序，通常包含日期）
        data_dir = sorted(matching_dirs)[-1]
        print(f'[{folder_type}] 数据目录: {data_dir}')
        
        return data_dir
    
    def _build_file_path(self, file_key: str) -> str:
        """
        构建完整的文件路径
        
        Args:
            file_key: 文件配置键名（如 'feat_train', 'label_train'）
        
        Returns:
            完整的文件路径
        """
        filename = self.data_config.get(file_key)
        
        # 区分特征文件和标签文件
        if 'feat' in file_key:
            # 特征文件从ahead文件夹读取
            if self.feat_data_dir:
                return os.path.join(self.feat_data_dir, filename)
        elif 'label' in file_key:
            # 标签文件从price_diff文件夹读取
            if self.label_data_dir:
                return os.path.join(self.label_data_dir, filename)
        
        # 向后兼容旧的配置方式
        if file_key in self.data_config:
            return self.data_config[file_key]
        
        raise ValueError(f'未找到文件配置: {file_key}')
    
    def load_train_data(self) -> pd.DataFrame:
        """
        加载训练数据
        
        Returns:
            训练DataFrame
        """
        print('加载训练数据...')
        feat_path = self._build_file_path('feat_train')
        label_path = self._build_file_path('label_train')
        return self._read_and_merge(feat_path, label_path)
    
    def load_test_data(self) -> pd.DataFrame:
        """
        加载测试数据
        
        Returns:
            测试DataFrame
        """
        print('加载测试数据...')
        feat_path = self._build_file_path('feat_test')
        label_path = self._build_file_path('label_test')
        return self._read_and_merge(feat_path, label_path)
    
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
        
        # 检查标签列是否存在
        if self.label_column not in lab.columns:
            raise KeyError(
                f'标签文件中未找到目标标签列: {self.label_column}\n'
                f'可用列: {lab.columns.tolist()}'
            )
        
        # 只保留需要的标签列和对齐列
        label_columns_to_keep = ['info_date', 'info_hour', self.label_column]
        lab = lab[label_columns_to_keep]
        
        print(f"特征数据 shape={feat.shape}")
        print(f"标签数据 shape={lab.shape}, 标签列={self.label_column}")
        
        # 按 info_date 和 info_hour 对齐合并
        df = feat.merge(lab, on=['info_date', 'info_hour'], how='inner')
        print(f"合并后 shape={df.shape}")
        print(f"合并示例:")
        print(df[['info_date', 'info_hour', self.label_column]].head(5))
        
        return df
    
    @staticmethod
    def make_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
        """
        创建时间索引并排序
        
        Args:
            df: 输入DataFrame
        
        Returns:
            按时间排序后的DataFrame（临时时间列已移除）
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
        
        # 移除临时列
        df = df.drop(columns=['info_date_dt', '_time_delta', '_timestamp'])
        
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

