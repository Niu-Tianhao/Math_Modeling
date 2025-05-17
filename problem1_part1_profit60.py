import pulp

# 初始化模型
model = pulp.LpProblem("Maximize_Profit", pulp.LpMaximize)

# 决策变量
n = pulp.LpVariable('n', lowBound=0, cat='Integer')  # 每日主播数
k = pulp.LpVariable('k', lowBound=0, cat='Integer')  # 每日化妆主播数

# 参数
max_rooms = 75
hours_per_room = 20
stream_hours = 6.5
max_daily_streamers = int(max_rooms * hours_per_room // stream_hours)  # ≈ 230
makeup_limit_per_day = 13 * 7  # 7 个化妆师每天最多服务 91 人
makeup_salary = 9000 * 7
profit_per_streamer = 4000

# 目标函数：月净利润 = 总月利润 - 化妆师工资
model += profit_per_streamer * n - makeup_salary, "Total_Net_Profit"

# 约束1：主播数量不超过每日最多
model += n <= max_daily_streamers, "StreamRoom_Capacity"

# 约束2：化妆人数不能超过化妆师最多可服务的人
model += k <= makeup_limit_per_day, "MakeupStaff_Limit"

# 约束3：化妆率不小于 60%
model += k >= 0.6 * n, "Makeup_Rate_60"

# 求解
model.solve()

# 输出结果
print("每日主播数 =", int(n.varValue))
print("其中化妆人数 =", int(k.varValue))
print("化妆率 = {:.2%}".format(k.varValue / n.varValue))
print("月净利润 = {:.2f} 元".format(pulp.value(model.objective)))
