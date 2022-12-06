import sys
sys.path.insert(0,'/content/WASP-CBSS-BT')
import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')
import fileinput

original_bt =['s(',
                  'f(','s(', 'at station CHARGE1?', 'charge!',')',
                  'battery level > 10?', 'at station CHARGE1?', 's(', 'move to CHARGE1!', 'charge!',')',')',
              
                  'f(', 'carried weight <= 6?', 's(', 'move to DELIVERY!','place!',')',')',
              
                  'f(','s(', 'at station CONVEYOR_HEAVY?', 'pick!',')',
                  'conveyor light <= 0?', 's(','move to CONVEYOR_LIGHT!','pick!',')',')',
              
                  'f(', 's(', 'conveyor heavy <= 1?', 'idle!',')',  's(','move to CONVEYOR_HEAVY!','pick!',')',
              ')']

number_traces =100
ticks = 200
executed_traces_filename = "ExecutedTraces_test.csv"  

def get_station_from_position(x=0, y=0):
    """
    Returns pose of given station
    """
    if x == 23 and y == 12:
        return "CHARGE1"
    if x == 12 and y == 12:
        return "CONVEYOR_HEAVY"
    if x == 12 and y == 3:
        return "CONVEYOR_LIGHT"
    if x == 21 and y == 7.5:
        return "DELIVERY"
    return "OTHER"

executed_traces_file= open(executed_traces_filename,"w")
executed_traces_file.write("at station,battery level,carried weight,carried light,carried heavy,conveyor light,conveyor heavy,Decision\n") 
executed_traces_file.close()

for i in range (300, 302):
    environment = notebook_interface.Environment(seed=i, verbose=False)
    result = environment.get_fitness(original_bt, max_ticks=ticks, show_world=True, seed=environment.seed)
    #print("Fitness:", result)
    #print(i)
    input_file = "executed_traces/robots_" + str(i) +".txt"
    executed_traces_file= open(executed_traces_filename,"a")
    new_line=""
    for line in fileinput.input(input_file ):
        if 'WorldState(' in line:
            variables = line.split(",")
            x=float(variables[1].split("=")[2])
            y=float(variables[2].split("=")[1].replace(")", ""))
            current_state = get_station_from_position(x,y) + "," + variables[3].replace('battery_level=', '') + variables[4].replace(' carried_weight=', ',') + variables[5].replace(' carried_light=', ',') + variables[6].replace(' carried_heavy=', ',') + variables[7].replace(' cnv_n_light=', ',') + variables[8].replace(' cnv_n_heavy=', ',')
        if '!'in line:
            current_act = line.replace('\n', '') 
            executed_traces_file.write(current_state + "," + current_act + "\n")
            new_line=""
    fileinput.close()
    executed_traces_file.close()