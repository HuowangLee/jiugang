"""
特征工程模块
负责特征的构建和转换
"""
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from src.utils import calculate_sample_weights


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
        self.weight_config = config_manager.get_sample_weight_config()
        self.lag_length = self.feature_config.get('lag_length', 0)
        self.group_key = self.feature_config.get('group_key', None)
        self.lag_method = self.feature_config.get('lag_method', 'direct')
    
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
        
        print(f'构建滞后特征，lag_length={self.lag_length}, method={self.lag_method}')
        
        if self.lag_method == 'direct':
            # 方法1: 直接拼接滞后特征
            return self._build_direct_lag_features(df, feature_cols)
        elif self.lag_method == 'statistical':
            # 方法2: 构造统计量
            return self._build_statistical_lag_features(df, feature_cols)
        else:
            raise ValueError(f"不支持的lag_method: {self.lag_method}，请选择 'direct' 或 'statistical'")
    
    def _build_direct_lag_features(
        self, 
        df: pd.DataFrame, 
        feature_cols: List[str]
    ) -> pd.DataFrame:
        """
        方法1: 直接拼接滞后特征
        生成 lag_1, lag_2, ..., lag_N
        
        Args:
            df: 输入DataFrame
            feature_cols: 需要构建滞后特征的列名列表
        
        Returns:
            包含滞后特征的DataFrame
        """
        if self.group_key and self.group_key in df.columns:
            # 按组生成滞后特征
            print(f'  按 {self.group_key} 分组生成滞后特征')
            for f in feature_cols:
                for l in range(1, self.lag_length + 1):
                    df[f'{f}_lag{l}'] = df.groupby(self.group_key)[f].shift(l)
        else:
            # 全局生成滞后特征
            print('  全局生成滞后特征')
            for f in feature_cols:
                for l in range(1, self.lag_length + 1):
                    df[f'{f}_lag{l}'] = df[f].shift(l)
        
        return df
    
    def _build_statistical_lag_features(
        self, 
        df: pd.DataFrame, 
        feature_cols: List[str]
    ) -> pd.DataFrame:
        """
        方法2: 构造统计量
        对于每个特征，生成以下统计量：
        - lag_1: 上一时刻的值
        - diff_1: 与上一时刻的差值
        - rolling_mean: 滚动窗口的平均值
        - rolling_std: 滚动窗口的标准差
        - diff_N: 与N个时刻前的差值（N=lag_length）
        
        Args:
            df: 输入DataFrame
            feature_cols: 需要构建滞后特征的列名列表
        
        Returns:
            包含统计量特征的DataFrame
        """
        print(f'  构造统计量特征 (窗口长度={self.lag_length})')
        
        if self.group_key and self.group_key in df.columns:
            # 按组生成统计量特征
            print(f'  按 {self.group_key} 分组生成统计量特征')
            for f in feature_cols:
                grouped = df.groupby(self.group_key)[f]
                
                # lag_1: 上一时刻的值
                df[f'{f}_lag1'] = grouped.shift(1)
                
                # diff_1: 与上一时刻的差值
                df[f'{f}_diff1'] = df[f] - df[f'{f}_lag1']
                
                # rolling_mean: 滚动平均（窗口大小为lag_length）
                df[f'{f}_rolling_mean'] = grouped.shift(1).rolling(
                    window=self.lag_length, 
                    min_periods=1
                ).mean()
                
                # rolling_std: 滚动标准差（窗口大小为lag_length）
                df[f'{f}_rolling_std'] = grouped.shift(1).rolling(
                    window=self.lag_length, 
                    min_periods=1
                ).std()
                
                # diff_N: 与N个时刻前的差值
                if self.lag_length > 1:
                    df[f'{f}_lag{self.lag_length}'] = grouped.shift(self.lag_length)
                    df[f'{f}_diff{self.lag_length}'] = df[f] - df[f'{f}_lag{self.lag_length}']
        else:
            # 全局生成统计量特征
            print('  全局生成统计量特征')
            for f in feature_cols:
                # lag_1: 上一时刻的值
                df[f'{f}_lag1'] = df[f].shift(1)
                
                # diff_1: 与上一时刻的差值
                df[f'{f}_diff1'] = df[f] - df[f'{f}_lag1']
                
                # rolling_mean: 滚动平均（窗口大小为lag_length）
                df[f'{f}_rolling_mean'] = df[f].shift(1).rolling(
                    window=self.lag_length, 
                    min_periods=1
                ).mean()
                
                # rolling_std: 滚动标准差（窗口大小为lag_length）
                df[f'{f}_rolling_std'] = df[f].shift(1).rolling(
                    window=self.lag_length, 
                    min_periods=1
                ).std()
                
                # diff_N: 与N个时刻前的差值
                if self.lag_length > 1:
                    df[f'{f}_lag{self.lag_length}'] = df[f].shift(self.lag_length)
                    df[f'{f}_diff{self.lag_length}'] = df[f] - df[f'{f}_lag{self.lag_length}']
        
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

        # 只保留指定的几列
        # keep_cols = ['jingjiakongjian', 'sdsurplus',
        # # 'load_ahead_publish_新疆', 'load_ahead_publish_宁夏', 'load_ahead_publish_青海', 'load_ahead_publish_陕西',
        #  'price_ahead_clear', 'price_real_clear','price_diff', 'info_date', 'info_hour']
        # # 只保留存在于concat_df中的那些
        # keep_cols = [c for c in keep_cols if c in train_df.columns and c in test_df.columns]
        # train_df = train_df[keep_cols].copy()
        # test_df = test_df[keep_cols].copy()
        # feature_cols = [c for c in keep_cols if c not in ['info_date', 'info_hour','price_diff','price_ahead_clear', 'price_real_clear']]
        
        # 标记数据集
        train_df['_split'] = 'train'
        test_df['_split'] = 'test'
        
        # 拼接
        concat_df = pd.concat([train_df, test_df], ignore_index=True)
        
        # 构造时间索引
        concat_df = datetime_func(concat_df)
        
        # 移除所有后缀含有新疆、宁夏、青海、陕西但不是load_ahead_publish_XXX的列，并输出移除的列名
        # 并将保留的列的后缀从中文换成拼音
        import re

        regions = ['新疆', '宁夏', '青海', '陕西']
        region_pinyin = {'新疆': 'xinjiang', '宁夏': 'ningxia', '青海': 'qinghai', '陕西': 'shanxi'}

        def should_remove(col_name):
            # 匹配后缀为区域名
            for region in regions:
                pattern = rf'{region}$'
                if re.search(pattern, col_name):
                    # 允许load_ahead_publish_XXX格式
                    if col_name == f'load_ahead_publish_{region}':
                        return False
                    else:
                        return True
            return False

        # 找到需要移除的列
        remove_cols = [c for c in concat_df.columns if should_remove(c)]
        if remove_cols:
            print(f'移除以下含有区域后缀的列（除load_ahead_publish_XXX）：{remove_cols}')
            concat_df = concat_df.drop(columns=remove_cols, errors='ignore')

        # 列重命名：将保留的列的后缀从中文换成拼音
        rename_cols = {}
        for col in concat_df.columns:
            for region in regions:
                if col.endswith(region) and col != f'load_ahead_publish_{region}':
                    continue  # 已在上面被删除
                # 对于load_ahead_publish_XXX或者其它保留的区域后缀，重命名
                pattern = rf'(.*)({region})$'
                if re.match(pattern, col):
                    new_col = re.sub(region + r'$', region_pinyin[region], col)
                    if new_col != col:
                        rename_cols[col] = new_col
        if rename_cols:
            print(f'将以下列后缀从中文替换为拼音: {rename_cols}')
            concat_df = concat_df.rename(columns=rename_cols)
        # 此时feature_cols中也需做同步更名
        feature_cols = [rename_cols.get(fc, fc) for fc in feature_cols]

            
        
        # 更新特征列，移除已删除的列
        feature_cols = [c for c in feature_cols if c in concat_df.columns]
        
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
        test_lagged = self.remove_lag_na(test_lagged, '测试集')
        
        # 更新特征列（包含新生成的滞后特征）
        reserved = set(self.feature_config.get('reserved_columns', []))

        # 移除全部为nan的列，并输出移除的列名
        all_nan_cols = [col for col in train_lagged.columns if train_lagged[col].isna().all() and test_lagged[col].isna().all()]
        if all_nan_cols:
            print(f'移除全部为nan的列: {all_nan_cols}')
            train_lagged = train_lagged.drop(columns=all_nan_cols)
            test_lagged = test_lagged.drop(columns=all_nan_cols)

        
        
        updated_feat_cols = [c for c in train_lagged.columns if c not in reserved]
        
        print(f'保留的特征列: {updated_feat_cols}')

        return train_lagged, test_lagged, updated_feat_cols
    
    def compute_sample_weights(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        根据price_diff计算样本权重
        
        Args:
            df: 包含price_diff列的DataFrame
        
        Returns:
            样本权重数组，如果未启用则返回None
        """
        if not self.weight_config.get('enabled', False):
            return None
        
        if 'price_diff' not in df.columns:
            print('警告: 未找到price_diff列，无法计算样本权重')
            return None
        
        weight_type = self.weight_config.get('weight_type', 'nonlinear')
        eps = self.weight_config.get('eps', 1e-6)
        alpha = self.weight_config.get('alpha', 2)
        
        price_diff = df['price_diff'].values
        weights = calculate_sample_weights(price_diff, weight_type, eps, alpha)
        
        print(f'\n样本权重计算:')
        print(f'  权重类型: {weight_type}')
        print(f'  eps: {eps}')
        if weight_type == 'nonlinear':
            print(f'  alpha: {alpha}')
        print(f'  权重统计: min={weights.min():.4f}, max={weights.max():.4f}, mean={weights.mean():.4f}')
        
        return weights

