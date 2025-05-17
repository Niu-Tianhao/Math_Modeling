from datetime import datetime, timedelta
import csv

# 参数设置
makeup_duration = timedelta(minutes=40)  # 化妆时间
live_duration = timedelta(hours=6, minutes=30)  # 直播时间
makeup_start = datetime.strptime("07:00", "%H:%M")  # 化妆师开始时间
max_daily_makeup = 151  # 每天需化妆151人（100%覆盖）
total_anchors = 151  # 每日主播总数
rooms_available = [datetime.strptime("08:00", "%H:%M") for _ in range(75)]  # 直播间初始可用时间
makeup_staff_count = 12  # 所需化妆师数（151/13≈12）

schedule = []
anchor_id = 1

# 安排化妆主播（151人）
for staff_id in range(makeup_staff_count):  # 12名化妆师
    for i in range(13):  # 每名化妆师每天服务13人
        if anchor_id > max_daily_makeup:
            break
        # 计算化妆时间
        makeup_end = makeup_start + timedelta(minutes=40 * i + 40)
        # 找到最早可用的直播间
        earliest_room = min(rooms_available)
        # 直播开始时间 = max(化妆结束时间, 直播间可用时间)
        live_start = max(makeup_end, earliest_room)
        # 强制等待时间≤5小时且直播结束时间≤凌晨4:00
        if (live_start - makeup_end) > timedelta(hours=5):
            live_start = makeup_end + timedelta(hours=5)  # 最多等待5小时
        live_end = live_start + live_duration
        if live_end > datetime.strptime("04:00", "%H:%M") + timedelta(days=1):
            live_start = datetime.strptime("21:30", "%H:%M")  # 确保直播结束在4:00前
            live_end = live_start + live_duration
        # 更新直播间可用时间
        room_idx = rooms_available.index(earliest_room)
        rooms_available[room_idx] = live_end

        schedule.append({
            "化妆师": f"化妆师{staff_id + 1}",
            "主播编号": f"主播{anchor_id}",
            "化妆开始时间": (makeup_start + timedelta(minutes=40 * i)).strftime("%H:%M"),
            "化妆结束时间": makeup_end.strftime("%H:%M"),
            "直播开始时间": live_start.strftime("%H:%M"),
            "直播结束时间": live_end.strftime("%H:%M"),
        })
        anchor_id += 1

# 导出CSV
with open('problem1_100%_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["化妆师", "主播编号", "化妆开始时间", "化妆结束时间", "直播开始时间",
                                           "直播结束时间"])
    writer.writeheader()
    writer.writerows(schedule)