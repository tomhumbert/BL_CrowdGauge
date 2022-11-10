from datetime import datetime
from nltk.corpus import wordnet as wn
import sys, os, random, math
import pandas as pd
from colorama import Fore, Back, Style

class experiment_creator:
    cwd = os.path.abspath(".")
    input_df = False
    task_table = ""
    task_tables = []
    experiment = ""
    experiment_input_file_name = ""
    rand_img_selector_dict = dict()
    
    experiment_code_file = ""
    experiment_task_table_file = ""
    experiment_task_table_files = []
    experiment_training_tasks = ""
    experiment_image_list = ""
    
    def __init__(self, name, folder, collection_df, is_load=False):
        self.experiment_input_file_name = name
        self.input_df = collection_df
        self.cwd = folder
        self.experiment_code_file = f"{name}_code.txt"
        self.experiment_task_table_file = f"{name}_tasks.txt"
        self.experiment_training_tasks = f"{name}_training.txt"
        self.experiment_image_list = f"{name}_images.txt"

        with open(os.path.join(self.cwd, self.experiment_image_list), 'w') as file:
            image_names = collection_df["hyponym"].tolist()
            content = ""
            for img in image_names:
                img_a = img.replace('.', '_').replace("-", '').replace("'", '')
                content += f"{img_a}\n"
            file.write(content)

        self.img_dict_create(collection_df)

        print("Experiment generator initialized")

        return None

    def generate(self):
        flag = True
        try:
            self.shuffle_gen()
            self.experiment = self.gen_experiment_code()
            print("Experiment Generation successful ..")
        except:
            flag = False
            print("TT GENERATION FAILED!")
        return flag

    def gen_v2(self):
        flag = True
        
        self.task_tables = self.split_tasktable(self.task_table)
        self.experiment = self.gen_experiment_v2()
    
        print("All tasklists have been generated .. ")
        return flag

    def img_dict_create(self, df):
        hypernym_groups = list(set(df.get('hypernym').tolist()))
        for x in hypernym_groups:
            images = df[df.hypernym == x].get('hyponym').tolist()
            image_list = [(img, 0) for img in images]
            image_list +=  [(img, 1) for img in images]
            image_list +=  [(img, 2) for img in images]
            
            self.rand_img_selector_dict[x] = set(image_list)
        print("Img dictionary created ..")
        
    def rand_false_img(self, group):
        branches = list(self.rand_img_selector_dict.keys())
        other_branches_set = set(branches) - set([group])
        imgs = []
        for br in list(other_branches_set):
            img_list = list(self.rand_img_selector_dict[br])
            for img in img_list:
                imgs.append((img, br))
        img = False
        while True:
            random.seed(datetime.now())
            if len(imgs) > 0:
                img = random.choice(imgs)
                self.rand_img_selector_dict[img[1]] -= set([img[0]])
                break
            elif len(imgs) == 0:
                print("There were not enough pictures available to choose from! Please rebalance the image sets.")
                break
            else:
                print("What did just happen?")
                pass
        return img[0][0]

    def gen_task_list(self, df):
        all_tasks = []
        tasktable = "#-image-----------------label-----------------------condition (concept, group, image, exp_response)----------------------correct_response-"
        
        for index, row in df.iterrows(): 
            for i in range(3):
                group = ""
                if i == 0:
                    group = "hypernym"
                if i == 1:
                    group = "bl"
                if i == 2:
                    group = "hyponym"

                # This creates correct concept - image pairings
                concept = row[group]
                concept_string = concept.replace(".", "_").replace("-", '').replace("'", '')
                img = row['hyponym'].replace(".", "_").replace("-", '').replace("'", '')
                condition = f"\"{concept_string} {group} {img} True\""
                label = capitalize(wn.synset(concept).lemma_names()[0])
                label = f"\"{label}\""
                newline = f"\n{img} {label} {condition} 1"

                all_tasks.append(newline)

                #Then the false concept - image pairings
                img = self.rand_false_img(row['hypernym'])
                img = img.replace(".", "_").replace("-", '').replace("'", '')
                condition = f"\"{concept_string} {group} {img} False\""
                label = capitalize(wn.synset(concept).lemma_names()[0])
                label = f"\"{label}\""
                newline = f"\n{img} {label} {condition} 2"

                all_tasks.append(newline)
                
        all_tasks = random.sample(all_tasks, len(all_tasks))
        for t in all_tasks:
            tasktable += t
        
        return tasktable

    def split_tasktable(self, tasktable):
        ini_tasktable = tasktable.split('\n')
        top_row = ini_tasktable[0]
        ini_tasktable = ini_tasktable[1:]
        task_num = len(ini_tasktable)
        last_group_len = task_num%20
        group_num = task_num//20
        tasktables = []

        if last_group_len != 0:
            group_num +=1
               
        for i in range(group_num):
            new_tt = ""
            new_tt += top_row

            if (i == group_num-1 and last_group_len >0):
                for j in range(last_group_len):
                    new_tt += f"\n{ini_tasktable[j+(i*20)]}"
            
            else:
                for j in range(20):
                    new_tt += f"\n{ini_tasktable[j+(i*20)]}"

            tasktables.append(new_tt)
            print(f"Tasklist {i+1} was generated ..")
        self.task_tables = tasktables

        for k in range(len(tasktables)):
            self.experiment_task_table_files.append(f"{self.experiment_input_file_name}_tl{k}.txt")

        return tasktables

    def shuffle_gen(self):
        self.input_df = self.input_df.sample(frac=1)
        print("Dataframe shuffled..")
        self.task_table = self.gen_task_list(self.input_df)
        print("Tasktable generated")
        return self.task_table

    def store_tt(self, option='single'):
        if option == 'single':
            with open(os.path.join(self.cwd,self.experiment_task_table_file),'w') as file:
                file.write(self.task_table)

        if option == 'multi':
            for i in range(len(self.task_tables)):
                ttable = self.task_tables[i]
                with open(os.path.join(self.cwd,self.experiment_task_table_files[i]),'w') as file:
                    file.write(ttable)
        return None
        

    def gen_experiment_code(self):
        task_list_len = len(self.input_df.index)*6
        block_num = int(task_list_len/20)+1
        remainder = task_list_len%20

        num_trials = 20
        #the fixed no-repeat version apparently worked too? Still a mistake, but would be nice if the experiment could actually shuffle and still never ask smth twice from round to round. IT DID NOT WORK, MUST AVOID 'FIXED'
        mode = 'fixed'
        absolved_trials = 0
        all_blocks = ""
        # Here I need to fix the last group, which is shorter than 20, already fixed the 21st redundant group. FIXED
        for i in range(block_num):
            if (i+1)*20 > task_list_len:
                num_trials = remainder
            if i > 0:
                all_blocks = all_blocks + """message break_screen
"""
            absolved_trials += num_trials
            #Here I need to give the participants the information of how many wrong answers they gave, to further play into the "game" factor of the experiment.
            #DONE
            all_blocks = all_blocks + f"""
block group{i}
    delay 500
    tasklist
        Rosch {num_trials} {mode}
    end
    feedback
        set &fastest min c7 ; select c6 == 1
        set &slowest max c7 ; select c6 == 1
        set &correct count ; select c6 == 1
        text align center
        text color black
        text 0 -35 "Well done!"
        text 0 0 &correct ; prefix "Correct answers: " ; postfix " out of {absolved_trials}"
        text 0 30 &fastest ; prefix "Your fastest response time: " ; postfix " ms"
        text 0 60 &slowest ; prefix "Your slowest response time: " ; postfix " ms"
        text 0 90 "Press the spacebar to continue to the break screen."
    end

"""

        #Here I need to add the response to the participant, if he was right or wrong with a cross or checkmark # DONE
        #TODO: The very last message needs to say smth like "This is the end, press spacebar to end the experiment."
        experiment = f"""options
    background color white
    bitmapdir images

bitmaps
    include {self.experiment_image_list}
    cross
    check
    true_bar
    false_bar
    Intro1
    Intro2
    Intro3
    IntroEND
    break_screen

fonts
    arial 20
    bahn BAHNSCHRIFT.TTF 40

table all_tasks
    include {self.experiment_task_table_file}

task Rosch
    font bahn
    table all_tasks
    keys l a
    show bitmap true_bar 390 0
    show bitmap false_bar -390 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 10000
    if STATUS != CORRECT                   # if you make an error
        show bitmap cross                  # show a blinking cross for a wrong answer
        delay 50                           
        clear 5
        delay 50                           
        show bitmap cross                 
        delay 50                           
    fi
    if STATUS == CORRECT                    
        show bitmap check                  # Checkmark for a correct answer
        delay 80                           
    fi
    clear 5                            # and then clear
    delay 10                           # 10 ms for the drama
    clear 3 4
    delay 200                              
    save TABLEROW @3 STATUS RT             # save data to file

message Intro1
message Intro2
message Intro3
message IntroEND
{all_blocks}

        """
        with open(os.path.join(self.cwd, self.experiment_code_file), 'w') as file:
            file.write(experiment)

        return experiment

    def gen_experiment_v2(self):
        block_num = len(self.experiment_task_table_files)
        mode = 'all_before_repeat'
        absolved_trials = 0
        all_blocks = ""

        for i in range(block_num):
            if i > 0:
                all_blocks = all_blocks + """message break_screen
"""
            ttable = self.task_tables[i]
            num_trials = len(ttable.split('\n'))-1
            absolved_trials += num_trials
            all_blocks = all_blocks + f"""
block group{i}
    delay 500
    tasklist
        Rosch{i} {num_trials} {mode}
    end
    feedback
        set &fastest min c7 ; select c6 == 1
        set &slowest max c7 ; select c6 == 1
        set &correct count ; select c6 == 1
        text align center
        text color black
        text 0 -35 "Well done!"
        text 0 0 &correct ; prefix "Correct answers: " ; postfix " out of {absolved_trials}"
        text 0 30 &fastest ; prefix "Your fastest response time: " ; postfix " ms"
        text 0 60 &slowest ; prefix "Your slowest response time: " ; postfix " ms"
        text 0 90 "Press the spacebar to continue to the break screen."
    end

"""

        all_tables = ""
        all_tasks = ""

        for j in range(len(self.experiment_task_table_files)):
            all_tables += f"""
table all_tasks{j}
    include {self.experiment_task_table_files[j]}
"""

            all_tasks += f"""
task Rosch{j}
    font bahn
    table all_tasks{j}
    part rest_of_experiment
"""
        
        #Here I need to add the response to the participant, if he was right or wrong with a cross or checkmark # DONE
        #TODO: The very last message needs to say smth like "This is the end, press spacebar to end the experiment."
        experiment = f"""options
    background color white
    bitmapdir images

bitmaps
    include {self.experiment_image_list}
    cross
    check
    true_bar
    false_bar
    Intro1
    Intro2
    Intro3
    IntroEND
    break_screen

fonts
    arial 20
    bahn BAHNSCHRIFT.TTF 40
{all_tables}
part rest_of_experiment
    keys l a
    show bitmap true_bar 390 0
    show bitmap false_bar -390 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 10000
    if STATUS != CORRECT                   # if you make an error
        show bitmap cross                  # show a blinking cross for a wrong answer
        delay 50                           
        clear 5
        delay 50                           
        show bitmap cross                 
        delay 50                           
    fi
    if STATUS == CORRECT                    
        show bitmap check                  # Checkmark for a correct answer
        delay 80                           
    fi
    clear 5                            # and then clear
    delay 10                           # 10 ms for the drama
    clear 3 4
    delay 200                              
    save TABLEROW @3 STATUS RT             # save data to file
{all_tasks}
message Intro1
message Intro2
message Intro3
message IntroEND
{all_blocks}

        """
        with open(os.path.join(self.cwd, self.experiment_code_file), 'w') as file:
            file.write(experiment)

        print("The experiment is now complete and ready to upload.")
        return True


