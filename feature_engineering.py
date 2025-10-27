"""
特征工程模块
负责特征的构建和转换
"""
import pandas as pd
from typing import List, Optional


class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self, config_manager):
        """
        初始化特征工程器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.feature_config = config_manager.get_feature_config()
        self.lag_length = self.feature_config.get('lag_length', 0)
        self.group_key = self.feature_config.get('group_key', None)
    
    def build_lag_features(
        self, 
        df: pd.DataFrame, 
        feature_cols: List[str]
    ) -> pd.DataFrame:
        """
        构建滞后特征
        
        Args:
            df: 输入DataFrame
            feature_cols: 需要构建滞后特征的列名列表
        
        Returns:
            包含滞后特征的DataFrame
        """
        if self.lag_length == 0:
            print('滞后长度为0，跳过滞后特征构建')
            return df
        
        df = df.copy()
        
        print(f'构建滞后特征，lag_length={self.lag_length}')
        
        if self.group_key and self.group_key in df.columns:
            # 按组生成滞后特征
            print(f'按 {self.group_key} 分组生成滞后特征')
            for f in feature_cols:
                for l in range(1, self.lag_length + 1):
                    df[f'{f}_lag{l}'] = df.groupby(self.group_key)[f].shift(l)
        else:
            # 全局生成滞后特征
            print('全局生成滞后特征')
            for f in feature_cols:
                for l in range(1, self.lag_length + 1):
                    df[f'{f}_lag{l}'] = df[f].shift(l)
        
        return df
    
    def remove_lag_na(
        self, 
        df: pd.DataFrame, 
        dataset_name: str = ''
    ) -> pd.DataFrame:
        """
        移除因滞后特征产生的NA行
        
        Args:
            df: 输入DataFrame
            dataset_name: 数据集名称（用于日志）
        
        Returns:
            移除NA后的DataFrame
        """
        if self.lag_length == 0:
            return df
        
        before_len = len(df)
        df = df.iloc[self.lag_length:]
        after_len = len(df)
        
        print(f'{dataset_name} 移除滞后NA: {before_len} -> {after_len} (移除 {before_len - after_len} 行)')
        
        return df
    
    def process_train_test_features(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_cols: List[str],
        datetime_func
    ) -> tuple:
        """
        处理训练集和测试集的特征
        （包括时间索引、滞后特征等）
        
        Args:
            train_df: 训练数据
            test_df: 测试数据
            feature_cols: 特征列
            datetime_func: 创建时间索引的函数
        
        Returns:
            (处理后的训练集, 处理后的测试集, 更新后的特征列)
        """
        print('准备特征工程...')
        
        # 标记数据集
        train_df['_split'] = 'train'
        test_df['_split'] = 'test'
        
        # 拼接
        concat_df = pd.concat([train_df, test_df], ignore_index=True)
        
        # 构造时间索引
        concat_df = datetime_func(concat_df)
        
        # 生成滞后特征
        concat_lagged = self.build_lag_features(concat_df, feature_cols)
        
        # 切分回训练集和测试集
        concat_lagged['_split'] = concat_lagged['_split'].astype(str)
        train_lagged = concat_lagged[concat_lagged['_split'] == 'train'].drop(columns=['_split'])
        test_lagged = concat_lagged[concat_lagged['_split'] == 'test'].drop(columns=['_split'])
        
        # Reset index
        train_lagged = train_lagged.reset_index(drop=True)
        test_lagged = test_lagged.reset_index(drop=True)
        
        # 移除滞后造成的NA
        train_lagged = self.remove_lag_na(train_lagged, '训练集')
        
        # 更新特征列（包含新生成的滞后特征）
        reserved = set(self.feature_config.get('reserved_columns', []))
        updated_feat_cols = [c for c in train_lagged.columns if c not in reserved]
        
        return train_lagged, test_lagged, updated_feat_cols

