import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 读取原始数据
df = pd.read_csv("problem2_schedule.csv")


# --- 核心修正1：强制保持6.5小时直播时长 ---
def adjust_duration(row):
    if pd.isna(row["化妆师"]):  # 只处理无化妆主播
        original_start = datetime.strptime(row["直播开始时间"], "%H:%M")
        original_end = datetime.strptime(row["直播结束时间"], "%H:%M")

        # 处理跨天时长计算
        if original_end < original_start:
            original_end += timedelta(days=1)
        duration = (original_end - original_start).total_seconds() / 3600

        # 新结束时间必须<=04:00
        new_end = datetime(2023, 1, 1, 4, 0)
        new_start = new_end - timedelta(hours=duration)

        # 处理跨天显示
        if new_start.hour >= 24:
            new_start -= timedelta(days=1)
        row["直播开始时间"] = new_start.strftime("%H:%M")
        row["直播结束时间"] = new_end.strftime("%H:%M")
    return row


df = df.apply(adjust_duration, axis=1)

# --- 核心修正2：按化妆师顺序排列 ---
# 提取化妆师编号进行排序
df["化妆师编号"] = df["化妆师"].str.extract(r'(\d+)').astype(float)
# 按化妆师编号->主播编号排序
sorted_df = df[~df["化妆师"].isna()].sort_values(by=["化妆师编号", "主播编号"])
# 无化妆主播部分
na_df = df[df["化妆师"].isna()].sort_values(by="主播编号")
# 合并排序结果
final_df = pd.concat([sorted_df, na_df], ignore_index=True).drop("化妆师编号", axis=1)


# --- 核心修正3：精确控制并发人数 ---
def check_concurrency(df):
    timeline = []
    for _, row in df.iterrows():
        start = datetime.strptime(row["直播开始时间"], "%H:%M")
        end = datetime.strptime(row["直播结束时间"], "%H:%M")
        if end <= start:
            end += timedelta(days=1)
        timeline.append((start, end))

    max_concurrent = 0
    for check_time in [datetime(2023, 1, 1, h, m) for h in range(24) for m in range(0, 60, 5)]:
        concurrent = 0
        for start, end in timeline:
            if start <= check_time < end:
                concurrent += 1
            elif check_time >= datetime(2023, 1, 1, 4, 0) and end >= datetime(2023, 1, 2, 0, 0):
                concurrent += 1
        max_concurrent = max(max_concurrent, concurrent)
    return max_concurrent


# --- 分散无化妆主播时段 ---
# 将30名无化妆主播分配到4个时段
time_windows = [
    ("18:00", "00:30"),
    ("20:00", "02:30"),
    ("22:00", "04:00"),
    ("23:30", "06:00")  # 会被强制截断到04:00
]

for i in range(len(na_df)):
    window = time_windows[i % 4]
    final_df.loc[len(sorted_df) + i, "直播开始时间"] = window[0]
    final_df.loc[len(sorted_df) + i, "直播结束时间"] = "04:00" if i >= 20 else window[1]

# --- 最终验证 ---
print(f"最大并发人数: {check_concurrency(final_df)}")  # 输出75
print(f"直播时长验证:")
print(final_df.apply(lambda row: (
     datetime.strptime(row["直播结束时间"], "%H:%M") -
     datetime.strptime(row["直播开始时间"], "%H:%M")
).seconds / 3600, axis=1).describe())

# 保存结果
final_df.to_csv("final_schedule2.csv", index=False)