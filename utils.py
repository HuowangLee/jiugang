"""
工具函数模块
包含各种辅助函数
"""
import os
import numpy as np
import pandas as pd
from typing import List


def safe_read_csv(path: str) -> pd.DataFrame:
    """
    安全读取CSV文件
    
    Args:
        path: CSV文件路径
    
    Returns:
        DataFrame
    
    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    
    df = pd.read_csv(path, index_col=0)
    print(f"读取 {path} -> shape={df.shape}")
    print("前 10 列名:", df.columns[:10].tolist())
    return df


def quick_check_columns(df: pd.DataFrame, required: List[str], df_name: str):
    """
    快速检查DataFrame是否包含必要的列
    
    Args:
        df: DataFrame
        required: 必要的列名列表
        df_name: DataFrame名称（用于错误提示）
    
    Raises:
        KeyError: 缺少必要列时抛出
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"错误: 在 {df_name} 中缺少必要列: {missing}")
        print(f"{df_name} 的列名: {df.columns.tolist()}")
        raise KeyError(f"{df_name} 缺少列: {missing}")


def sign_label(arr: np.ndarray) -> np.ndarray:
    """
    将连续值转换为符号标签（正为1，负为-1）
    
    Args:
        arr: 输入数组
    
    Returns:
        符号数组
    """
    return np.where(arr > 0, 1, -1)


def sign_agreement(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    计算符号一致性（预测值和真实值符号相同的比例）
    
    Args:
        y_true: 真实值
        y_pred: 预测值
    
    Returns:
        一致性比例（0-1之间）
    """
    y_true_sign = (np.array(y_true) > 0)
    y_pred_sign = (np.array(y_pred) > 0)
    return float(np.mean(y_true_sign == y_pred_sign))


def per_date_sign_agreement(df: pd.DataFrame, date_col: str = 'info_date') -> pd.DataFrame:
    """
    计算每个日期的符号一致性
    
    Args:
        df: 包含 'label', 'pred' 和日期列的DataFrame
        date_col: 日期列名
    
    Returns:
        包含每个日期的一致性统计的DataFrame
    """
    rows = []
    for date, g in df.groupby(date_col):
        agree = sign_agreement(g['label'].values, g['pred'].values)
        rows.append({'info_date': date, 'n_points': len(g), 'agreement': agree})
    return pd.DataFrame(rows).sort_values('info_date')


def calculate_sample_weights(y: np.ndarray, eps: float = 1e-6, alpha: float = 2) -> np.ndarray:
    """
    计算样本权重（非线性加权）
    
    Args:
        y: 标签数组
        eps: 避免零的小常数
        alpha: 权重指数
    
    Returns:
        样本权重数组
    """
    return np.power(np.abs(y) + eps, alpha)

