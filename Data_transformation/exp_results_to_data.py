from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
import os, sys

def get_branch(concept):
    branches = ['edible_fruit.n.01', 'clothing.n.01', 'hand_tool.n.01', 'musical_instrument.n.01', 'furniture.n.01']
    conc = concept[::-1].replace('_','.',1)[::-1]
    conc = conc[::-1].replace('_','.',1)[::-1]

    if conc == "highhat_cymbal.n.01":
        conc = "high-hat_cymbal.n.01"

    if conc == "carpenters_square.n.01":
        conc = "carpenter's_square.n.01"

    if conc == "carpenters_hammer.n.01":
        conc = "carpenter's_hammer.n.01"

    syn = wn.synset(conc)

    data = None
    hypers = list(set([s.name() for s in syn.closure(lambda s:s.hypernyms())]))

    has_hyper = list(set(hypers) & set(branches))

    if syn.name() in branches:
        data = syn.name()

    elif len(has_hyper)>0:
        data = has_hyper[0]

    else:
        print(hypers)
        
    print(data)
    return data

def data_from_exp_files(file_path):
    exp_result_files = os.listdir(os.path.join(file_path,'experiment_data'))

    participant_experiment_results = []
    participant_info = False
    partic_dict = {'partic_id':[], 'correct_ans':[], 'wrong_ans':[], 'rate':[]}
    for txt_file in exp_result_files:
        participant_id = txt_file.split('.')[3]
        fpath = os.path.join(file_path,'experiment_data',txt_file)
        
        with open(fpath, 'r') as file:
            data_dict = False
            
            for line in file:
                line = line.strip("\n").split(' ')

                if not data_dict:
                    data_dict={'c_name':[line[1]], 'c_img':[line[3]],'lvl':[line[2]],'branch':[get_branch(line[1])],'resp_type':[line[4]],'partic_id':[participant_id], 'is_ans_correct':[line[5]], 'react_time':[line[6]]}
                else:
                    data_dict['c_name'].append(line[1])
                    data_dict['c_img'].append(line[3])
                    data_dict['lvl'].append(line[2])
                    data_dict['branch'].append(get_branch(line[1]))
                    data_dict['resp_type'].append(line[4])
                    data_dict['partic_id'].append(participant_id)
                    data_dict['is_ans_correct'].append(line[5])
                    data_dict['react_time'].append(line[6])

            exp_df = pd.DataFrame(data_dict)

            fail_count = exp_df.groupby('is_ans_correct').count().to_numpy()
            
            partic_dict['partic_id'].append(participant_id)
            partic_dict['correct_ans'].append(fail_count[0][1])
            partic_dict['wrong_ans'].append(fail_count[1][1])
            partic_dict['rate'].append(np.round((fail_count[1][1]/396)*100)/100)            
            exp_df.to_csv(os.path.join('experiment_data_computed', f"data_{participant_id}.csv"))
            participant_experiment_results.append(exp_df)
        participant_info = pd.DataFrame(partic_dict)
        participant_info.to_csv(os.path.join('experiment_data_computed', f"data_participants.csv"))
    return participant_experiment_results, participant_info

def main():
    cwd = os.getcwd()
    results = os.path.join(cwd,'p1_data')
    all_exp_results, participant_data = data_from_exp_files(results)
    
    # Now creating a data_set by converging all participants times

    all_exp_results_concat = pd.concat(all_exp_results)
    all_exp_results_concat.to_csv(os.path.join('p1_computed', f"data_all_ans.csv"))

    return None

if __name__ == "__main__":
    main()