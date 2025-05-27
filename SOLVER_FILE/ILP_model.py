from ortools.linear_solver import pywraplp

def solve_timetable_ilp(N,M,data,c):
    solver = pywraplp.Solver.CreateSolver('SCIP')
        # Phân tích dữ liệu
        
    t = [0] * (N + 1) # t[i]: số tiết của lớp i (dùng 1-indexed)
    g = [0] * (N + 1) # g[i]: giáo viên của lớp i
    s = [0] * (N + 1) # s[i]: số sinh viên của lớp i
        
    for i in range(1, N + 1):
        ti, gi, si = data[i-1]
        t[i] = ti
        g[i] = gi
        s[i] = si
        
    T = 60 # Tổng số tiết trong tuần (5 ngày * 12 tiết/ngày)
    
    # --- 2. Biến Quyết định ---
    # z[(i,u,v)]: Biến nhị phân, 1 nếu lớp i bắt đầu từ tiết u và phòng v
    z = {}
    for i in range(1, N + 1):
        # Lớp i có thể bắt đầu từ tiết u (1-indexed)
        # và phải đảm bảo đủ t[i] tiết liên tiếp trong tổng số T tiết.
        for u in range(1, T - t[i] + 2): 
            # Phòng v (1-indexed)
            for v in range(1, M + 1):
                # Chỉ tạo biến z nếu phòng đủ chỗ cho số sinh viên của lớp
                if s[i] <= c[v]:
                    z[(i,u,v)] = solver.BoolVar(f'z_{i}_{u}_{v}')
    
    # y[i]: Biến nhị phân, 1 nếu lớp i được xếp đầy đủ tiết
    y = {}
    for i in range(1, N + 1):
        y[i] = solver.BoolVar(f'y_{i}')
    
    # --- 3. Hàm Mục Tiêu ---
    # Tối đa hóa số lớp được xếp thời khóa biểu
    objective = solver.Objective()
    for i in range(1, N + 1):
        objective.SetCoefficient(y[i], 1)
    objective.SetMaximization()
    
    # --- 4. Các Ràng buộc (Constraints) ---


    #### Ràng buộc 1: Liên kết Biến z và y (Mỗi lớp được xếp tối đa một lần)
    # Logic: Nếu y[i] = 1 (lớp i được xếp), thì tổng của tất cả z[(i,u,v)] phải là 1 (chỉ một điểm bắt đầu duy nhất).
    # Nếu y[i] = 0 (lớp i không được xếp), thì tổng của tất cả z[(i,u,v)] phải là 0 (không có điểm bắt đầu nào).
    for i in range(1, N + 1):
        sum_z_for_i = 0
        for u in range(1, T - t[i] + 2):
            for v in range(1, M + 1):
                if (i,u,v) in z: # Chỉ cộng biến z đã được tạo
                    sum_z_for_i += z[(i,u,v)]
        solver.Add(sum_z_for_i == y[i], name=f'C1_ClassSchedule_{i}')
    
    #### Ràng buộc 2: Không Trùng Giáo viên
    # Logic: Một giáo viên chỉ có thể dạy tối đa 1 lớp tại bất kỳ thời điểm nào.
    # Duyệt qua từng tiết trong tuần
    for current_u in range(1, T + 1): 
        # Lấy danh sách các ID giáo viên duy nhất để tránh lặp
        unique_teacher_ids = set(g[i] for i in range(1, N + 1))
        for teacher_id in unique_teacher_ids:
            teacher_conflict_expr = 0
            # Duyệt qua tất cả các lớp
            for i in range(1, N + 1):
                if g[i] == teacher_id: # Nếu lớp i thuộc về giáo viên này
                    # Tìm tất cả các điểm bắt đầu (start_u) mà lớp i có thể bắt đầu
                    # để nó bao phủ tiết current_u này.
                    # start_u phải nằm trong khoảng [current_u - t[i] + 1, current_u]
                    # và phải là một điểm bắt đầu hợp lệ (u + t[i] - 1 <= T).
                    for start_u in range(max(1, current_u - t[i] + 1), min(current_u + 1, T - t[i] + 2)):
                        # Duyệt qua tất cả các phòng
                        for v in range(1, M + 1):
                            if (i, start_u, v) in z: # Chỉ cộng biến z đã được tạo
                                teacher_conflict_expr += z[(i, start_u, v)]
            # Ràng buộc: Tổng các z của giáo viên này tại tiết current_u không quá 1
            solver.Add(teacher_conflict_expr <= 1, name=f'C2_TeacherConflict_GV{teacher_id}_T{current_u}')
            
    #### Ràng buộc 3: Mỗi Phòng Mỗi Tiết Chỉ Có Một Lớp
    # Logic: Mỗi phòng học chỉ có thể được sử dụng bởi tối đa một lớp tại bất kỳ thời điểm nào.
    # Duyệt qua từng tiết trong tuần
    for current_u in range(1, T + 1):
        # Duyệt qua từng phòng
        for v_room in range(1, M + 1):
            room_conflict_expr = 0
            # Duyệt qua tất cả các lớp
            for i in range(1, N + 1):
                # Tìm tất cả các điểm bắt đầu (start_u) mà lớp i có thể bắt đầu
                # để nó bao phủ tiết current_u này tại phòng v_room.
                for start_u in range(max(1, current_u - t[i] + 1), min(current_u + 1, T - t[i] + 2)):
                    if (i, start_u, v_room) in z: # Chỉ cộng biến z đã được tạo
                        room_conflict_expr += z[(i, start_u, v_room)]
            # Ràng buộc: Tổng các z chiếm phòng v_room tại tiết current_u không quá 1
            solver.Add(room_conflict_expr <= 1, name=f'C3_RoomConflict_P{v_room}_T{current_u}')
    
    solver.SetTimeLimit(20000)
    # --- 5. Giải bài toán ---
    status = solver.Solve()
    
    # --- 6. In Kết quả ---
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        # Số lớp được xếp lịch theo hàm mục tiêu
        Q_scheduled_classes = int(solver.Objective().Value())
        print(f"{Q_scheduled_classes}")
        
    else:
        print("No solution")  

if __name__ == '__main__':
    N,M = map(int, input().split())
    data = [list(map(int, input().split())) for _ in range(N)]
    c =[0]+ list(map(int, input().split()))
    solve_timetable_ilp(N,M,data,c)