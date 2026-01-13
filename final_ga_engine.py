import pandas as pd
import random
import copy

# 1. LOAD DATA
df = pd.read_csv('standardized_university_data.csv')
class_requirements = df.to_dict('records')

rooms = df['Room'].unique().tolist()
teachers = df['Teacher'].unique().tolist()
sections = df['Section'].unique().tolist()

# Expanded Time Slots (Adding more slots to handle the 1519 classes)
days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
times = ['08:00-11:00', '11:15-02:15', '02:30-05:30', '05:45-08:45']
all_slots = [f"{d}@{t}" for d in days for t in times]

def calculate_fitness(schedule):
    score = 10000 # Starting points
    room_busy = {}
    teacher_busy = {}
    section_busy = {}

    for item in schedule:
        slot = item['assigned_slot']
        
        # Rule 1: Room Double-Booking (Penalty reduced to 20 to allow learning)
        r_key = (item['Room'], slot)
        if r_key in room_busy: score -= 20
        room_busy[r_key] = True
        
        # Rule 2: Teacher in two places
        t_key = (item['Teacher'], slot)
        if t_key in teacher_busy: score -= 20
        teacher_busy[t_key] = True
        
        # Rule 3: Students (Section) having two classes at once
        s_key = (item['Section'], slot)
        if s_key in section_busy: score -= 20
        section_busy[s_key] = True
        
    return score

# 2. RUN GA
print(f"🚀 AI Scaling: 1519 requirements vs {len(rooms)} rooms...")

# Create initial population
population = []
for _ in range(15):
    version = []
    for req in class_requirements:
        new_gene = copy.deepcopy(req)
        new_gene['assigned_slot'] = random.choice(all_slots)
        version.append(new_gene)
    population.append(version)

# Evolution Loop
for gen in range(101):
    population.sort(key=calculate_fitness, reverse=True)
    best_score = calculate_fitness(population[0])
    
    if gen % 10 == 0:
        print(f"Gen {gen} | Optimization Score: {best_score}")

    # Survival: Keep top 3
    next_gen = population[:3]
    while len(next_gen) < 15:
        parent = copy.deepcopy(random.choice(population[:5]))
        # Mutation: Fix 5% of classes
        for _ in range(int(len(parent)*0.05)):
            idx = random.randint(0, len(parent)-1)
            parent[idx]['assigned_slot'] = random.choice(all_slots)
        next_gen.append(parent)
    population = next_gen

# 3. EXPORT WITH THE FIX
best_schedule = pd.DataFrame(population[0])

# SAFE SPLIT FIX:
# This ensures we always get exactly 2 columns, avoiding the ValueError
split_data = best_schedule['assigned_slot'].str.split('@', n=1, expand=True)
best_schedule['Final_Day'] = split_data[0]
best_schedule['Final_Time'] = split_data[1]

print("📊 Creating Matrix...")
try:
    final_grid = best_schedule.pivot_table(
        index=['Final_Day', 'Final_Time'], 
        columns='Room', 
        values='Course', 
        aggfunc=lambda x: " / ".join(str(v) for v in x)
    )
    
    with pd.ExcelWriter("University_Master_Timetable_2025.xlsx", engine='xlsxwriter') as writer:
        best_schedule.to_excel(writer, sheet_name="Full_List", index=False)
        final_grid.to_excel(writer, sheet_name="Room_Timetable_Grid")
    print("\n✅ SUCCESS! File created: University_Master_Timetable_2025.xlsx")
except Exception as e:
    print(f"❌ Error creating Grid: {e}")
    best_schedule.to_excel("University_Master_List_Only.xlsx")