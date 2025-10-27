"""
评估和可视化模块
负责模型评估、结果保存和可视化
"""
import os
import json
import csv
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from utils import per_date_sign_agreement, sign_label


class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self, config_manager):
        """
        初始化模型评估器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.model_config = config_manager.get_model_config()
        self.output_config = config_manager.get_output_config()
        self.viz_config = self.output_config.get('visualization', {})
        
        self.mode = self.model_config.get('mode', 'regression')
        self.output_dir = None
    
    def create_output_directory(self) -> str:
        """
        创建输出目录
        
        Returns:
            输出目录路径
        """
        date = datetime.now() - timedelta(days=2)
        dir_prefix = self.output_config.get('dir_prefix', 'output')
        self.output_dir = f"{dir_prefix}-{date.strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f'输出目录: {self.output_dir}')
        return self.output_dir
    
    def predict(self, model, X_test: np.ndarray, y_test: np.ndarray, test_dates: pd.Series) -> pd.DataFrame:
        """
        在测试集上进行预测
        
        Args:
            model: 训练好的模型
            X_test: 测试特征
            y_test: 测试标签
            test_dates: 测试日期
        
        Returns:
            包含预测结果的DataFrame
        """
        print('\n在测试集上预测...')
        
        if self.mode == 'regression':
            test_pred = model.predict(X_test)
            res_df = pd.DataFrame({
                'label': y_test,
                'pred': test_pred,
                'info_date': test_dates.values
            })
        else:  # classification
            # 如果y_test是连续值，需要转换
            if not np.all(np.isin(y_test, [-1, 1])):
                y_test_cls = sign_label(y_test)
            else:
                y_test_cls = y_test
            
            test_proba = model.predict_proba(X_test)[:, 1]
            test_pred_class = (test_proba > 0.5).astype(int)
            
            res_df = pd.DataFrame({
                'label': y_test_cls,
                'pred': test_pred_class,
                'prob': test_proba,
                'info_date': test_dates.values
            })
        
        return res_df
    
    def calculate_metrics(self, res_df: pd.DataFrame) -> dict:
        """
        计算评估指标
        
        Args:
            res_df: 预测结果DataFrame
        
        Returns:
            评估指标字典
        """
        print('\n计算评估指标...')
        
        # 按日期计算符号一致性
        per_date = per_date_sign_agreement(res_df, date_col='info_date')
        print('\n按 info_date 的正负一致性:')
        print(per_date.to_string(index=False))
        
        overall_agreement = float(per_date['agreement'].mean())
        print(f"\n平均 info_date agreement = {overall_agreement:.4f}")
        
        metrics = {
            'overall_info_date_agreement': overall_agreement,
            'per_date_agreement': per_date
        }
        
        # 回归模式额外指标
        if self.mode == 'regression':
            from sklearn.metrics import mean_squared_error, mean_absolute_error
            mse = mean_squared_error(res_df['label'], res_df['pred'])
            mae = mean_absolute_error(res_df['label'], res_df['pred'])
            rmse = np.sqrt(mse)
            
            metrics.update({
                'rmse': float(rmse),
                'mae': float(mae),
                'mse': float(mse)
            })
            
            print(f'RMSE: {rmse:.4f}')
            print(f'MAE: {mae:.4f}')
        
        return metrics
    
    def save_results(
        self,
        model,
        res_df: pd.DataFrame,
        metrics: dict,
        best_params: dict,
        train_config: dict = None
    ):
        """
        保存所有结果
        
        Args:
            model: 训练好的模型
            res_df: 预测结果DataFrame
            metrics: 评估指标
            best_params: 最佳参数
            train_config: 训练配置
        """
        if self.output_dir is None:
            self.create_output_directory()
        
        print('\n保存结果...')
        
        # 1. 保存训练参数
        if train_config:
            params_json = os.path.join(self.output_dir, "params_json.json")
            with open(params_json, 'w', encoding='utf-8') as f:
                json.dump(train_config, f, ensure_ascii=False, indent=2)
            print(f"训练参数: {params_json}")
        
        # 2. 保存最佳超参数
        best_params_file = os.path.join(self.output_dir, "best_params.json")
        with open(best_params_file, 'w', encoding='utf-8') as f:
            json.dump(best_params, f, ensure_ascii=False, indent=2)
        print(f"最佳超参数: {best_params_file}")
        
        # 3. 保存按日期的一致性
        per_date_csv = os.path.join(self.output_dir, "per_date_sign_agreement.csv")
        metrics['per_date_agreement'].to_csv(per_date_csv, index=False)
        print(f"按日期一致性: {per_date_csv}")
        
        # 4. 保存评估摘要
        eval_summary = {k: v for k, v in metrics.items() if k != 'per_date_agreement'}
        eval_summary_json = os.path.join(self.output_dir, "eval_summary.json")
        with open(eval_summary_json, 'w', encoding='utf-8') as f:
            json.dump(eval_summary, f, ensure_ascii=False, indent=2)
        print(f"评估摘要: {eval_summary_json}")
        
        # 5. 保存预测结果
        res_df_file = os.path.join(self.output_dir, "test_predictions.csv")
        res_df.to_csv(res_df_file, index=False)
        print(f"预测结果: {res_df_file}")
        
        # 6. 保存模型
        self._save_model(model)
        
        # 7. 保存特征重要性
        if self.output_config.get('save_feature_importance', True):
            self._save_feature_importance(model)
    
    def _save_model(self, model):
        """保存模型文件"""
        model_json = self.output_config.get('model_json', 'xgb_best_model.json')
        model_pickle = self.output_config.get('model_pickle', 'xgb_best_model.pkl')
        
        # 保存JSON格式
        try:
            json_path = os.path.join(self.output_dir, model_json)
            model.get_booster().save_model(json_path)
            print(f'模型(JSON): {json_path}')
        except Exception as e:
            print(f'保存JSON模型失败: {e}')
        
        # 保存Pickle格式
        try:
            pickle_path = os.path.join(self.output_dir, model_pickle)
            joblib.dump(model, pickle_path)
            print(f'模型(PKL): {pickle_path}')
        except Exception as e:
            print(f'保存PKL模型失败: {e}')
    
    def _save_feature_importance(self, model):
        """保存特征重要性"""
        try:
            booster = model.get_booster()
            imp_dict = booster.get_score(importance_type="gain")
            
            # 转换为列表
            importance_items = [(fname, imp_dict.get(fname, 0.0)) for fname in booster.feature_names]
            importance_items.sort(key=lambda x: x[1], reverse=True)
            
            # 保存为CSV
            fi_csv = os.path.join(self.output_dir, "feature_importance.csv")
            with open(fi_csv, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["feature", "importance_gain"])
                writer.writerows(importance_items)
            print(f"特征重要性: {fi_csv}")
        except Exception as e:
            print(f"保存特征重要性失败: {e}")
    
    def visualize(self, res_df: pd.DataFrame, metrics: dict):
        """
        可视化结果
        
        Args:
            res_df: 预测结果DataFrame
            metrics: 评估指标
        """
        if self.output_dir is None:
            self.create_output_directory()
        
        print('\n生成可视化图表...')
        
        fig_size = self.viz_config.get('figure_size', [10, 6])
        style = self.viz_config.get('style', 'whitegrid')
        sns.set(style=style)
        
        if self.mode == 'regression':
            self._plot_regression(res_df, fig_size)
        else:
            self._plot_classification(metrics['per_date_agreement'], fig_size)
    
    def _plot_regression(self, res_df: pd.DataFrame, fig_size: list):
        """绘制回归结果对比图"""
        plt.figure(figsize=tuple(fig_size))
        
        res_df = res_df.reset_index(drop=True)
        res_df['idx'] = res_df.index
        
        plt.plot(res_df['idx'], res_df['label'], label='真实值', alpha=0.7)
        plt.plot(res_df['idx'], res_df['pred'], label='预测值', alpha=0.7)
        
        plt.xlabel("样本序号")
        plt.ylabel("值")
        plt.title("真实值 vs 预测值")
        plt.legend()
        plt.tight_layout()
        
        fig_file = os.path.join(self.output_dir, "label_pred_line.png")
        plt.savefig(fig_file, dpi=self.viz_config.get('dpi', 100))
        print(f"对比图: {fig_file}")
        plt.close()
    
    def _plot_classification(self, per_date: pd.DataFrame, fig_size: list):
        """绘制分类结果（按日期一致性柱状图）"""
        plt.figure(figsize=tuple(fig_size))
        
        sns.barplot(data=per_date, x='info_date', y='agreement')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("日期")
        plt.ylabel("正负一致性")
        plt.title("按日期的正负一致性")
        plt.tight_layout()
        
        fig_file = os.path.join(self.output_dir, "agreement_by_date_bar.png")
        plt.savefig(fig_file, dpi=self.viz_config.get('dpi', 100))
        print(f"一致性图: {fig_file}")
        plt.close()

