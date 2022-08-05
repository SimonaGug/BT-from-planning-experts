#Setup paths and imports
import sys
sys.path.insert(0,'/content/WASP-CBSS-BT')
from IPython.display import Image
import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from pathlib import Path
import os
import csv

individuals =[ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 'carried weight > 7.0','conveyor light > 0.5','conveyor heavy  <=  1.5',')','move to CHARGE1!', ')', 
 's(', 'carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1',')',')','idle!', ')', 
 's(', 'conveyor heavy > 1.5','carried weight  <=  7.0','conveyor light  <=  0.5','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'not at station CHARGE1','not at station CONVEYOR_HEAVY',')',')','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','battery level > 10.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'conveyor light > 0.5','carried weight  <=  7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station CONVEYOR_LIGHT',')',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station DELIVERY',')',')','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 'carried weight > 7.0','conveyor light > 0.5','conveyor heavy  <=  1.5',')','move to CHARGE1!', ')', 
 's(', 'carried weight  <=  7.0','conveyor light  <=  0.5','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','conveyor heavy  <=  1.5',')',')','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','battery level > 10.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'conveyor light > 0.5','carried weight  <=  7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station CONVEYOR_LIGHT',')',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station DELIVERY',')',')','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 'carried weight > 7.0','conveyor light > 0.5','conveyor heavy  <=  1.5',')','move to CHARGE1!', ')', 
 's(', 'battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','battery level > 10.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'carried weight  <=  7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','not at station CONVEYOR_LIGHT',')',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station DELIVERY',')',')','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 's(', 'carried weight > 7.0','not at station DELIVERY',')','s(', 'conveyor light > 0.5','carried weight  <=  7.0',')','s(', 'carried weight  <=  7.0','conveyor heavy  <=  1.5',')',')','move to CHARGE1!', ')', 
 's(', 'battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','battery level > 10.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'carried weight  <=  7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','not at station CONVEYOR_LIGHT',')',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station DELIVERY',')',')','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 's(', 'carried weight > 7.0','not at station DELIVERY',')','s(', 'conveyor light > 0.5','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')','s(', 'carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5',')',')','move to CHARGE1!', ')', 
 's(', 'battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'carried weight  <=  7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','not at station CONVEYOR_LIGHT',')',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','f(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'battery level > 10.5','not at station CHARGE1','not at station DELIVERY',')',')','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 's(', 'carried weight > 7.0','not at station DELIVERY',')','s(', 'conveyor light > 0.5','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')','s(', 'carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5',')',')','move to CHARGE1!', ')', 
 's(', 'battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 's(', 'carried weight > 7.0','not at station DELIVERY',')','s(', 'conveyor light > 0.5','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')',')','move to CHARGE1!', ')', 
 's(', 's(', 'at station CHARGE1','battery level > 99.5',')','s(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','battery level  <=  99.5','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'not at station CHARGE1','battery level  <=  10.5','f(', 's(', 'carried weight > 7.0','not at station DELIVERY',')','s(', 'conveyor light > 0.5','carried weight  <=  7.0','not at station CONVEYOR_LIGHT',')',')','move to CHARGE1!', ')', 
 's(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','battery level > 10.5','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','battery level  <=  10.5','move to CHARGE1!', ')', 
 's(', 'conveyor light > 0.5','battery level > 10.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','not at station CONVEYOR_HEAVY','move to CONVEYOR_HEAVY!', ')', 
 's(', 'not at station CHARGE1','carried weight  <=  7.0','f(', 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT',')','s(', 'conveyor heavy > 1.5','at station CONVEYOR_HEAVY','conveyor light  <=  0.5',')',')','pick!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','move to CONVEYOR_LIGHT!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','move to CONVEYOR_HEAVY!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','move to CONVEYOR_LIGHT!', ')', 
 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT','not at station CHARGE1','carried weight  <=  7.0','pick!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','not at station DELIVERY','move to DELIVERY!', ')', 
 's(', 'carried weight > 7.0','at station DELIVERY','not at station CHARGE1','place!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','move to CONVEYOR_HEAVY!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','not at station CONVEYOR_LIGHT','move to CONVEYOR_LIGHT!', ')', 
 's(', 'conveyor light > 0.5','at station CONVEYOR_LIGHT','not at station CHARGE1','carried weight  <=  7.0','pick!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','move to DELIVERY!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','conveyor heavy  <=  1.5','idle!', ')', 
 's(', 'conveyor heavy > 1.5','not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','move to CONVEYOR_HEAVY!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','move to CONVEYOR_LIGHT!~||~pick!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','move to DELIVERY!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','carried weight  <=  7.0','conveyor light  <=  0.5','idle!', ')', 
 's(', 'conveyor light > 0.5','not at station CHARGE1','carried weight  <=  7.0','move to CONVEYOR_LIGHT!~||~pick!', ')', 
 's(', 'carried weight > 7.0','not at station CHARGE1','move to DELIVERY!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
] , [ 'p(', 's(', 'not at station CHARGE1','idle!', ')', 
 's(', 'at station CHARGE1','charge!', ')', 
]


