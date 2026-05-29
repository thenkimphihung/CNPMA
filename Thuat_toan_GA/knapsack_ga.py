import random
from dataclasses import dataclass
from typing import List, Tuple

# Kiểm tra thư viện vẽ đồ thị matplotlib
try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # pragma: no cover
    plt = None


# -----------------------------
# Dữ liệu bài toán Balo 0/1
# -----------------------------
# Định dạng vật phẩm: (tên, cân nặng, giá trị)
Item = Tuple[str, int, int]

DEFAULT_ITEMS: List[Item] = [
    ("Map & Matches", 1, 15),
    ("Water Bottle", 3, 20),
    ("Sleeping Bag", 4, 25),
    ("Canned Food", 5, 30),
    ("Medical First Aid Kit", 2, 22),
    ("Flashlight & Batteries", 2, 10),
    ("Multi-tool Knife", 1, 12),
    ("Portable Tent", 6, 35),
    ("Warm Clothes", 3, 15),
    ("Solar Power Bank", 2, 18),
]

DEFAULT_W_MAX: int = 15


# -----------------------------
# Cấu hình Thuật toán Di truyền (GA)
# -----------------------------
@dataclass
class GAConfig:
    population_size: int = 80       # Kích thước quần thể (P)
    max_generations: int = 100      # Số thế hệ tối đa
    crossover_prob: float = 0.8     # Xác suất lai ghép (Pc)
    mutation_prob: float = 0.02     # Xác suất đột biến (Pm trên từng gene)
    tournament_k: int = 3           # Số lượng cá thể tham gia đấu giải
    elitism_count: int = 2          # Số lượng cá thể tinh hoa được giữ lại
    patience: int = 20              # Dừng sớm nếu không cải thiện sau 20 thế hệ


# -----------------------------
# Các hàm xử lý cốt lõi của GA
# -----------------------------

def fitness(chromosome: List[int], items: List[Item], w_max: int) -> int:
    """Tính toán độ thích nghi (tổng giá trị). Trả về 0 nếu quá tải trọng."""
    total_w = 0
    total_v = 0
    for gene, (_, w, v) in zip(chromosome, items):
        if gene:
            total_w += w
            total_v += v

    if total_w <= w_max:
        return total_v
    return 0


def evaluate_population(population: List[List[int]], items: List[Item], w_max: int) -> List[int]:
    """Đánh giá độ thích nghi của toàn bộ quần thể."""
    return [fitness(ind, items, w_max) for ind in population]


def tournament_select(population: List[List[int]], fitnesses: List[int], k: int) -> List[int]:
    """Lựa chọn cá thể bằng phương pháp đấu giải (Tournament Selection)."""
    candidates = random.sample(range(len(population)), k)
    best_idx = max(candidates, key=lambda idx: fitnesses[idx])
    return population[best_idx][:]


def single_point_crossover(
    parent1: List[int], parent2: List[int], prob: float
) -> Tuple[List[int], List[int]]:
    """Lai ghép đơn điểm giữa hai cá thể cha mẹ."""
    if random.random() >= prob:
        return parent1[:], parent2[:]

    n_items = len(parent1)
    point = random.randint(1, n_items - 1)

    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def flip_bit_mutation(chromosome: List[int], prob: float) -> None:
    """Đột biến đảo bit (0 thành 1 và ngược lại) dựa trên xác suất."""
    for i in range(len(chromosome)):
        if random.random() < prob:
            chromosome[i] ^= 1


def make_initial_population(P: int, n_items: int) -> List[List[int]]:
    """Khởi tạo quần thể ban đầu ngẫu nhiên."""
    return [[random.randint(0, 1) for _ in range(n_items)] for _ in range(P)]


# -----------------------------
# Tiến trình chạy GA
# -----------------------------

def run_ga(config: GAConfig, items: List[Item], w_max: int, seed: int = 42):
    random.seed(seed)

    # Khởi tạo quần thể thế hệ đầu tiên
    population = make_initial_population(config.population_size, len(items))

    best_history: List[int] = []
    avg_history: List[float] = []

    best_overall = None
    best_overall_fit = -1
    no_improve = 0

    for _gen in range(config.max_generations):
        # 1. Đánh giá thế hệ hiện tại
        fitnesses = evaluate_population(population, items, w_max)

        gen_best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        gen_best_fit = fitnesses[gen_best_idx]
        gen_best = population[gen_best_idx][:]
        gen_avg = sum(fitnesses) / len(fitnesses)

        best_history.append(gen_best_fit)
        avg_history.append(gen_avg)

        # Kiểm tra cải thiện độ thích nghi tốt nhất
        if gen_best_fit > best_overall_fit:
            best_overall_fit = gen_best_fit
            best_overall = gen_best
            no_improve = 0
        else:
            no_improve += 1

        # Điều kiện dừng sớm (Patience)
        if no_improve >= config.patience:
            break

        # 2. Chiến lược tinh hoa (Elitism)
        ranked = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        elites = [population[i][:] for i in ranked[: config.elitism_count]]

        next_population: List[List[int]] = []
        next_population.extend(elites)

        # 3. Tạo quần thể thế hệ tiếp theo (Chọn lọc, Lai ghép, Đột biến)
        while len(next_population) < config.population_size:
            p1 = tournament_select(population, fitnesses, config.tournament_k)
            p2 = tournament_select(population, fitnesses, config.tournament_k)

            c1, c2 = single_point_crossover(p1, p2, config.crossover_prob)

            flip_bit_mutation(c1, config.mutation_prob)
            flip_bit_mutation(c2, config.mutation_prob)

            next_population.append(c1)
            if len(next_population) < config.population_size:
                next_population.append(c2)

        population = next_population

    return {
        "best_individual": best_overall,
        "best_fitness": best_overall_fit,
        "best_history": best_history,
        "avg_history": avg_history,
    }


