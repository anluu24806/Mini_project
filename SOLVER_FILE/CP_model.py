from ortools.sat.python import cp_model

def solve_scheduling_cp(classes_data, room_capacities):
    model = cp_model.CpModel()
    num_classes = len(classes_data)
    num_rooms = len(room_capacities)
    num_slots = 60  # 5 days * 12 time slots/day

    is_assigned = [model.NewBoolVar(f'assigned_{i}') for i in range(num_classes)]
    room_var = [model.NewIntVar(-1, num_rooms - 1, f'room_{i}') for i in range(num_classes)]
    start_slot_var = [model.NewIntVar(-1, num_slots - 1, f'start_slot_{i}') for i in range(num_classes)]

    # Constraint: If a class is assigned, room and slot must be valid
    for i in range(num_classes):
        t_i = classes_data[i]['t']
        model.Add(room_var[i] >= 0).OnlyEnforceIf(is_assigned[i])
        model.Add(start_slot_var[i] >= 0).OnlyEnforceIf(is_assigned[i])
        model.Add(start_slot_var[i] <= num_slots - t_i).OnlyEnforceIf(is_assigned[i])

        model.Add(room_var[i] == -1).OnlyEnforceIf(is_assigned[i].Not())
        model.Add(start_slot_var[i] == -1).OnlyEnforceIf(is_assigned[i].Not())

    # Constraint: Number of students does not exceed room capacity
    for i in range(num_classes):
        s_i = classes_data[i]['s']
        for r in range(num_rooms):
            assigned_in_room = model.NewBoolVar(f'class_{i}_in_room_{r}')
            model.Add(room_var[i] == r).OnlyEnforceIf(assigned_in_room)
            model.Add(room_var[i] != r).OnlyEnforceIf(assigned_in_room.Not())
            model.AddImplication(assigned_in_room, is_assigned[i])
            model.Add(s_i <= room_capacities[r]).OnlyEnforceIf(assigned_in_room)

    # Constraint: A teacher cannot teach two classes at the same time
    for i in range(num_classes):
        for j in range(i + 1, num_classes):
            if classes_data[i]['g'] == classes_data[j]['g']:
                t_i = classes_data[i]['t']
                t_j = classes_data[j]['t']
                si = start_slot_var[i]
                sj = start_slot_var[j]

                cond1 = model.NewBoolVar(f'class_{i}_before_{j}')
                cond2 = model.NewBoolVar(f'class_{j}_before_{i}')
                model.Add(si + t_i <= sj).OnlyEnforceIf(cond1)
                model.Add(si + t_i > sj).OnlyEnforceIf(cond1.Not())
                model.Add(sj + t_j <= si).OnlyEnforceIf(cond2)
                model.Add(sj + t_j > si).OnlyEnforceIf(cond2.Not())

                model.AddBoolOr([
                    is_assigned[i].Not(),
                    is_assigned[j].Not(),
                    cond1,
                    cond2
                ])

    # Constraint: Each room cannot contain multiple classes at the same time
    for r in range(num_rooms):
        intervals = []
        for i in range(num_classes):
            t_i = classes_data[i]['t']
            start = start_slot_var[i]
            end = model.NewIntVar(0, num_slots, f'end_{i}_{r}')
            model.Add(end == start + t_i)

            assigned_in_room = model.NewBoolVar(f'class_{i}_in_room_{r}')
            model.Add(room_var[i] == r).OnlyEnforceIf(assigned_in_room)
            model.Add(room_var[i] != r).OnlyEnforceIf(assigned_in_room.Not())
            model.AddImplication(assigned_in_room, is_assigned[i])

            interval = model.NewOptionalIntervalVar(start, t_i, end, assigned_in_room, f'interval_{i}_{r}')
            intervals.append(interval)

        model.AddNoOverlap(intervals)

    # Objective: Maximize the number of scheduled classes
    model.Maximize(sum(is_assigned))

    solver = cp_model.CpSolver()

    # Limit the solver runtime (e.g., 150 seconds)
    solver.parameters.max_time_in_seconds = 10000000000000000000000000

    status = solver.Solve(model)

    scheduled_classes = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(int(solver.ObjectiveValue()))
        for i in range(num_classes):
            if solver.Value(is_assigned[i]):
                class_id = classes_data[i]['id']
                room = solver.Value(room_var[i]) + 1
                slot = solver.Value(start_slot_var[i]) + 1
                scheduled_classes.append((class_id, slot, room))
    else:
        print(0)

    return scheduled_classes


if __name__ == '__main__':
    n, m = map(int, input().split())
    classes_data = []
    for i in range(n):
        t, g, s = map(int, input().split())
        classes_data.append({'id': i + 1, 't': t, 'g': g, 's': s})
    room_capacities = list(map(int, input().split()))

    scheduled_result = solve_scheduling_cp(classes_data, room_capacities)

    for class_id, slot, room_id in sorted(scheduled_result):
        print(class_id, slot, room_id)