alphas = [0.0 , 0.0008702702702702704 , 0.002275761475761476 , 0.0023387234042553198 , 0.00286216824111561 , 0.004518119197364479 , 0.01613263904845741 , 0.017295262636850696 , 0.021831437125748504 , 0.028595685907316433 , 0.04565415414611293 , 0.06448135999711224 , 0.10655000496981389 , 0.11300443126357335 , 0.1220828974320117]


possible_to_improve = [False , False , False , True , True , True , False , False , False , False , False , False , False , False , False]

my_bt =   [ 's(', 'f(', 'not at station DELIVERY','battery level <= 10','carried weight <= 6','place!', ')', 
 'f(', 'carried weight > 6','conveyor light <= 0', 's(', 'battery level <= 99', 'f(', 'battery level <= 10', 's(', 'not at station OTHER','not at station DELIVERY',')',')',')','move to CONVEYOR_LIGHT!', ')',
 'f(', 'carried weight <= 6', 's(', 'battery level <= 99', 'f(', 'battery level <= 10', 's(', 'not at station OTHER','not at station CONVEYOR_LIGHT','not at station CONVEYOR_HEAVY',')',')',')','move to DELIVERY!', ')',
 'f(', 'battery level > 10', 's(', 'not at station OTHER','not at station CONVEYOR_LIGHT','not at station DELIVERY','not at station CONVEYOR_HEAVY',')','move to CHARGE1!', ')',
 'f(', 'carried weight > 6','battery level <= 10', 's(', 'not at station CONVEYOR_HEAVY', 'f(', 'not at station CONVEYOR_LIGHT','conveyor light <= 0',')',')','pick!', ')',     
 'f(', 'carried weight > 6','conveyor light > 0','conveyor heavy <= 1', 's(', 'battery level <= 99', 'f(', 'battery level <= 10', 's(', 'not at station OTHER','not at station CONVEYOR_LIGHT','not at station DELIVERY',')',')',')','move to CONVEYOR_HEAVY!', ')',
 'f(', 'battery level > 99','not at station CHARGE1','charge!', ')',
'idle!', ]

my_bt_dnf = ['p(', 's(', 'at station CHARGE1','battery level <= 99','charge!', ')', 
 's(', 'conveyor light <= 0','conveyor heavy <= 1', 'f(', 'battery level > 99', 's(', 'battery level > 10','carried weight <= 6', 'f(', 'at station OTHER','at station CONVEYOR_LIGHT','at station DELIVERY',')',')',')','idle!', ')',
 's(', 'battery level <= 10', 'f(', 'at station CONVEYOR_HEAVY','at station OTHER','at station CONVEYOR_LIGHT','at station DELIVERY',')','move to CHARGE1!', ')',
 's(', 'conveyor heavy > 1','carried weight <= 6','conveyor light <= 0', 'f(', 'battery level > 99', 's(', 'battery level > 10', 'f(', 'at station OTHER','at station CONVEYOR_LIGHT','at station DELIVERY',')',')',')','move to CONVEYOR_HEAVY!', ')',
 's(', 'conveyor light > 0','carried weight <= 6', 'f(', 'battery level > 99', 's(', 'battery level > 10', 'f(', 'at station OTHER','at station DELIVERY',')',')',')','move to CONVEYOR_LIGHT!', ')',
 's(', 'carried weight > 6', 'f(', 'battery level > 99', 's(', 'battery level > 10', 'f(', 'at station CONVEYOR_HEAVY','at station OTHER','at station CONVEYOR_LIGHT',')',')',')','move to DELIVERY!', ')',
 's(', 'battery level > 10','carried weight <= 6', 'f(', 'at station CONVEYOR_HEAVY', 's(', 'at station CONVEYOR_LIGHT','conveyor light > 0',')',')','pick!', ')',
 's(', 'at station DELIVERY','battery level > 10','carried weight > 6','place!', ')',
 ]

original_bt = ['s(',
                  'f(','s(', 'at station CHARGE1?', 'charge!',')',
                  'battery level > 10?', 'at station CHARGE1?', 's(', 'move to CHARGE1!', 'charge!',')',')',
              
                  'f(', 'carried weight <= 6?', 's(', 'move to DELIVERY!','place!',')',')',
              
                  'f(','s(', 'at station CONVEYOR_HEAVY?', 'pick!',')',
                  'conveyor light <= 0?', 's(','move to CONVEYOR_LIGHT!','pick!',')',')',
              
                  'f(', 's(', 'conveyor heavy <= 1?', 'idle!',')',  's(','move to CONVEYOR_HEAVY!','pick!',')',
              ')']


