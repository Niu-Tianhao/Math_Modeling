from datetime import datetime, timedelta
import csv

# 参数设置
num_makeup_staff = 15
makeup_per_staff = 13
makeup_duration = timedelta(minutes=40)
live_duration = timedelta(hours=6, minutes=30)
makeup_start_time = datetime.strptime("07:00", "%H:%M")

# 你的模型求解结果
daily_total_anchors = 230       # 每日主播总数
daily_makeup_anchors = 195      # 每日化妆主播数

schedule = []
anchor_id = 1

# 化妆主播排班
for staff_id in range(num_makeup_staff):
    for i in range(makeup_per_staff):
        if anchor_id > daily_makeup_anchors:
            break  # 超过化妆主播数退出
        makeup_start = makeup_start_time + timedelta(minutes=40 * i)
        makeup_end = makeup_start + makeup_duration
        live_start = makeup_end + timedelta(hours=1)  # 直播开始时间设为化妆结束后1小时
        live_end = live_start + live_duration

        schedule.append({
            '化妆师': f'化妆师{staff_id + 1}',
            '主播编号': f'主播{anchor_id}',
            '化妆开始时间': makeup_start.strftime("%H:%M"),
            '化妆结束时间': makeup_end.strftime("%H:%M"),
            '直播开始时间': live_start.strftime("%H:%M"),
            '直播结束时间': live_end.strftime("%H:%M"),
            '是否化妆': '是'
        })
        anchor_id += 1

# 未化妆主播直播排班
num_unmakeup = daily_total_anchors - daily_makeup_anchors
if num_unmakeup > 0:
    # 直播分3个批次开始时间
    live_batches = [datetime.strptime(t, "%H:%M") for t in ["08:00", "14:30", "21:00"]]
    for i in range(num_unmakeup):
        batch_idx = i % 3
        live_start = live_batches[batch_idx]
        live_end = live_start + live_duration
        schedule.append({
            '化妆师': '无',
            '主播编号': f'主播{anchor_id}',
            '化妆开始时间': '',
            '化妆结束时间': '',
            '直播开始时间': live_start.strftime("%H:%M"),
            '直播结束时间': live_end.strftime("%H:%M"),
            '是否化妆': '否'
        })
        anchor_id += 1

# 写入CSV文件
with open('problem2_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['化妆师', '主播编号', '化妆开始时间', '化妆结束时间', '直播开始时间', '直播结束时间', '是否化妆'])
    writer.writeheader()
    writer.writerows(schedule)

print("问题二排班表已生成 problem2_schedule.csv，请查收！")
