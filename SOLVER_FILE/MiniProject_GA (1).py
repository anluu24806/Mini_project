import random
import os
import time

def take_input():
    N, M = map(int, input().split())
    t = []
    g = []
    s = []
    for i in range(N):
        ti, gi, si = map(int, input().split())
        t.append(ti)
        g.append(gi-1)
        s.append(si)
    c = list(map(int, input().split()))
    return N, M, t, g, s, c
def file_input(file):
    with open(file, "r") as fin:
        lines = fin.readlines()
        N, M = map(int, lines[0].split())
        t = []
        g = []
        s = []
        for i in range(1, N + 1):
            ti, gi, si = map(int, lines[i].split())
            t.append(ti)
            g.append(gi-1)
            s.append(si)
        c = list(map(int, lines[-1].split()))
    return N, M, t, g, s, c

def generate_individual():
    schedule = {}  # lớp -> list of (slot, room)
    used_slots = {i: set() for i in range(5 * SLOTS_PER_DAY)}  # slot -> phòng đã dùng
    teacher_busy = {i: set() for i in range(MAX_TEACHER)}  # giáo viên -> slot bận

    for i, (ti, gi, si) in enumerate(classes):
        assigned = []
        attempts = 0
        success = False

        while attempts < 40:
            day = random.randint(0, 4)  # chọn ngày (0 đến 4)
            start_in_day = random.randint(0, SLOTS_PER_DAY - ti)  # tiết bắt đầu trong ngày
            start_slot = day * SLOTS_PER_DAY + start_in_day
            slot_range = list(range(start_slot, start_slot + ti))

            # Kiểm tra xem giáo viên và phòng có bận không
            room_candidates = [r for r in range(M) if c[r] >= si]
            random.shuffle(room_candidates)

            for room in room_candidates:
                if all(room not in used_slots[s] for s in slot_range) and \
                   all(s not in teacher_busy[gi] for s in slot_range):
                    # Gán lịch
                    assigned = [(s, room) for s in slot_range]
                    for s in slot_range:
                        used_slots[s].add(room)
                        teacher_busy[gi].add(s)
                    schedule[i] = assigned
                    success = True
                    break
            if success:
                break
            attempts += 1
    return schedule

def fitness(schedule, total_classes):
    score = 0
    used_slots = set()
    used_rooms = set()

    for cls, allocations in schedule.items():
        slots = [s for (s, _) in allocations]
        rooms = [r for (_, r) in allocations]

        # Ràng buộc liền nhau (đã đảm bảo từ đầu), nhưng có thể kiểm tra lại
        if len(slots) != (max(slots) - min(slots) + 1):
            continue  # vi phạm liền kề

        score += 1  # thưởng 10 điểm cho mỗi lớp được xếp

        # Khuyến khích dùng ít slot/phòng
        used_slots.update(slots)
        used_rooms.update(rooms)

    # Phạt nhẹ nếu dùng quá nhiều slot/phòng
    penalty = 0.2 * len(used_slots) + 0.3 * len(used_rooms)

    final_score = score - penalty
    return final_score

def crossover(parent1, parent2, classes, room_caps):
    """
    parent1, parent2: dict[class_id] = [(slot, room)]
    classes: list of (t, g, s) for each class
    room_caps: danh sách sức chứa phòng
    """
    child = {}
    used_slots = {i: set() for i in range(5 * SLOTS_PER_DAY)}  # slot -> phòng đã dùng
    teacher_busy = {i: set() for i in range(MAX_TEACHER)}  # giáo viên -> slot bận

    for cls_id, (t_cls, g_cls, s_cls) in enumerate(classes):
        selected = None
        if cls_id in parent1 and cls_id in parent2:
            selected = random.choice([parent1[cls_id], parent2[cls_id]])
        elif cls_id in parent1:
            selected = parent1[cls_id]
        elif cls_id in parent2:
            selected = parent2[cls_id]

        if selected:
            slots = [s for (s, _) in selected]
            rooms = [r for (_, r) in selected]

            # Kiểm tra: số lượng slot đúng, slot liền nhau, phòng đủ chỗ, không trùng giáo viên, không trùng phòng
            if len(slots) != t_cls:
                continue
            if max(slots) - min(slots) + 1 != t_cls:
                continue
            if any(r >= len(room_caps) or room_caps[r] < s_cls for r in rooms):
                continue
            if any(s in teacher_busy[g_cls] for s in slots):
                continue
            if any(r in used_slots[s] for s, r in selected):
                continue

            # Nếu hợp lệ thì thêm vào child
            child[cls_id] = selected
            for s, r in selected:
                used_slots[s].add(r)
                teacher_busy[g_cls].add(s)
    return child