#===============================================================================================
#OLD CODE, DISREGARD

#Various colored console output methods.
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))

def prList(list):
    '''Takes any list.
    Pretty prints it in the console.
    Returns True.'''
    count = 1
    for li in list:
        print(f"    {count}) {li}")
        count +=1

    print()
    return True

def capitalize(word):
    label = word.split('.')[0]
    label = label.replace("_", " ").replace("'", "").capitalize()
    return  label

def select_files(list):
    selection = []
    prRed(50*"=_")
    print("These files are available for conversion:")
    prList(list)
    print("\nWrite either 'all' or list the exact names of the files, seperated by spaces, you would like to convert to a psytoolkit task table:")
    ans = input("> ")

    if ans == "all":
        selection = list
    else:
        selection = ans.split(" ")

    prRed(50*"=-")
    return selection

def create_tt(dfs, lvl):
    tasktable = "#-image--label--condition(img,group,label,ans)--correct_response-#"
    unique_labels = []
    #first run of all the correct labels
    for df in dfs:
        unique_labels.append(df.hypernym.unique())
        for index, row in df.iterrows(): 
            img = row["hyponym_img"]
            label = row[lvl]
            condition = f"\'{img} {lvl} {label} True\'"
            label = capitalize(label)
            label = f"\'{label}\'"
            newline = f"\n{img} {label} {condition} 1"
            tasktable = tasktable + newline

    #now create false labels
    for df in dfs:
        for index, row in df.iterrows(): 
            img = row["hyponym_img"]
            lb_candidates = df[df["hypernym"] != row["hypernym"]]
            label = lb_candidates[lvl].tolist()[random.randint(0,(len(lb_candidates)-1))]
            condition = f"\'{img} {lvl} {label} False\'"
            label = capitalize(label)
            label = f"\'{label}\'"
            newline = f"\n{img} {label} {condition} 2"
            tasktable = tasktable + newline

    prGreen(f"Finished creating the tasktable for {lvl} lvl")
    print()
    return tasktable