def decode_solution(chromosome: List[int], items: List[Item]) -> Tuple[List[str], int, int]:
    """Giải mã chuỗi chromosome thành thông tin vật phẩm được chọn."""
    selected: List[str] = []
    total_w = 0
    total_v = 0

    for gene, (name, w, v) in zip(chromosome, items):
        if gene:
            selected.append(name)
            total_w += w
            total_v += v

    return selected, total_w, total_v


def plot_histories(best_history: List[int], avg_history: List[float], show: bool = True) -> None:
    """Vẽ đồ thị lịch sử tiến hóa độ thích nghi."""
    if plt is None:
        return

    generations = list(range(len(best_history)))

    plt.figure(figsize=(9, 5))
    plt.plot(generations, best_history, label="Best Fitness", linewidth=2)
    plt.plot(generations, avg_history, label="Average Fitness", linewidth=2, linestyle="--")
    plt.xlabel("Generation")
    plt.ylabel("Fitness (Value)")
    plt.title("GA - 0/1 Knapsack Fitness Evolution")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if show:
        plt.show()
    else:
        plt.close()


# -----------------------------
# Giao diện điều khiển (Console UI)
# -----------------------------

def prompt_int(msg: str, default: int = None, min_value: int = None) -> int:
    """Yêu cầu người dùng nhập số nguyên hợp lệ."""
    while True:
        raw = input(msg).strip()
        if raw == "" and default is not None:
            val = default
        else:
            try:
                val = int(raw)
            except ValueError:
                print("Giá trị không hợp lệ, nhập lại!")
                continue

        if min_value is not None and val < min_value:
            print(f"Giá trị phải >= {min_value}")
            continue

        return val


def prompt_items_subset() -> List[Item]:
    """Lọc danh sách các vật phẩm người dùng muốn giữ lại."""
    print("Danh sách vật phẩm mặc định (bạn chọn danh sách GIỮ lại):")
    for idx, (name, w, v) in enumerate(DEFAULT_ITEMS, start=1):
        print(f"{idx}. {name} (w={w}, v={v})")

    print("\nNhập các số thứ tự bạn muốn GIỮ (cách nhau bởi khoảng trắng).")
    print("Ví dụ: 1 3 4 6")
    raw = input("Nhấn Enter để dùng tất cả: ").strip()

    if raw == "":
        return DEFAULT_ITEMS[:]

    chosen: List[Item] = []
    seen = set()
    for part in raw.split():
        try:
            i = int(part)
        except ValueError:
            continue
        if 1 <= i <= len(DEFAULT_ITEMS) and i not in seen:
            chosen.append(DEFAULT_ITEMS[i - 1])
            seen.add(i)

    if not chosen:
        print("Bạn chưa chọn vật phẩm nào. Dùng mặc định.")
        return DEFAULT_ITEMS[:]

    return chosen


def main():
    print("Chọn 1 trong 2 chế độ:")
    print("1) Thêm/bớt vật phẩm (chọn danh sách vật phẩm có thể mang)")
    print("2) Nhập cân nặng tối đa W_MAX và tính phương án tối ưu")

    choice = None
    while choice not in (1, 2):
        try:
            choice = int(input("Nhập lựa chọn (1 hoặc 2): ").strip())
        except ValueError:
            choice = None

    if choice == 1:
        items = prompt_items_subset()
        w_max = prompt_int(
            f"Nhập W_max tối đa (kg) [mặc định {DEFAULT_W_MAX}]: ",
            default=DEFAULT_W_MAX,
            min_value=1,
        )
    else:
        items = DEFAULT_ITEMS[:]
        w_max = prompt_int(
            f"Nhập W_max tối đa (kg) [mặc định {DEFAULT_W_MAX}]: ",
            default=DEFAULT_W_MAX,
            min_value=1,
        )

    # Thiết lập cấu hình GA mẫu
    config = GAConfig(
        population_size=80,
        max_generations=100,
        crossover_prob=0.8,
        mutation_prob=0.02,
        tournament_k=3,
        elitism_count=2,
        patience=20,
    )

    # Chạy thuật toán
    result = run_ga(config=config, items=items, w_max=w_max, seed=42)

    best_ind = result["best_individual"]
    best_fit = result["best_fitness"]

    selected_names, total_w, total_v = decode_solution(best_ind, items)

    # In kết quả
    print("\n=== Best Solution Found ===")
    print(f"Max value: {total_v}")
    print(f"Total weight: {total_w} kg (limit: {w_max} kg)")

    print("Selected items:")
    if selected_names:
        for name in selected_names:
            print(f"- {name}")
    else:
        print("- (none)")

    print("\n=== GA Statistics ===")
    print(f"Best fitness overall: {best_fit}")
    print(f"Generations executed: {len(result['best_history'])}")

    # Tạo đồ thị (nếu matplotlib hoạt động, đặt show=True nếu bạn muốn bật cửa sổ đồ thị)
    plot_histories(result["best_history"], result["avg_history"], show=False)


if __name__ == "__main__":
    main()