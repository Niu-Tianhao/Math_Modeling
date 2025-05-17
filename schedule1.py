from datetime import datetime, timedelta
import csv

# 参数
num_makeup_staff = 7
makeup_per_staff = 13
makeup_duration = timedelta(minutes=40)
live_duration = timedelta(hours=6, minutes=30)
makeup_start_time = datetime.strptime("07:00", "%H:%M")

schedule = []

for staff_id in range(num_makeup_staff):
    for i in range(makeup_per_staff):
        makeup_start = makeup_start_time + timedelta(minutes=40 * i)
        makeup_end = makeup_start + makeup_duration
        live_start = makeup_end + timedelta(hours=1)
        live_end = live_start + live_duration

        # 主播编号，顺序递增
        anchor_id = staff_id * makeup_per_staff + i + 1
        if anchor_id > 151:
            break

        schedule.append({
            '化妆师': f'化妆师{staff_id + 1}',
            '主播编号': f'主播{anchor_id}',
            '化妆开始时间': makeup_start.strftime("%H:%M"),
            '化妆结束时间': makeup_end.strftime("%H:%M"),
            '直播开始时间': live_start.strftime("%H:%M"),
            '直播结束时间': live_end.strftime("%H:%M"),
        })

# 导出CSV
with open('problem1_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['化妆师', '主播编号', '化妆开始时间', '化妆结束时间', '直播开始时间', '直播结束时间'])
    writer.writeheader()
    writer.writerows(schedule)

print("排班表已生成并保存为 problem1_schedule.csv ，请查收！")