def store(folder, filename, content):
    os.chdir(folder)
    success = False
    try:
        with open(filename, "w") as file:
            file.write(content)
        success = True
    except:
        prRed("The file could not be saved.")

    os.chdir("..")
    return success

def create_image_list_file():
    image_list = ""

    return store("Rosch7", "image_list.txt", image_list)

def write_exp_code(taskgroups):
    blocks={"block1":{  "length": len(taskgroups['hypernym'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("},
            "block2":{  "length": len(taskgroups['bl'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("},
            "block3": {"length": len(taskgroups['hyponym'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("}
    }

    for key in blocks.keys():
        length = blocks[key]['length']
        for i in range(length):
            if i == (length/2)-1:
                blocks[key]['true_rows'] += f"c1 == {i} ) && c5 == 1"
            elif i == length-1:
                blocks[key]['false_rows'] += f"c1 == {i} ) && c5 == 1"
            elif i < (length-1)/2:
                blocks[key]['true_rows'] += f"c1 == {i} ||"
            else:
                blocks[key]['false_rows'] += f"c1 == {i} ||"
    
    content = f"""#In the original Rosch experiment(7) 15 people participated in judging superordinate names of objects.
options
    background color white
    bitmapdir images

bitmaps
    include image_list.txt
    mistake
    intro
    intro2
    outro

fonts
    arial 20
    bahn BAHNSCHRIFT.TTF 40

table hypernym_tasks
    include tasklist_hypernym.txt

table bl_tasks
    include tasklist_bl.txt

table hyponym_tasks
    include tasklist_hyponym.txt

task hypernyms
    font bahn
    table hypernym_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file

task bl
    font bahn
    table bl_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file


task hyponyms
    font bahn
    table hyponym_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file


message intro
message intro2

block group1 
    delay 1000
    tasklist
        hypernyms {blocks["block1"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block1"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block1"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message intro2

block group2 
    delay 1000
    tasklist
        bl {blocks["block2"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block2"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block2"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message intro2

block group3 
    delay 1000
    tasklist
        hyponyms {blocks["block3"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block3"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block3"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message outro
 """

    return store("Rosch7", "code.psy", content)

def main():
    cwd = os.getcwd()
    exp_input_folder = "exp_selection"
    exp_folder = "Rosch7"
    img_folder = os.path.join(exp_folder,"images")

    if not os.path.isdir(exp_folder):
        os.mkdir(exp_folder)

    if not os.path.isdir(img_folder):
        os.mkdir(img_folder)

    files = os.listdir(exp_input_folder)
    exp_files = select_files(files)
    dataframes = []
    taskgroups = {'hypernym':"",'bl':"",'hyponym':""}

    for file in exp_files:
        df = pd.read_csv(os.path.join(exp_input_folder, file))
        dataframes.append(df)

    for lvl in taskgroups.keys():
        taskgroups[lvl] = create_tt(dataframes, lvl)
        if store(exp_folder, f"tl_{lvl}.txt", taskgroups[lvl]):
            prGreen(f"The {lvl} taskgroup has been created in the Rosch7 experiment folder.")
    
    prYellow("Do you also want the code for the experiment automatically generated?")
    cont_program = input("(y/n)? >")
    if cont_program == 'y':
        code = write_exp_code(taskgroups)

    #Need to paste a copy of the 'publish' folder with files into exp_folder

    prGreen(30*'+')
    prGreen("The process has concluded.")
    prGreen(30*'+')
    print()
    print("If it hasn't existed yet, the experiment folder was created with the images and publish folders inside.")
    prYellow("The folder should now contain:")
    prList(["Three tasklist files","A file listing all images","The main code.psy file","An 'images' folder", "A 'publish' folder"])
    print()
    print(30*"~")
    prRed("Do not forget to paste the images in the images folder, with the exact names as they are listed in the experiment input file.")
    prYellow("All images should have white background, depict only the object and be 400x400 pixels in size.")
    print(30*"~")

if __name__ == "__main__":
    main()