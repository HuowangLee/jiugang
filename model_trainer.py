"""
模型训练模块
负责模型训练和超参数搜索
"""
import sys
import numpy as np
import xgboost as xgb
from sklearn.model_selection import ParameterSampler
from tqdm import trange
from typing import Tuple, Optional

from utils import sign_label, calculate_sample_weights


class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, config_manager):
        """
        初始化模型训练器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.model_config = config_manager.get_model_config()
        self.weight_config = config_manager.get_sample_weight_config()
        
        self.mode = self.model_config.get('mode', 'regression')
        self.random_seed = self.model_config.get('random_seed', 42)
        self.n_trials = self.model_config.get('n_random_trials', 100)
        self.early_stopping = self.model_config.get('early_stopping_rounds', 30)
        self.num_boost_round = self.model_config.get('num_boost_round', 1000)
        self.validation_ratio = self.model_config.get('validation_ratio', 0.1)
        
        self.best_score = -np.inf
        self.best_params = None
        self.best_num_rounds = None
        self.best_model = None
    
    def prepare_data(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list
    ) -> Tuple:
        """
        准备训练数据（包括分类任务的标签转换）
        
        Args:
            X_train: 训练特征
            y_train: 训练标签
            feature_names: 特征名列表
        
        Returns:
            (X_train, y_train, feature_names)
        """
        if self.mode == 'classification':
            print('分类模式：将标签转换为符号标签')
            y_train = sign_label(y_train)
        
        return X_train, y_train, feature_names
    
    def split_train_validation(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple:
        """
        拆分训练集和验证集
        
        Args:
            X: 特征
            y: 标签
        
        Returns:
            (X_train, y_train, X_val, y_val)
        """
        n_all = len(X)
        split_idx = int(n_all * (1 - self.validation_ratio))
        
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        X_val = X[split_idx:]
        y_val = y[split_idx:]
        
        print(f'训练/验证拆分: {len(X_train)}/{len(X_val)}')
        
        return X_train, y_train, X_val, y_val
    
    def create_dmatrix(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: list,
        apply_weight: bool = True
    ) -> xgb.DMatrix:
        """
        创建XGBoost DMatrix
        
        Args:
            X: 特征
            y: 标签
            feature_names: 特征名
            apply_weight: 是否应用样本权重
        
        Returns:
            DMatrix对象
        """
        if apply_weight and self.weight_config.get('enabled', False):
            eps = self.weight_config.get('eps', 1e-6)
            alpha = self.weight_config.get('alpha', 2)
            weights = calculate_sample_weights(y, eps, alpha)
            return xgb.DMatrix(X, label=y, feature_names=feature_names, weight=weights)
        else:
            return xgb.DMatrix(X, label=y, feature_names=feature_names)
    
    def get_params_for_trial(self, trial_params: dict) -> dict:
        """
        为单次试验准备参数
        
        Args:
            trial_params: 试验参数
        
        Returns:
            完整的模型参数
        """
        params = trial_params.copy()
        
        # 移除n_estimators（后续单独处理）
        if "n_estimators" in params:
            params.pop("n_estimators")
        
        # 根据模式设置不同的参数
        if self.mode == 'regression':
            params.update({
                "objective": "reg:squarederror",
                "seed": self.random_seed,
            })
        else:  # classification
            params.update({
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "use_label_encoder": False,
                "seed": self.random_seed,
            })
        
        return params
    
    def evaluate_trial(
        self,
        model: xgb.Booster,
        dval: xgb.DMatrix,
        y_val: np.ndarray
    ) -> Tuple[float, float]:
        """
        评估单次试验结果
        
        Args:
            model: 训练好的模型
            dval: 验证集DMatrix
            y_val: 验证集标签
        
        Returns:
            (score, metric_value)
        """
        y_val_pred = model.predict(dval)
        
        if self.mode == 'regression':
            from sklearn.metrics import mean_squared_error
            mse = mean_squared_error(y_val, y_val_pred)
            rmse = np.sqrt(mse)
            score = -rmse  # 越小越好，所以取负
            metric_value = rmse
        else:  # classification
            # 计算符号一致性
            sign_true = np.sign(y_val)
            sign_pred = np.sign(y_val_pred)
            agreement = float(np.mean(sign_true == sign_pred))
            score = agreement  # 越大越好
            metric_value = agreement
        
        return score, metric_value
    
    def hyperparameter_search(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list
    ):
        """
        超参数搜索
        
        Args:
            X_train: 训练特征
            y_train: 训练标签
            feature_names: 特征名列表
        """
        print(f'\n开始超参数搜索 (mode={self.mode}, n_trials={self.n_trials})...')
        
        # 获取超参数搜索空间
        param_space = self.config.get_hyperparameters(self.mode)
        sampler = list(ParameterSampler(
            param_space,
            n_iter=self.n_trials,
            random_state=self.random_seed
        ))
        
        # 拆分训练/验证
        X_tr, y_tr, X_val, y_val = self.split_train_validation(X_train, y_train)
        
        try:
            for i in trange(len(sampler), desc='超参数试验'):
                trial_params = sampler[i].copy()
                params = self.get_params_for_trial(trial_params)
                
                # 创建DMatrix
                dtrain = self.create_dmatrix(X_tr, y_tr, feature_names)
                dval = self.create_dmatrix(X_val, y_val, feature_names)
                
                # 训练模型
                model = xgb.train(
                    params,
                    dtrain,
                    num_boost_round=self.num_boost_round,
                    evals=[(dtrain, "train"), (dval, "val")],
                    early_stopping_rounds=self.early_stopping,
                    verbose_eval=False
                )
                
                # 评估
                best_rounds = model.best_iteration + 1
                score, metric_value = self.evaluate_trial(model, dval, y_val)
                
                metric_name = 'RMSE' if self.mode == 'regression' else 'Agreement'
                print(
                    f"Trial {i} params={trial_params} -> "
                    f"{metric_name}={metric_value:.5f}, score={score:.5f}, "
                    f"rounds={best_rounds}"
                )
                
                # 更新最佳结果
                if score > self.best_score:
                    self.best_score = score
                    self.best_params = trial_params
                    self.best_num_rounds = best_rounds
                    self.best_model = model
                    print(f"  ✓ 发现更好的模型! score={score:.5f}")
        
        except KeyboardInterrupt:
            print('\n检测到 KeyboardInterrupt，优雅退出超参数搜索...')
            if self.best_model is None:
                print('没有已训练完成的模型')
                sys.exit(1)
        
        print(f'\n超参数搜索完成! 最佳score={self.best_score:.5f}')
        print(f'最佳参数: {self.best_params}')
        print(f'最佳轮数: {self.best_num_rounds}')
    
    def train_final_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ):
        """
        使用最佳参数在全部训练集上训练最终模型
        
        Args:
            X_train: 训练特征
            y_train: 训练标签
        """
        print('\n使用最佳参数训练最终模型...')
        
        if self.best_params is None:
            raise ValueError('请先运行超参数搜索')
        
        if self.mode == 'regression':
            self.best_model = xgb.XGBRegressor(
                verbosity=0,
                random_state=self.random_seed,
                **self.best_params,
                n_estimators=self.best_num_rounds
            )
        else:  # classification
            self.best_model = xgb.XGBClassifier(
                use_label_encoder=False,
                eval_metric='logloss',
                verbosity=0,
                random_state=self.random_seed,
                **self.best_params,
                n_estimators=self.best_num_rounds
            )
        
        self.best_model.fit(X_train, y_train)
        print('最终模型训练完成!')
    
    def get_best_model(self):
        """获取最佳模型"""
        return self.best_model
    
    def get_best_params(self) -> dict:
        """获取最佳参数"""
        return {
            'params': self.best_params,
            'num_rounds': self.best_num_rounds,
            'score': self.best_score
        }

