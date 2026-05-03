import random
from statistics import mean
import matplotlib.pyplot as plt

# 시장 생성
def generate_market(num_buyers=20, num_sellers=20, seed=None):
    if seed is not None:
        random.seed(seed)

    # 구매자와 판매자의 value 및 cost를 무작위로 생성
    buyers = [round(random.uniform(0, 100), 2) for _ in range(num_buyers)] 
    sellers = [round(random.uniform(0, 100), 2) for _ in range(num_sellers)] 
    return buyers, sellers

# 최적의 이익 계산
def optimal_surplus(buyers, sellers):

    # 구매자 가치를 내림차순으로, 판매자 비용을 오름차순으로 정렬
    buyers_sorted = sorted(buyers, reverse=True)
    sellers_sorted = sorted(sellers)
    surplus = 0.0
    trades = 0

    # 가치가 비용보다 큰 쌍을 찾아 이익 계산
    for v, c in zip(buyers_sorted, sellers_sorted):
        if v > c:
            surplus += v - c
            trades += 1
        else:
            break

    return surplus, trades

# 실제 거래 시뮬레이션
def real_trading(buyers, sellers, max_rounds=10000, rng=None):
    if rng is None:
        rng = random

    # 구매자와 판매자의 수
    n_b, n_s = len(buyers), len(sellers)
    buyer_free = [True] * n_b
    seller_free = [True] * n_s

    surplus = 0.0
    trades = 0
    rounds_without_trade = 0
    max_no_trade_steps = n_b * n_s

    # 각 반복마다 무작위로 구매자와 판매자를 선택하여 거래 시도
    for _ in range(max_rounds):
        i = rng.randrange(n_b)
        j = rng.randrange(n_s)

        # 거래 가능 여부 확인
        if not buyer_free[i] or not seller_free[j]:
            rounds_without_trade += 1
        else:
            v, c = buyers[i], sellers[j]
            
            # value > cost인 경우 거래 성사
            if v > c:
                surplus += v - c
                trades += 1
                buyer_free[i] = False
                seller_free[j] = False
                rounds_without_trade = 0
            # 거래 실패 시 변수 증가
            else:
                rounds_without_trade += 1

        # 일정 거래 실패 횟수 달성 시 종료
        if rounds_without_trade > max_no_trade_steps:
            break

    return surplus, trades

# 균형 가격 및 수량 계산
def compute_equilibrium(buyers, sellers):
    # 구매자 가치를 내림차순으로, 판매자 비용을 오름차순으로 정렬
    buyers_sorted = sorted(buyers, reverse=True)
    sellers_sorted = sorted(sellers)

    # 균형 거래 수량 계산
    q_star = 0
    for v, c in zip(buyers_sorted, sellers_sorted):
        if v > c:
            q_star += 1
        else:
            break

    if q_star == 0:
        return 0, None

    # 균형 가격 계산
    v_star = buyers_sorted[q_star - 1]
    c_star = sellers_sorted[q_star - 1]
    p_star = (v_star + c_star) / 2.0
    return q_star, p_star

# 여러 반복 실행
def run_epochs(
    num_epochs=50,
    num_agents=20,
    runs_per_epoch=5,
    base_seed=0
):
    results = []

    # 각 반복마다 시장 생성 및 거래 시뮬레이션 수행
    for epoch in range(num_epochs):
        buyers, sellers = generate_market(
            num_buyers=num_agents,
            num_sellers=num_agents,
            seed=base_seed + epoch
        )

        cp_surplus, cp_trades = optimal_surplus(buyers, sellers)

        if cp_surplus == 0:
            print(f"반복 {epoch}: 건너뜀 (거래 불가)")
            continue

        epoch_ratios = []
        for run_id in range(runs_per_epoch):
            rng = random.Random(base_seed + epoch * 1000 + run_id)
            dec_surplus, dec_trades = real_trading(
                buyers,
                sellers,
                rng=rng
            )
            ratio = dec_surplus / cp_surplus if cp_surplus > 0 else 0.0
            epoch_ratios.append(ratio)

            # 결과
            # epoch, run_id, cp_surplus, cp_trades, dec_surplus, dec_trades, ratio
            # epoch: 반복 번호
            # run_id: 실행 번호
            # cp_surplus: 최적 이익
            # cp_trades: 최적 거래 수
            # dec_surplus: 실제 거래 이익
            # dec_trades: 실제 거래 수
            # ratio: 실제 이익 / 최적 이익 비율
            results.append({
                "epoch": epoch,
                "run_id": run_id,
                "cp_surplus": cp_surplus,
                "cp_trades": cp_trades,
                "dec_surplus": dec_surplus,
                "dec_trades": dec_trades,
                "ratio": ratio,
            })

        avg_epoch_ratio = mean(epoch_ratios)
        print(f"반복 {epoch}: 최적 이익={cp_surplus:.2f}, 평균 효율성={avg_epoch_ratio:.3f}")

    return results

def summarize_results(results):
    ratios = [r["ratio"] for r in results]
    if not ratios:
        print("유효한 시장 없음 (모든 반복에서 최적 이익 == 0).")
        return

    avg_ratio = mean(ratios)
    min_ratio = min(ratios)
    max_ratio = max(ratios)

    print("\n" + "="*50)
    print(f"데이터 포인트 수 (반복 * 실행): {len(results)}")
    print(f"평균 분산/최적 비율: {avg_ratio:.3f}")
    print(f"최소 비율: {min_ratio:.3f}")
    print(f"최대 비율: {max_ratio:.3f}")
    
    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False
    plt.figure(figsize=(7, 4))
    plt.hist(ratios, bins=10, edgecolor="black")
    plt.xlabel("분산 / 최적 이익 비율")
    plt.ylabel("빈도")
    plt.title("분산 거래 이익의 최적 이익 대비 비율 분포")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    NUM_EPOCHS = 200
    NUM_AGENTS = 20
    RUNS_PER_EPOCH = 5
    BASE_SEED = 42

    results = run_epochs(
        num_epochs=NUM_EPOCHS,
        num_agents=NUM_AGENTS,
        runs_per_epoch=RUNS_PER_EPOCH,
        base_seed=BASE_SEED,
    )

    summarize_results(results)

    exit(0)