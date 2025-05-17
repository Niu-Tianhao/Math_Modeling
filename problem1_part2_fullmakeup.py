import math

required_k = 151
required_n = 151

max_per_staff = 13

min_staff_needed = math.ceil(required_k / max_per_staff)

profit_per_streamer = 4000
makeup_salary = 9000 * min_staff_needed
net_profit = profit_per_streamer * required_n - makeup_salary

print("化妆率提升至 100% 所需最少化妆师 =", min_staff_needed)
print("月净利润 = {:.2f} 元".format(net_profit))