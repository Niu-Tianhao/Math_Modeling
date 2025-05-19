import random
from math import exp
from copy import deepcopy

# 确保安装DEAP: pip install deap pandas

from deap import base, creator, tools

# === 参数定义 ===
NUM_ANCHORS = 225
LEVEL_COUNTS = [75, 75, 75]              # 各级主播人数
LEVEL_REVENUE = [4000, 7000, 10000]      # 月基础收益
STREAM_DURATION = 39                     # 每主播直播时长：39段（6.5小时）
STREAM_START_MIN = 0
STREAM_START_MAX = 120 - STREAM_DURATION # 可选起始段编号
NUM_ROOMS = 75

MAKEUP_TIME = 4       # 化妆用时4段
MAKEUP_START_MIN = 0  # 对应07:00
MAKEUP_START_MAX = 60 - MAKEUP_TIME  # 对应17:00结束

GOLDEN_START = 60     # 18:00对应段编号
GOLDEN_END = 84       # 22:00对应段编号

MAKEUP_ARTISTS = 15
MAKEUP_MONTHLY_SALARY = 9000
WORKING_DAYS_MONTH = 26
DAILY_MAKEUP_COST = MAKEUP_ARTISTS * MAKEUP_MONTHLY_SALARY / WORKING_DAYS_MONTH

# === DEAP 设置 ===
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # 最大化利润
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("randomStart", random.randint, STREAM_START_MIN, STREAM_START_MAX)
toolbox.register("randomRoom", random.randint, 0, NUM_ROOMS - 1)
toolbox.register("randomMakeupFlag", random.randint, 0, 1)
toolbox.register("randomMakeupStart", random.randint, MAKEUP_START_MIN, MAKEUP_START_MAX)

# 个体初始化函数：225个主播，每个4个属性
def init_individual():
    ind = creator.Individual()
    for i in range(NUM_ANCHORS):
        ind.append(toolbox.randomStart())
        ind.append(toolbox.randomRoom())
        ind.append(toolbox.randomMakeupFlag())
        ind.append(toolbox.randomMakeupStart())
    return ind

toolbox.register("individual", init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# === 适应度评估函数 ===
def eval_schedule(ind):
    total_revenue = 0.0
    penalty = 0.0

    # 计算每级主播的日基础收益
    base_daily = [rev / WORKING_DAYS_MONTH for rev in LEVEL_REVENUE]

    # 检查冲突：房间占用 & 化妆人数
    occupancy = {}      # (room, time_segment) -> count
    makeup_timeline = [0] * 60  # 每10分钟化妆人数（07:00-17:00共60段）

    makeup_count = 0
    for idx in range(NUM_ANCHORS):
        # 确定主播等级与基础收益
        level = idx // LEVEL_COUNTS[0]  # 0=低级,1=中级,2=高级
        base_rev = base_daily[level]

        start = ind[4*idx]
        room = ind[4*idx+1]
        makeup_flag = ind[4*idx+2]
        makeup_start = ind[4*idx+3]

        # 检查合法直播段
        if start < STREAM_START_MIN or start > STREAM_START_MAX:
            penalty += 1e6

        # 计算黄金时段重叠段数
        segs = range(start, start + STREAM_DURATION)
        golden_segs = len([s for s in segs if GOLDEN_START <= s < GOLDEN_END])
        base_per_seg = base_rev / STREAM_DURATION
        revenue = base_rev + base_per_seg * 0.5 * golden_segs

        # 化妆约束
        if makeup_flag == 1:
            makeup_end = makeup_start + MAKEUP_TIME
            # 化妆结束不得超过17:00
            if makeup_end > 60:
                penalty += 1e5
            # 化妆结束后5小时（30段）内开播：将化妆时段映射到直播段
            makeup_end_stream = makeup_start - 6 + MAKEUP_TIME
            if start < makeup_end_stream or start > makeup_end_stream + 30:
                penalty += 1e5
            makeup_count += 1
            # 标记化妆人数
            for t in range(makeup_start, makeup_end):
                if t < 60:
                    makeup_timeline[t] += 1

        # 若化妆，收益乘1.2
        if makeup_flag == 1:
            revenue *= 1.2
        total_revenue += revenue

        # 检查房间占用冲突
        for t in segs:
            if t >= 120:
                penalty += 1e6
                continue
            key = (room, t)
            occupancy[key] = occupancy.get(key, 0) + 1
            if occupancy[key] > 1:
                penalty += 1000  # 房间冲突罚分

    # 化妆师并发限制：任意时刻最多15人化妆
    for cnt in makeup_timeline:
        if cnt > MAKEUP_ARTISTS:
            penalty += (cnt - MAKEUP_ARTISTS) * 1000
    # 总化妆次数不得超过15*12=180
    if makeup_count > MAKEUP_ARTISTS * 12:
        penalty += (makeup_count - MAKEUP_ARTISTS * 12) * 1000

    total_cost = DAILY_MAKEUP_COST
    profit = total_revenue - total_cost
    return profit - penalty,

toolbox.register("evaluate", eval_schedule)

# === 遗传算子 ===
# 交叉：以主播为单位交换4属性块
def cxAnchors(ind1, ind2):
    for i in range(NUM_ANCHORS):
        if random.random() < 0.5:
            for j in range(4):
                idx = 4*i + j
                ind1[idx], ind2[idx] = ind2[idx], ind1[idx]
    return ind1, ind2

toolbox.register("mate", cxAnchors)

# 变异：逐个主播属性随机变
def mutateSchedule(individual, indpb=0.02):
    for i in range(NUM_ANCHORS):
        if random.random() < indpb:
            individual[4*i] = random.randint(STREAM_START_MIN, STREAM_START_MAX)
        if random.random() < indpb:
            individual[4*i+1] = random.randint(0, NUM_ROOMS-1)
        if random.random() < indpb:
            individual[4*i+2] = random.randint(0,1)
        if random.random() < indpb:
            individual[4*i+3] = random.randint(MAKEUP_START_MIN, MAKEUP_START_MAX)
    return individual,

toolbox.register("mutate", mutateSchedule)
toolbox.register("select", tools.selTournament, tournsize=3)

# === 遗传算法主循环 ===
POP_SIZE = 50
GENERATIONS = 50
CXPB = 0.6
MUTPB = 0.2

def run_ga():
    pop = toolbox.population(n=POP_SIZE)
    # 评估初始种群
    for ind in pop:
        ind.fitness.values = toolbox.evaluate(ind)

    for gen in range(GENERATIONS):
        # 选择
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))
        # 交叉和变异
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # 评估新种群
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid:
            ind.fitness.values = toolbox.evaluate(ind)
        pop[:] = offspring

        # 打印每代最佳适应度
        best_fit = max(ind.fitness.values[0] for ind in pop)
        print(f"第 {gen} 代: 最佳利润 = {best_fit:.2f}")

    best_ind = tools.selBest(pop, 1)[0]
    return best_ind

