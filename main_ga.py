import pandas as pd
import random

# 1. Load the CLEANED data (loads instantly!)
df = pd.read_csv('ga_ready_data.csv')

rooms = df['Room'].unique().tolist()
labs = df[df['Is_Lab'] == True]['Room'].unique().tolist()
# We'll take the most recent 50 courses for the new schedule
courses = df['Course'].unique().tolist()[:50]

# Standard university slots
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
times = ['08:30-11:30', '11:45-02:45', '03:15-06:15']
slots = [f"{d} {t}" for d in days for t in times]

class SchedulerGA:
    def __init__(self, pop_size=50):
        # Create a population of random schedules
        self.population = []
        for _ in range(pop_size):
            sched = [{'course': c, 'room': random.choice(rooms), 'slot': random.choice(slots)} for c in courses]
            self.population.append(sched)

    def fitness(self, schedule):
        score = 1000
        used_spots = set()
        for gene in schedule:
            # Rule 1: No two classes in same room/time
            if (gene['room'], gene['slot']) in used_spots:
                score -= 200
            used_spots.add((gene['room'], gene['slot']))
            
            # Rule 2: Labs MUST go to Lab Rooms
            if 'lab' in gene['course'].lower() and gene['room'] not in labs:
                score -= 100
        return score

    def start_evolution(self):
        print(f"🚀 Starting AI Scheduling for {len(courses)} classes...")
        for gen in range(30):
            # Sort by best fitness
            self.population.sort(key=self.fitness, reverse=True)
            print(f"Generation {gen} | Best Score: {self.fitness(self.population[0])}")
            
            if self.fitness(self.population[0]) >= 1000:
                print("✨ Perfect Schedule Found!")
                break
        
        # Display the best one
        print("\n--- BEST SCHEDULE FOUND ---")
        best = pd.DataFrame(self.population[0])
        print(best.head(10))

if __name__ == "__main__":
    ga = SchedulerGA()
    ga.start_evolution()