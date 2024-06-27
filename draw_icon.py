import matplotlib.pyplot as plt

# 创建一个新的图形窗口
fig, ax = plt.subplots(figsize=(4, 4))  # 设置图像大小为1x1英寸

# 设置坐标轴的范围和隐藏坐标轴
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1, 1)
ax.axis('off')

# 绘制LM字样的文字
ax.text(-0.5, 0, 'L', fontsize=100, fontweight='bold', va='center', ha='center', alpha=0.5, color='blue')
ax.text(0.5, 0, 'M', fontsize=100, fontweight='bold', va='center', ha='center', alpha=0.5, color='blue')

# 保存图像到文件，设置透明背景
plt.savefig('LM_logo.png', transparent=True, bbox_inches='tight', pad_inches=0)

# 显示图像
plt.show()
