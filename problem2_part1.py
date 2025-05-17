import pulp

# 初始化模型
model = pulp.LpProblem("Maximize_Profit_Problem2", pulp.LpMaximize)

# 决策变量
n = pulp.LpVariable('n', lowBound=0, upBound=230, cat='Integer')  # 每日主播总数
k = pulp.LpVariable('k', lowBound=0, upBound=195, cat='Integer')  # 每日化妆主播数

# 参数
makeup_staff_num = 15
makeup_limit = makeup_staff_num * 13
makeup_salary_total = 9000 * makeup_staff_num

profit_unmakeup = 4000
profit_makeup = profit_unmakeup * 1.2

# 目标函数
model += profit_makeup * k + profit_unmakeup * (n - k) - makeup_salary_total, "Total_Net_Profit"

# 约束条件
model += n <= 230, "Max_Streamer_Limit"
model += k <= makeup_limit, "Max_Makeup_Limit"
model += k <= n, "Makeup_Cannot_Exceed_Total"

# 求解
model.solve()

# 输出结果
print("每日主播总数 =", int(n.varValue))
print("每日化妆主播数 =", int(k.varValue))
print("化妆率 = {:.2%}".format(k.varValue / n.varValue if n.varValue > 0 else 0))
print("月净利润 = {:.2f} 元".format(pulp.value(model.objective)))