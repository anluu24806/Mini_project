from collections import Counter

def compute_class_priority(class_data, room_capacities):
    teacher_load = Counter(g_i for _, g_i, _ in class_data)
    priority_list = []

    for i, (t_i, g_i, s_i) in enumerate(class_data, start=1):
        num_compatible_rooms = sum(1 for c in room_capacities if c >= s_i)
        if num_compatible_rooms == 0:
            continue
        teacher_busy_score = teacher_load[g_i]
        priority_list.append((num_compatible_rooms, teacher_busy_score, t_i, i, t_i, g_i, s_i))

    priority_list.sort()
    return [(i, t_i, g_i, s_i) for _, _, _, i, t_i, g_i, s_i in priority_list]

#ban dung cho so to
def greedy_solution(class_data, room_capacities, N, M):
    priotity_list = compute_class_priority(class_data, room_capacities)
    room_capacities.sort()

    teacher_busy = {g: set() for g in range(1, max(class_data, key=lambda x: x[1])[1] + 1)}
    room_busy = {r_id: set() for r_id in range(1, M + 1)}
    class_schedule = []

    wait_list = priotity_list[:]
    scheduled_class = set()

    # Phase 1
    while wait_list:
        new_wait_list = []
        any_scheduled = False

        for i, t_i, g_i, s_i in wait_list:
            if i in scheduled_class:
                continue

            sorted_rooms = sorted(
                [(r_id, len(room_busy[r_id])) for r_id in range(1, M + 1) if room_capacities[r_id - 1] >= s_i],
                key=lambda x: x[1]
            )

            scheduled = False
            for r_id, _ in sorted_rooms:
                busy_slots = room_busy[r_id]
                last_slots = max(busy_slots) + 1 if busy_slots else 1

                for start in range(last_slots, 62 - t_i):
                    slots = set(range(start, start + t_i))
                    if not (slots & teacher_busy[g_i]):
                        room_busy[r_id].update(slots)
                        teacher_busy[g_i].update(slots)
                        class_schedule.append((i, start, r_id))
                        scheduled_class.add(i)
                        scheduled = True
                        any_scheduled = True
                        break
                if scheduled:
                    break

            if not scheduled:
                new_wait_list.append((i, t_i, g_i, s_i))

        if not any_scheduled:
            break
        wait_list = new_wait_list

    # Phase 2
    remaining_classes = [c for c in wait_list if c[0] not in scheduled_class]
    remaining_classes += [c for c in priotity_list if c[0] not in scheduled_class]

    remaining_classes.sort(key=lambda x: (
        sum(1 for c in room_capacities if c >= x[3]),  # s_i
        len(teacher_busy[x[2]])                        # g_i
    ))

    for i, t_i, g_i, s_i in remaining_classes:
        if i in scheduled_class:
            continue
        for r_id in range(1, M + 1):
            if room_capacities[r_id - 1] < s_i:
                continue
            for start in range(1, 61 - t_i + 1):
                slots = set(range(start, start + t_i))
                if not (slots & room_busy[r_id] or slots & teacher_busy[g_i]):
                    room_busy[r_id].update(slots)
                    teacher_busy[g_i].update(slots)
                    class_schedule.append((i, start, r_id))
                    scheduled_class.add(i)
                    break
            else:
                continue
            break

    # Loại bỏ lớp bị trùng (nếu có)
    unique_class_schedule = {}
    for i, start, r_id in class_schedule:
        if i not in unique_class_schedule:
            unique_class_schedule[i] = (i, start, r_id)

    final_schedule = list(unique_class_schedule.values())
    final_schedule.sort()

    print(len(final_schedule))
    for cls in final_schedule:
        print(*cls)

#banr dung cho so nho
def Greedy_solution(class_data, room_capacities, N, M):
    priority_list = compute_class_priority(class_data, room_capacities)
    room_capacities.sort()
    
    #tạo các biến cần thiết
    teacher_busy = {g:set() for g in range(1, max(class_data, key = lambda x: x[1])[1]+1)}
    room_busy = {g:set() for g in range(1, M+1)}
    class_schecule = []

    #sắp xếp thời khóa biểu
    for i, t_i, g_i, s_i in priority_list:
        #duyệt các phòng phù hợp
        for room_index, c in enumerate(room_capacities, start = 1):
            if c<s_i:
                continue
            for start in range(1, 62-t_i):
                slots = set(range(start, start+t_i))
                if slots & teacher_busy[g_i]:
                    continue
                if slots & room_busy[room_index]:
                    continue

                class_schecule.append((i, start, room_index))
                teacher_busy[g_i].update(slots)
                room_busy[room_index].update(slots)
                break
            else:
                continue
            break
    print(len(class_schecule))
    class_schecule.sort()
    for cls in class_schecule:
        print(*cls)    

if __name__ == "__main__":
    N, M = map(int, input().split())
    class_data = [list(map(int, input().split())) for _ in range(N)]
    room_capacities = list(map(int, input().split()))
    if N>300:
        greedy_solution(class_data, room_capacities, N, M)
    else:
        Greedy_solution(class_data, room_capacities, N, M)