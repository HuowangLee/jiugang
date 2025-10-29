"""
测试样本权重计算功能
"""
import numpy as np
from utils import calculate_sample_weights

def test_sample_weights():
    """测试样本权重计算"""
    print("=" * 80)
    print("样本权重功能测试")
    print("=" * 80)
    
    # 模拟price_diff数据
    price_diff = np.array([0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    
    print("\n测试数据 (price_diff):")
    print(price_diff)
    
    # 测试1: 线性权重
    print("\n" + "=" * 80)
    print("测试1: 线性权重 (weight_type='linear', eps=0.01)")
    print("=" * 80)
    weights_linear = calculate_sample_weights(price_diff, weight_type='linear', eps=0.01)
    print("权重计算公式: weight = |price_diff| + eps")
    print("计算结果:")
    for pd, w in zip(price_diff, weights_linear):
        print(f"  price_diff={pd:6.2f}  ->  weight={w:8.4f}")
    print(f"权重统计: min={weights_linear.min():.4f}, max={weights_linear.max():.4f}, mean={weights_linear.mean():.4f}")
    
    # 测试2: 非线性权重 (alpha=2)
    print("\n" + "=" * 80)
    print("测试2: 非线性权重 (weight_type='nonlinear', eps=1e-6, alpha=2)")
    print("=" * 80)
    weights_nonlinear_2 = calculate_sample_weights(price_diff, weight_type='nonlinear', eps=1e-6, alpha=2)
    print("权重计算公式: weight = (|price_diff| + eps) ^ 2")
    print("计算结果:")
    for pd, w in zip(price_diff, weights_nonlinear_2):
        print(f"  price_diff={pd:6.2f}  ->  weight={w:8.4f}")
    print(f"权重统计: min={weights_nonlinear_2.min():.4f}, max={weights_nonlinear_2.max():.4f}, mean={weights_nonlinear_2.mean():.4f}")
    
    # 测试3: 非线性权重 (alpha=3)
    print("\n" + "=" * 80)
    print("测试3: 非线性权重 (weight_type='nonlinear', eps=1e-6, alpha=3)")
    print("=" * 80)
    weights_nonlinear_3 = calculate_sample_weights(price_diff, weight_type='nonlinear', eps=1e-6, alpha=3)
    print("权重计算公式: weight = (|price_diff| + eps) ^ 3")
    print("计算结果:")
    for pd, w in zip(price_diff, weights_nonlinear_3):
        print(f"  price_diff={pd:6.2f}  ->  weight={w:8.4f}")
    print(f"权重统计: min={weights_nonlinear_3.min():.4f}, max={weights_nonlinear_3.max():.4f}, mean={weights_nonlinear_3.mean():.4f}")
    
    # 测试4: 比较不同权重方式
    print("\n" + "=" * 80)
    print("测试4: 权重对比")
    print("=" * 80)
    print(f"{'price_diff':<12} {'Linear':<12} {'Alpha=2':<12} {'Alpha=3':<12}")
    print("-" * 50)
    for pd, w_lin, w_nl2, w_nl3 in zip(price_diff, weights_linear, weights_nonlinear_2, weights_nonlinear_3):
        print(f"{pd:<12.2f} {w_lin:<12.4f} {w_nl2:<12.4f} {w_nl3:<12.4f}")
    
    # 测试5: 归一化权重对比（相对于最小权重）
    print("\n" + "=" * 80)
    print("测试5: 归一化权重对比 (相对于最小权重)")
    print("=" * 80)
    norm_linear = weights_linear / weights_linear.min()
    norm_nl2 = weights_nonlinear_2 / weights_nonlinear_2.min()
    norm_nl3 = weights_nonlinear_3 / weights_nonlinear_3.min()
    
    print(f"{'price_diff':<12} {'Linear':<12} {'Alpha=2':<12} {'Alpha=3':<12}")
    print("-" * 50)
    for pd, n_lin, n_nl2, n_nl3 in zip(price_diff, norm_linear, norm_nl2, norm_nl3):
        print(f"{pd:<12.2f} {n_lin:<12.2f}x {n_nl2:<12.2f}x {n_nl3:<12.2f}x")
    
    print("\n观察:")
    print("- 线性权重: 权重增长速度恒定")
    print("- 非线性权重(alpha=2): 权重增长加速，大差异样本权重显著增加")
    print("- 非线性权重(alpha=3): 权重增长更快，对大差异样本更加敏感")
    
    # 测试6: 错误处理
    print("\n" + "=" * 80)
    print("测试6: 错误处理")
    print("=" * 80)
    try:
        calculate_sample_weights(price_diff, weight_type='invalid')
        print("错误：应该抛出异常但没有")
    except ValueError as e:
        print(f"✓ 正确捕获错误: {e}")
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)

if __name__ == '__main__':
    test_sample_weights()