with open("results/performances.csv", "a", encoding='UTF8', newline='') as csvFile:

    header = ["seed","fitness original","fitness BT-Factor", "fitness BT-Factor (dnf)", "fitness RE-BT", "BT-Factor: delta fitness" , "BT-Factor (DNF) delta fitness" ,"RE:BT: delta fitness", "Possible to improve?"]
    performance = csv.writer(csvFile)
    #performance.writerow(header)

    for j in range (173,175):
        seed_path = "results/seed" + str(j)
        path_re_bt=  seed_path + "/re-bt"
        if not os.path.exists(path_re_bt):
            os.makedirs(path_re_bt)
        path_new_method= seed_path + "/my_method"
        if not os.path.exists(path_new_method):
            os.makedirs(path_new_method)
        path_original= seed_path + "/original"
        if not os.path.exists(path_original):
            os.makedirs(path_original)
        path_new_method_dnf= seed_path + "/my_method_dnf"
        if not os.path.exists(path_new_method_dnf):
            os.makedirs(path_new_method_dnf)
        
        environment = notebook_interface.Environment(seed=j, verbose=False)


        environment.plot_individual(path_original, 'behavior_tree', original_bt)
        fitness_original_bt, delivered_heavy_original_bt, delivered_light_original_bt = environment.get_fitness(original_bt, max_ticks=200, show_world=True, seed=environment.seed) 
        output= open(seed_path + "/output.txt","w+")
        output.write("Results for seed %d\r\n" % j)
        output.write("\nOriginal method\n\n\nFitness %d\r" % fitness_original_bt)
        output.write("delivered_heavy %d\r" % delivered_heavy_original_bt)
        output.write("delivered_light %d\r" % delivered_light_original_bt)

        environment.plot_individual(path_new_method, 'behavior_tree', my_bt)
        fitness_my_bt, delivered_heavy_my_bt, delivered_light_my_bt = environment.get_fitness(my_bt, max_ticks=200, show_world=True, seed=environment.seed) 
        output.write("\n\n\nMy method\n\n\nFitness %d\r" % fitness_my_bt)
        output.write("delivered_heavy %d\r" % delivered_heavy_my_bt)
        output.write("delivered_light %d\r" % delivered_light_my_bt)

        environment.plot_individual(path_new_method_dnf, 'behavior_tree', my_bt_dnf)
        fitness_my_bt_dnf, delivered_heavy_my_bt_dnf, delivered_light_my_bt_dnf = environment.get_fitness(my_bt_dnf, max_ticks=200, show_world=True, seed=environment.seed) 
        output.write("\n\n\nMy method\n\n\nFitness %d\r" % fitness_my_bt_dnf)
        output.write("delivered_heavy %d\r" % delivered_heavy_my_bt_dnf)
        output.write("delivered_light %d\r" % delivered_light_my_bt_dnf)


        
        i=0
        re_bt = individuals[0]
        environment.plot_individual(path_re_bt, 'behavior_tree', re_bt)
        print("Alpha = ", alphas[0])
        fitness_re_bt, delivered_heavy_re_bt, delivered_light_re_bt = environment.get_fitness(re_bt, max_ticks=200, show_world=True, seed=environment.seed) 
        previous_fitness_re_bt = fitness_re_bt  
        while (previous_fitness_re_bt <= fitness_re_bt):
            i+=1
            re_bt = individuals[i]
            environment = notebook_interface.Environment(seed=j, verbose=False)
            environment.plot_individual(path_re_bt, 'behavior_tree', re_bt)
            print("Alpha = ", alphas[i])
            previous_fitness_re_bt = fitness_re_bt
            previous_delivered_heavy_re_bt = delivered_heavy_re_bt
            previous_delivered_light_re_bt = delivered_light_re_bt 
            fitness_re_bt, delivered_heavy_re_bt, delivered_light_re_bt = environment.get_fitness(re_bt, max_ticks=200, show_world=True, seed=environment.seed)        
            print("Fitness:", fitness_re_bt)
            print("Previous Fitness:", previous_fitness_re_bt)
            output.write("\n\n\nRE-BT method\n\n\nFitness %d\r" % previous_fitness_re_bt)
            output.write("delivered_heavy %d\r" % previous_delivered_heavy_re_bt)
            output.write("delivered_light %d\r" % previous_delivered_light_re_bt)
            output.write("Best alpha is %s\r" % (alphas[i-1]))
            output.write("best bt is %s\r\n" % (individuals[i-1]))

            
        output.close()
            
        performance.writerow([j,fitness_original_bt, fitness_my_bt, fitness_my_bt_dnf, previous_fitness_re_bt, abs(fitness_original_bt-fitness_my_bt), abs(fitness_original_bt-fitness_my_bt_dnf), abs(fitness_original_bt-previous_fitness_re_bt), possible_to_improve[i-1]])





