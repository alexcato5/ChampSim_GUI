import re
import pandas as pd
import os

filename = 'results'
path_to_results = '../results/'

with open(path_to_results + filename + '.txt', 'r') as results:
    text = results.read()

# Regex pattern definitions
pattern_colon = r"(.+?)\:\s*((?:\d+\.?\d*|-\w?))\s*"
pattern_trace_name = r"(\w+\s\d+\s\w+)\s.+/(.+)"
pattern_branch_predictor = r"(\w+\s+\d+)\s+(\w+)\s+branch\s+predictor"
pattern_time = r"(.+?\d+).+\:\s+(\d+\.?\d*\s*hr\s+\d+\.?\d*\s*min\s*\d+\.?\d*)\s+sec"
pattern_invalid = r"(.+)\:\s*(-.*)"

# Regex find and store for all the text document
list_colon = re.findall(pattern_colon, text)
list_colon = [list(tup) for tup in list_colon] # Convert to list of lists

list_trace_name = re.findall(pattern_trace_name, text)
list_trace_name = [list(tup) for tup in list_trace_name] # Convert to list of lists

list_branch_predictor = re.findall(pattern_branch_predictor, text)
list_branch_predictor = [list(tup) for tup in list_branch_predictor] # Convert to list of lists

list_time = re.findall(pattern_time, text)
list_time = [list(tup) for tup in list_time] # Convert to list of lists

list_invalid = re.findall(pattern_invalid, text)
list_invalid = [list(tup) for tup in list_invalid] # Convert to list of lists

# Finding relevant variables: number of CPUs and number of DRAM channels
number_of_cpus = 0
number_of_DRAM_channels = 0
found_cpu_number = False
found_channel_number = False

i = 0
while i in range(0, len(list_colon), 1) and not found_cpu_number or not found_channel_number:
    if "Number of CPUs" in list_colon[i][0]:
        number_of_cpus = int(list_colon[i][1])
        found_cpu_number = True
    elif "Channels" in list_colon[i][0]:
        number_of_DRAM_channels = int(list_colon[i][1])
        found_channel_number = True
    i = i + 1

# Formatting lists to prepare for CSV printing
for i in range(0, len(list_colon)):
    list_colon[i][0] = list_colon[i][0].lower().replace("-bit ", "")
    list_colon[i][0] = list_colon[i][0].lower().replace(" ", "_")
    list_colon[i][0] = list_colon[i][0].lower().replace("-", "_")
    list_colon[i][0] = list_colon[i][0].lower().replace("(", "")

total_stats_index = 0
interest_index = 0
starting_total_stats_index = total_stats_index
saved_starting_total_stats_index = total_stats_index
starting_interest_index = interest_index

total_stats_length = 93 # Length of total stats per CPU in list_colon items
interest_length = 90 # Length of region of interest per CPU in list_colon items