def mutate(individual, classes, room_caps, mutation_rate=1, max_attempts=200):
    """
    individual: dict[class_id] = [(slot, room)]
    classes: list of (t, g, s)
    room_caps: list of capacity of rooms
    """
    mutated = individual.copy()
    used_slots = {i: set() for i in range(5 * SLOTS_PER_DAY)}
    teacher_busy = {i: set() for i in range(MAX_TEACHER)}

    # Cập nhật các slot/phòng/gv đã sử dụng
    for cls, alloc in mutated.items():
        t_cls, g_cls, _ = classes[cls]
        for s, r in alloc:
            used_slots[s].add(r)
            teacher_busy[g_cls].add(s)

    for cls in list(mutated.keys()):
        if random.random() < mutation_rate:
            t_cls, g_cls, s_cls = classes[cls]
            success = False

            # Gỡ lịch cũ
            for s, r in mutated[cls]:
                used_slots[s].remove(r)
                teacher_busy[g_cls].remove(s)
            del mutated[cls]

            # Thử gán lại lịch mới
            for _ in range(max_attempts):
                day = random.randint(0, 4)
                start_in_day = random.randint(0, 12 - t_cls)
                start_slot = day * 12 + start_in_day
                slot_range = list(range(start_slot, start_slot + t_cls))

                room_candidates = [r for r in range(len(room_caps)) if room_caps[r] >= s_cls]
                random.shuffle(room_candidates)

                for r in room_candidates:
                    if all(r not in used_slots[s] for s in slot_range) and \
                       all(s not in teacher_busy[g_cls] for s in slot_range):

                        mutated[cls] = [(s, r) for s in slot_range]
                        for s in slot_range:
                            used_slots[s].add(r)
                            teacher_busy[g_cls].add(s)
                        success = True
                        break
                if success:
                    break

            # Nếu không thành công thì bỏ lớp này khỏi lịch

    return mutated

def genetic_algorithm(classes, room_caps, population_size=50, generations=5):
    population = [generate_individual() for _ in range(population_size)]
    best = max(population, key=lambda ind: fitness(ind, len(classes)))

    for gen in range(generations):
        new_population = []

        # Selection (elitism)
        population.sort(key=lambda ind: fitness(ind, len(classes)), reverse=True)
        elite = population[:population_size // 5]  # top 20%
        new_population.extend(elite)

        # Crossover + Mutation
        while len(new_population) < population_size:
            p1, p2 = random.sample(elite, 2)
            child = crossover(p1, p2, classes, room_caps)
            child = mutate(child, classes, room_caps)
            new_population.append(child)

        population = new_population
        current_best = max(population, key=lambda ind: fitness(ind, len(classes)))
        if fitness(current_best, len(classes)) > fitness(best, len(classes)):
            best = current_best
    return best

def print_schedule(best_schedule):
    result = []
    for cls_id in sorted(best_schedule.keys()):
        slot_room_list = best_schedule[cls_id]
        if not slot_room_list:
            continue
        start_slot, room = min(slot_room_list)  # lấy slot đầu tiên
        result.append((cls_id + 1, start_slot + 1, room + 1))  # chuyển về 1-based
    return len(result)

SLOTS_PER_DAY = 12  # số tiết trong một ngày
MAX_TEACHER = 100

with open("huge_test.txt", 'w') as f:
    for input_file in os.listdir(os.path.join("test chung", "huge")):
        start = time.time()
        N, M, t, g, s, c = file_input(os.path.join('test chung', "huge", input_file))
        classes = list(zip(t, g, s))

        best_schedule = genetic_algorithm(classes, c)
        end = time.time()
        res = print_schedule(best_schedule)
        f.write(f"File {input_file} ; Result : {res} ; Runtime : {end - start}\n")
