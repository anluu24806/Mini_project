# TimeTable assign slot and room to classes Large
This is a mini-project for topic 9 in Fundamentals of Optimization course of SoICT - HUST

# Our Team

| Name               | Student ID | Mail                                                                       |
|--------------------|------------|----------------------------------------------------------------------------|
| Luu Hieu An        | 202400093  | [an.lh2400093@sis.hust.edu.vn](mailto:an.lh2400093@sis.hust.edu.vn)       |
| Nguyen Danh Bao    | 202400094  | [bao.nd2400094@sis.hust.edu.vn](mailto:bao.nd2400094@sis.hust.edu.vn)     |
| Nguyen Bao Phong   | 202416731  | [phong.nb2416731@sis.hust.edu.vn](mailto:phong.nb2416731@sis.hust.edu.vn) |
| Nguyen Tran Trung  | 202400117  | [trung.nt2400117@sis.hust.edu.vn](mailto:trung.nt2400117@sis.hust.edu.vn) |

You can find a comprehensive explanation of our problem modeling, data generation techniques, results, and further details in "our full report."

# Problem

There are N classes labeled 1, 2, ..., N that need to be scheduled.

### Each class i has:
+ t(i): the number of sessions (time slots) it requires  
+ g(i): the teacher assigned to teach the class  
+ s(i): the number of students in the class  

There are M classrooms labeled 1, 2, ..., M, where:  
c(i): the seating capacity of room i.

The week consists of 5 days (from Monday to Friday), each day has 12 periods (6 in the morning and 6 in the afternoon),
making a total of 60 time slots numbered from 1 to 60.

### The goal is to schedule the classes (assigning a day, time slot, and room for each class), satisfying the following constraints:
+ Classes taught by the same teacher must not overlap in time  
+ The number of students in a class must not exceed the capacity of the assigned classroom  
+ The number of scheduled classes should be maximized
# Analysis

![ABC](https://github.com/anluu24806/Mini_project/blob/main/Pictures/Screenshot%202025-06-01%20224806.png)

##### + In cases with a small number of rooms (M), the heuristic algorithm often yields a smaller number of scheduled classes (f) compared to CP and ILP methods.
##### + This suggests that the heuristic method may be less effective in highly constrained scenarios.
##### + Despite this, the heuristic algorithm demonstrates consistently faster computation times than CP and ILP.
##### + Therefore, while exact methods (CP, ILP) produce better solutions in tight constraints, heuristics are more suitable when speed is prioritized.

![ABC](https://github.com/anluu24806/Mini_project/blob/main/Pictures/Screenshot%202025-06-01%20224806.png)
🔎 Observations from Large-Scale Test Cases
From experiments involving a large number of classes (N) and limited room resources (M), the following insights were observed:

### ⚡ Greedy Heuristic

✅ Very fast execution — typically within milliseconds.

❌ Misses many feasible assignments when resource constraints are tight.

📉 For instance, in input1.txt, it scheduled only 87/102 classes, compared to 92 from exact methods.

### 🧮 ILP (Integer Linear Programming)

✅ Produces high-quality solutions when sufficient time is available.

🕒 Very slow on larger or more constrained inputs — frequently hits time limits (e.g., input5.txt, input7.txt).

⚖️ Strong in quality but poor time efficiency on large instances.

### 🧩 CP (Constraint Programming)

✅ Offers a balanced trade-off between runtime and solution quality.

🥇 Consistently reaches optimal or near-optimal solutions within a reasonable time.

📈 Ideal for scenarios where both accuracy and efficiency are required.


# Folder structure
    ├── analyze                 # contains some analysis information
    │   └── ...
    ├── CP_model.pdf            # how we model the problem
    ├── ILP_model.pdf
    ├── Heuristic.pdf
    ├── GA_model.pdf
    ├── assets
    ├── figure                  # contains generated figures
    │   ├── generated_CP
    │   │   └── ...
    │   ├── generated_HEU
    │   │   └── ...
    │   └── gen_figure.py       # figure generator
    ├── input_data              # contains generated data
    │   └── ...
    ├── presentation
    ├── results                 # contains results from solver
    │   └── ...
    ├── script                  # script file for collect result and gen figure
    │   └── ...
    └── solver_file             # contains solver files
        ├── CP_model_solver
        │   └── ...
        ├── Heuristic
        │   └── ...
        └── ILP_model.py
# Visualizer 
![ABC](https://github.com/anluu24806/Mini_project/blob/main/Pictures/Screenshot%202025-05-26%20235245.png)