# === 模拟退火细调 ===
def simulated_annealing(schedule, eval_func, T0=1000, alpha=0.95, iterations=1000):
    current = deepcopy(schedule)
    current_fitness = eval_func(current)[0]
    best = deepcopy(current)
    best_fitness = current_fitness
    T = T0
    for i in range(iterations):
        neighbor = deepcopy(current)
        # 随机选一个主播，随机改一个属性
        a = random.randrange(NUM_ANCHORS)
        attr = random.randrange(4)
        if attr == 0:
            neighbor[4*a] = random.randint(STREAM_START_MIN, STREAM_START_MAX)
        elif attr == 1:
            neighbor[4*a+1] = random.randint(0, NUM_ROOMS-1)
        elif attr == 2:
            neighbor[4*a+2] = random.randint(0,1)
        else:
            neighbor[4*a+3] = random.randint(MAKEUP_START_MIN, MAKEUP_START_MAX)
        neighbor_fitness = eval_func(neighbor)[0]
        # 接受准则
        if neighbor_fitness > current_fitness or random.random() < exp((neighbor_fitness-current_fitness)/T):
            current, current_fitness = neighbor, neighbor_fitness
            if current_fitness > best_fitness:
                best, best_fitness = deepcopy(current), current_fitness
        T *= alpha
    return best, best_fitness

# === 主程序 ===
if __name__ == "__main__":
    best_ind = run_ga()
    print("GA获得的最佳利润:", eval_schedule(best_ind)[0])
    refined, refined_fit = simulated_annealing(best_ind, eval_schedule, T0=1000, alpha=0.99, iterations=5000)
    print("模拟退火优化后最佳利润:", refined_fit)

    # 将最终调度结果输出为CSV
    import pandas as pd
    records = []
    for i in range(NUM_ANCHORS):
        level = i // LEVEL_COUNTS[0]
        anchor_id = i + 1
        makeup_flag = refined[4*i+2]
        if makeup_flag == 1:
            ms = refined[4*i+3]
            # 化妆开始时间
            hr = 7 + (ms // 6)
            minute = (ms % 6) * 10
            makeup_time = f"{hr:02d}:{minute:02d}"
        else:
            makeup_time = ""
        start_seg = refined[4*i]
        end_seg = start_seg + STREAM_DURATION
        start_hr = 8 + (start_seg // 6)
        start_min = (start_seg % 6) * 10
        end_hr = 8 + (end_seg // 6)
        if end_hr >= 24:  # 过午夜转换
            end_hr -= 24
        end_min = (end_seg % 6) * 10
        room = refined[4*i+1] + 1

        base_rev = LEVEL_REVENUE[level] / WORKING_DAYS_MONTH
        segs = range(start_seg, end_seg)
        golden_segs = len([s for s in segs if GOLDEN_START <= s < GOLDEN_END])
        revenue = base_rev + (base_rev/STREAM_DURATION)*0.5*golden_segs
        if makeup_flag == 1:
            revenue *= 1.2
        records.append({
            "主播ID": anchor_id,
            "主播等级": ["低级","中级","高级"][level],
            "是否化妆": "是" if makeup_flag else "否",
            "化妆开始时间": makeup_time,
            "直播开始时间": f"{start_hr:02d}:{start_min:02d}",
            "直播结束时间": f"{end_hr:02d}:{end_min:02d}",
            "直播间编号": room,
            "预估当日收益": round(revenue, 2)
        })

    df = pd.DataFrame(records)
    df.to_csv("schedule3.csv", index=False, encoding="utf-8-sig")

    total_revenue = df["预估当日收益"].sum()
    total_cost = DAILY_MAKEUP_COST
    net_profit = total_revenue - total_cost
    print(f"总收益: {total_revenue:.2f}元, 总成本: {total_cost:.2f}元, 净利润: {net_profit:.2f}元")