for i in range(0, number_of_cpus):

    list_trace_name[i][0] = list_trace_name[i][0].replace(" ", "_")

    list_branch_predictor[i][0] = list_branch_predictor[i][0].replace(" ", "_") + "_branch_predictor"

    list_time[i][0] = list_time[i][0].replace(" ", "_")
    list_time[i + number_of_cpus][0] = list_time[i + number_of_cpus][0].replace(" ", "_")

    found_basic = False
    found_warmup = False
    found_finished = False
    reached_total_stats = False
    reached_interest = False

    for j in range(0, len(list_colon)):
        if "cpu" not in list_colon[j][0] and "basic" in list_colon[j][0] and not found_basic:
            list_colon[j][0] = list_colon[j][0].replace("basic", "cpu" + str(i) + "_basic")
            list_colon[j+1][0] = list_colon[j+1][0].replace("ways", "cpu" + str(i) + "_basic_btb_ways")
            list_colon[j+2][0] = list_colon[j+2][0].replace("indirect", "cpu" + str(i) + "_basic_btb_indirect")
            list_colon[j+3][0] = list_colon[j+3][0].replace("ras", "cpu" + str(i) + "_basic_btb_ras")
            found_basic = True

        if "warmup_complete" in list_colon[j][0] and not found_warmup and "cpu" not in list_colon[j+1][0]:
            list_colon[j+1][0] = list_colon[j+1][0].replace("cycles", "cpu" + str(i) + "_warmup_cycles")
            list_colon[j+2][0] = list_colon[j+2][0].replace("simulation", "cpu" + str(i) + "_warmup_simulation")
            found_warmup = True

        if "finished_cpu" in list_colon[j][0] and not found_finished and "cpu" not in list_colon[j+1][0]:
            list_colon[j+1][0] = list_colon[j+1][0].replace("cycles", "cpu" + str(i) + "_finished_cycles")
            list_colon[j+2][0] = list_colon[j+2][0].replace("cumulative", "cpu" + str(i) + "_finished_cumulative")
            list_colon[j+3][0] = list_colon[j+3][0].replace("simulation", "cpu" + str(i) + "_finished_simulation")
            found_finished = True
            reached_total_stats = True
            if i == 0:
                total_stats_index = j + 4 * number_of_cpus
                saved_starting_total_stats_index = starting_total_stats_index
            else:
                total_stats_index = j + 4 * number_of_cpus + total_stats_length - 4
            starting_total_stats_index = total_stats_index

        if reached_total_stats and total_stats_index < starting_total_stats_index + total_stats_length:
            if "cpu" in list_colon[total_stats_index][0] and "total_stats" not in list_colon[total_stats_index][0]:
                list_colon[total_stats_index][0] = "total_stats" + "_" + list_colon[total_stats_index][0]
            if "cpu" not in list_colon[total_stats_index][0] and "total_stats" not in list_colon[total_stats_index][0]:
                list_colon[total_stats_index][0] = "total_stats_cpu" + str(i) + "_" + list_colon[total_stats_index][0]
            total_stats_index = total_stats_index + 1

        '''Arreglar
        temp = total_stats_index
        if temp == total_stats_length + starting_total_stats_index:
            reached_total_stats = False
            reached_interest = True
            interest_index = total_stats_length * ( number_of_cpus - i ) + saved_starting_total_stats_index
            starting_interest_index = interest_index
            temp = temp + 1

        if reached_interest and interest_index < starting_interest_index + interest_length:
            if "cpu" in list_colon[interest_index][0] and "interest" not in list_colon[interest_index][0]:
                list_colon[interest_index][0] = "interest_" + list_colon[interest_index][0]
            if "cpu" not in list_colon[interest_index][0] and "interest" not in list_colon[interest_index][0]:
                list_colon[interest_index][0] = "interest_cpu" + str(i) + "_" + list_colon[interest_index][0]
            interest_index = interest_index + 1
'''

        if "cpu_" + str(i) + "_branch_prediction" in list_colon[j][0] and "cpu" not in list_colon[j+1][0]:
            list_colon[j+1][0] = "cpu" + str(i) + "_" + list_colon[j+1][0]
            list_colon[j+2][0] = "cpu" + str(i) + "_" + list_colon[j+2][0]
            list_colon[j+3][0] = "cpu" + str(i) + "_" + list_colon[j+3][0]
            list_colon[j+4][0] = "cpu" + str(i) + "_" + list_colon[j+4][0]
            list_colon[j+5][0] = "cpu" + str(i) + "_" + list_colon[j+5][0]
            list_colon[j+6][0] = "cpu" + str(i) + "_" + list_colon[j+6][0]
            list_colon[j+7][0] = "cpu" + str(i) + "_" + list_colon[j+7][0]
            list_colon[j+8][0] = "cpu" + str(i) + "_" + list_colon[j+8][0]

current_dram_channel = 0
for j in range(0, len(list_colon)):
    if "_rq_row" in list_colon[j][0] and "dram_channel" not in list_colon[j][0]:
        list_colon[j][0] = "dram_channel" + str(current_dram_channel) + list_colon[j][0]
        list_colon[j+1][0] = "dram_channel" + str(current_dram_channel) + "_" + list_colon[j+1][0]
        list_colon[j+2][0] = "dram_channel" + str(current_dram_channel) + list_colon[j+2][0]
        list_colon[j+3][0] = "dram_channel" + str(current_dram_channel) + "_" + list_colon[j+3][0]
        list_colon[j+4][0] = "dram_channel" + str(current_dram_channel) + "_" + list_colon[j+4][0]
        list_colon[j+5][0] = "dram_channel" + str(current_dram_channel) + "_" + list_colon[j+5][0]
        current_dram_channel = current_dram_channel + 1

# Creating output DataFrame
results_df = pd.DataFrame(list_trace_name, columns=['Parameter', 'Value at tick'])
results_df = pd.concat([results_df, pd.DataFrame(list_time, columns=['Parameter', 'Value at tick'])])
results_df = pd.concat([results_df, pd.DataFrame(list_branch_predictor, columns=['Parameter', 'Value at tick'])])
results_df = pd.concat([results_df, pd.DataFrame(list_colon, columns=['Parameter', 'Value at tick'])])

# Print DataFrame to CSV output file
# Check if file is empty
file_is_empty = False
if os.stat(path_to_results + filename + '.csv').st_size == 0:
    file_is_empty = True

if file_is_empty:
    results_df.to_csv(path_to_results + filename + '.csv', encoding='utf-8', index=False)
else:
    results_csv = pd.read_csv(path_to_results + filename + '.csv')
    new_column = list(results_df.pop("Value at tick"))
    results_csv['new_column'] = new_column
    results_csv.rename(columns={'new_column':'Value at Tick'}, inplace=True)
    results_csv.to_csv(path_to_results + filename + '.csv', index=False)
