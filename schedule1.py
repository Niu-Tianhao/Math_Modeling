from datetime import datetime, timedelta
import csv

# 参数设置
makeup_duration = timedelta(minutes=40)  # 化妆时间
live_duration = timedelta(hours=6, minutes=30)  # 直播时间
makeup_start = datetime.strptime("07:00", "%H:%M")  # 化妆师开始时间
max_daily_makeup = 91  # 每天最多化妆91人
total_anchors = 151  # 每日主播总数（60%化妆率）
rooms_available = [datetime.strptime("08:00", "%H:%M") for _ in range(75)]  # 75间直播间初始可用时间

schedule = []
anchor_id = 1

# 安排化妆主播（前91人）
for staff_id in range(7):  # 7名化妆师
    for i in range(13):  # 每个化妆师每天服务13人
        if anchor_id > max_daily_makeup:
            break
        # 计算化妆时间
        makeup_end = makeup_start + timedelta(minutes=40 * i + 40)
        # 找到最早可用的直播间
        earliest_room = min(rooms_available)
        # 直播开始时间 = max(化妆结束时间, 直播间可用时间)
        live_start = max(makeup_end, earliest_room)
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

# 安排未化妆主播（后60人）
for i in range(anchor_id, total_anchors + 1):
    earliest_room = min(rooms_available)
    live_start = earliest_room
    live_end = live_start + live_duration
    room_idx = rooms_available.index(earliest_room)
    rooms_available[room_idx] = live_end
    schedule.append({
        "化妆师": "N/A",
        "主播编号": f"主播{i}",
        "化妆开始时间": "N/A",
        "化妆结束时间": "N/A",
        "直播开始时间": live_start.strftime("%H:%M"),
        "直播结束时间": live_end.strftime("%H:%M"),
    })

# 导出CSV
with open('problem1_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["化妆师", "主播编号", "化妆开始时间", "化妆结束时间", "直播开始时间",
                                           "直播结束时间"])
    writer.writeheader()
    writer.writerows(schedule)