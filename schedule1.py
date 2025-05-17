from datetime import datetime, timedelta
import csv

makeup_duration = timedelta(minutes = 40) # 每位主播化妆时间
live_duration = timedelta(hours = 6, minutes = 30) # 每位主播直播时间
makeup_start_time = datetime.strptime("07:00", "%H:%M")
schedule = []

anchor_id = 1
for staff_id in range(7): # 7个化妆师
    for i in range(13): # 每个化妆师每天最多服务 13 个主播
        if anchor_id > 91: # 每日化妆主播人数为 91
            break
        makeup_start = makeup_start_time + timedelta(minutes = 40 * i) # 每个主播开始化妆时间
        makeup_end = makeup_start + makeup_duration # 化妆结束时间
        live_start = makeup_end + timedelta(hours = 1) # 直播开始时间
        live_end = live_start + live_duration # 直播结束时间

        schedule.append({
            '化妆师': f'化妆师{staff_id + 1}',
            '主播编号': f'主播{anchor_id}',
            '化妆开始时间': makeup_start.strftime("%H:%M"),
            '化妆结束时间': makeup_end.strftime("%H:%M"),
            '直播开始时间': live_start.strftime("%H:%M"),
            '直播结束时间': live_end.strftime("%H:%M"),
        })
        anchor_id += 1
# 安排未化妆主播(剩下的n - k个)
for i in range(anchor_id, 151 + 1):
    live_start = datetime.strptime("08:00", "%H:%M") + timedelta(minutes = 30 *(i - anchor_id))
    live_end = live_start + live_duration
    schedule.append({
        '化妆师': '无',
        '主播编号': f'主播{i}',
        '化妆开始时间': '无',
        '化妆结束时间': '无',
        '直播开始时间': live_start.strftime("%H:%M"),
        '直播结束时间': live_end.strftime("%H:%M"),
    })

with open('problem1_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['化妆师', '主播编号', '化妆开始时间', '化妆结束时间', '直播开始时间', '直播结束时间'])
    writer.writeheader()
    writer.writerows(schedule)