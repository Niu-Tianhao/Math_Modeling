from datetime import datetime, timedelta
import csv


def adjust_live_time(live_start, live_duration):
    """确保直播结束时间不超过次日4:00"""
    # 定义当天的4:00和次日的4:00
    current_day_4am = live_start.replace(hour=4, minute=0, second=0)
    next_day_4am = current_day_4am + timedelta(days=1)

    # 计算直播结束时间
    live_end = live_start + live_duration

    # 如果直播结束超过次日4:00
    if live_end > next_day_4am:
        # 计算最晚允许的直播开始时间
        latest_start = next_day_4am - live_duration
        # 如果最晚开始时间早于当前时间，强制调整
        if latest_start < live_start:
            live_start = latest_start
            live_end = live_start + live_duration
    return live_start, live_end


# 参数设置
makeup_duration = timedelta(minutes=40)
live_duration = timedelta(hours=6, minutes=30)
makeup_start = datetime.strptime("07:00", "%H:%M")
rooms_available = [datetime.strptime("08:00", "%H:%M") for _ in range(75)]
makeup_staff_count = 15
total_anchors = 230
max_makeup = 195

schedule = []
anchor_id = 1

# 初始化化妆师工作时间表
staff_schedules = {i: {"next_available": makeup_start} for i in range(makeup_staff_count)}

# 安排化妆主播（195人）
for anchor_id in range(1, max_makeup + 1):
    # 选择最早可用的化妆师
    staff_id = min(staff_schedules, key=lambda x: staff_schedules[x]["next_available"])
    staff = staff_schedules[staff_id]

    # 计算化妆时间
    makeup_start_time = staff["next_available"]
    makeup_end_time = makeup_start_time + makeup_duration

    # 检查化妆师工作时间是否超限（≤17:00）
    if makeup_end_time > datetime.strptime("17:00", "%H:%M"):
        raise ValueError("化妆师工作时间超过17:00")

    # 分配直播间
    earliest_room = min(rooms_available)
    live_start = max(makeup_end_time, earliest_room)

    # 强制等待时间≤5小时
    if (live_start - makeup_end_time) > timedelta(hours=5):
        live_start = makeup_end_time + timedelta(hours=5)

    # 精确调整直播时间
    live_start, live_end = adjust_live_time(live_start, live_duration)

    # 检查直播开始时间是否在运营时段内（8:00-4:00次日）
    if live_start < datetime.strptime("08:00", "%H:%M"):
        live_start = datetime.strptime("08:00", "%H:%M")
        live_end = live_start + live_duration
        live_start, live_end = adjust_live_time(live_start, live_duration)

    # 更新资源
    room_idx = rooms_available.index(earliest_room)
    rooms_available[room_idx] = live_end
    staff["next_available"] = makeup_end_time

    schedule.append({
        "化妆师": f"化妆师{staff_id + 1}",
        "主播编号": f"主播{anchor_id}",
        "化妆开始时间": makeup_start_time.strftime("%H:%M"),
        "化妆结束时间": makeup_end_time.strftime("%H:%M"),
        "直播开始时间": live_start.strftime("%H:%M"),
        "直播结束时间": live_end.strftime("%H:%M"),
        "是否化妆": "是"
    })

# 安排未化妆主播（35人）
for anchor_id in range(max_makeup + 1, total_anchors + 1):
    earliest_room = min(rooms_available)
    live_start = earliest_room
    live_end = live_start + live_duration

    # 调整未化妆主播的时间
    live_start, live_end = adjust_live_time(live_start, live_duration)

    room_idx = rooms_available.index(earliest_room)
    rooms_available[room_idx] = live_end

    schedule.append({
        "化妆师": "N/A",
        "主播编号": f"主播{anchor_id}",
        "化妆开始时间": "N/A",
        "化妆结束时间": "N/A",
        "直播开始时间": live_start.strftime("%H:%M"),
        "直播结束时间": live_end.strftime("%H:%M"),
        "是否化妆": "否"
    })

# 导出CSV
with open('problem2_schedule.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["化妆师", "主播编号", "化妆开始时间", "化妆结束时间", "直播开始时间",
                                           "直播结束时间", "是否化妆"])
    writer.writeheader()
    writer.writerows(schedule)