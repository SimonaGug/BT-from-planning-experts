import sys
sys.path.insert(0,'/content/WASP-CBSS-BT')
import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')
from pathlib import Path
import csv
from BTFactor.BT import bt_factor
from REBTEspresso.BT import re_bt_espresso
from REBTEspresso.alpha import alphas
from REBTEspresso.possible_to_improve import possible_to_improve


original_bt = ['s(',
                  'f(','s(', 'at station CHARGE1?', 'charge!',')',
                  'battery level > 10?', 'at station CHARGE1?', 's(', 'move to CHARGE1!', 'charge!',')',')',
              
                  'f(', 'carried weight <= 6?', 's(', 'move to DELIVERY!','place!',')',')',
              
                  'f(','s(', 'at station CONVEYOR_HEAVY?', 'pick!',')',
                  'conveyor light <= 0?', 's(','move to CONVEYOR_LIGHT!','pick!',')',')',
              
                  'f(', 's(', 'conveyor heavy <= 1?', 'idle!',')',  's(','move to CONVEYOR_HEAVY!','pick!',')',
              ')']

ticks = 200
with open("results/performance-correctness_test.csv", "w", encoding='UTF8', newline='') as csvFile:

    header = ["seed","fitness original","fitness BT-Factor", "fitness RE-BT", "RE:BT-Possible to minimize?", "Original battery over?" , "BT-Factor battery over?", "RE:BT battery over?", "RE:BT (no pruning) battery over?"]
    performance = csv.writer(csvFile)
    performance.writerow(header)

    for j in range(101,301):      
        environment = notebook_interface.Environment(seed=j, verbose=False)
        fitness_original_bt, delivered_heavy_original_bt, delivered_light_original_bt, battery_original = environment.get_fitness(original_bt, max_ticks=ticks, show_world=True, seed=environment.seed) 
        fitness_bt_factor, delivered_heavy_bt_factor, delivered_light_bt_factor, battery_bt_factor = environment.get_fitness(bt_factor, max_ticks=ticks, show_world=True, seed=environment.seed) 
        i=0
        re_bt = re_bt_espresso[0]
        fitness_re_bt, delivered_heavy_re_bt, delivered_light_re_bt, battery_re_bt = environment.get_fitness(re_bt, max_ticks=ticks, show_world=True, seed=environment.seed) 
        previous_fitness_re_bt = fitness_re_bt  
        battery_re_bt_0_pruning = battery_re_bt
        while (previous_fitness_re_bt <= fitness_re_bt):
            i+=1
            re_bt = re_bt_espresso[i]
            environment = notebook_interface.Environment(seed=j, verbose=False)
            previous_fitness_re_bt = fitness_re_bt
            previous_delivered_heavy_re_bt = delivered_heavy_re_bt
            previous_delivered_light_re_bt = delivered_light_re_bt 
            previous_battery_re_bt = battery_re_bt
            fitness_re_bt, delivered_heavy_re_bt, delivered_light_re_bt, battery_re_bt = environment.get_fitness(re_bt, max_ticks=ticks, show_world=True, seed=environment.seed)   
        print(j,fitness_original_bt, fitness_bt_factor, previous_fitness_re_bt, possible_to_improve[i-1], battery_original, battery_bt_factor, previous_battery_re_bt, battery_re_bt_0_pruning) 
        performance.writerow([j,fitness_original_bt, fitness_bt_factor, previous_fitness_re_bt, possible_to_improve[i-1], battery_original, battery_bt_factor, previous_battery_re_bt, battery_re_bt_0_pruning])





