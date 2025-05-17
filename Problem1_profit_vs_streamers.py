import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# 设置全局样式
plt.style.use('seaborn-v0_8-pastel')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 数据准备
n_values = np.arange(100, 231, 10)
profit_values = 4000 * n_values - 9000 * 7  # 单位：元
makeup_rate = 0.6

# 创建画布和主坐标轴
fig, ax1 = plt.subplots(figsize=(10, 6))

# 净利润曲线 (主坐标轴)
line1 = ax1.plot(n_values, profit_values/10000,
                color='#2E86C1',
                linewidth=2.5,
                marker='o',
                markersize=8,
                label='月净利润')

ax1.set_xlabel('每日主播人数', fontsize=12, fontweight='bold')
ax1.set_ylabel('净利润 (万元)', color='#2E86C1', fontsize=12)
ax1.tick_params(axis='y', labelcolor='#2E86C1')
ax1.grid(True, linestyle='--', alpha=0.6)

# 化妆率曲线 (次坐标轴)
ax2 = ax1.twinx()
line2 = ax2.plot(n_values, [makeup_rate]*len(n_values),
                color='#E74C3C',
                linewidth=2.5,
                linestyle='--',
                label='化妆率')

ax2.set_ylabel('化妆率', color='#E74C3C', fontsize=12)
ax2.tick_params(axis='y', labelcolor='#E74C3C')
ax2.set_ylim(0, 1)  # 固定化妆率坐标范围

# 添加标注点（已去除箭头）
max_idx = np.argmax(profit_values)
ax1.annotate(f'最大利润: {profit_values[max_idx]/10000:.1f}万元',
             xy=(n_values[max_idx], profit_values[max_idx]/10000),
             xytext=(10, 30),
             textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8))

# 合并图例
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=10)

# 格式化坐标轴
def yuan_formatter(x, pos):
    return f'{x:.0f}'
ax1.yaxis.set_major_formatter(FuncFormatter(yuan_formatter))

# 添加标题和注释
plt.title('主播规模与经营效益关系分析\n(化妆师固定7人，化妆率60%)',
          fontsize=14, fontweight='bold', pad=20)
plt.figtext(0.5, 0.01,
            '注：假设每个主播月均利润4000元，化妆师月工资9000元',
            ha='center', fontsize=9, style='italic')

# 调整布局
plt.tight_layout()
plt.subplots_adjust(bottom=0.15)

plt.show()