"""
配置管理模块
负责加载和管理训练配置
"""
import os
import yaml
from typing import Any, Dict


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的路径，如 'model.random_seed'
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_data_config(self) -> Dict[str, str]:
        """获取数据配置"""
        return self.config.get('data', {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return self.config.get('model', {})
    
    def get_feature_config(self) -> Dict[str, Any]:
        """获取特征工程配置"""
        return self.config.get('feature_engineering', {})
    
    def get_hyperparameters(self, mode: str) -> Dict[str, list]:
        """
        获取超参数搜索空间
        
        Args:
            mode: 'regression' 或 'classification'
        
        Returns:
            超参数字典
        """
        return self.config.get('hyperparameters', {}).get(mode, {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.config.get('output', {})
    
    def get_sample_weight_config(self) -> Dict[str, Any]:
        """获取样本权重配置"""
        return self.config.get('sample_weight', {})
    
    def __repr__(self) -> str:
        return f"ConfigManager(config_path='{self.config_path}')"

