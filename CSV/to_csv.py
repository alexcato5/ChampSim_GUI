import re
import time
import pandas as pd

# Filename of the txt containing ChampSim's results
filename = 'results'
path_to_results = '../results/'

# Execution time measurement
start_time = time.time()

# Read and store results in a single variable
with open(path_to_results + filename + '.txt', 'r') as results:
    text = results.read()

# # # # #
# Regex #
# # # # #

# Pattern definitions
pattern_colon = r"(.+?)\:\s*((?:\d+\.?\d*\w-\d+|\d+\.?\d*|-\w?))\s*"
pattern_trace_name = r"(\w+\s\d+\s\w+)\s.+/(.+)"
pattern_branch_predictor = r"(\w+\s+\d+)\s+(\w+)\s+branch\s+predictor"
pattern_final_times = r"(.+?\d+).+\:\s+(\d+\.?\d*\s*hr\s+\d+\.?\d*\s*min\s*\d+\.?\d*)\s+sec"
pattern_invalid = r"(.+)\:\s*(-.*)"
pattern_number_of_results = r"(ChampSim\s*completed)"

# Regex find and store for all the text document

# Contains all values present after a colon
list_colon = re.findall(pattern_colon, text)
list_colon = [list(tup) for tup in list_colon]

# Contains the trace filenames used in each of the CPUs
list_trace_name = re.findall(pattern_trace_name, text)
list_trace_name = [list(tup) for tup in list_trace_name]

# Contains the type of branch predictor used in each core
list_branch_predictor = re.findall(pattern_branch_predictor, text)
list_branch_predictor = [list(tup) for tup in list_branch_predictor]

# Contains the final execution times for warmup and simulation
list_final_times = re.findall(pattern_final_times, text)
list_final_times = [list(tup) for tup in list_final_times]

# Stores the variables with a result of NaN across the results
list_invalid = re.findall(pattern_invalid, text)
list_invalid = [list(tup) for tup in list_invalid]

# Contains a list of a repetitive token throughout the results file, in order to distinguish the number of iterations
list_number_of_results = re.findall(pattern_number_of_results, text)
list_number_of_results = [list(tup) for tup in list_number_of_results]

# # # # # # # # # # # # # # # # # #
# Find relevant system variables #
# # # # # # # # # # # # # # # # #

number_of_results = len(list_number_of_results)
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

# Number of list_colon entries used for system information
system_info_length = 11 + 4 * number_of_cpus

# Listing general system information
list_system_info = list_colon[0:system_info_length]
del list_colon[0:system_info_length]

# # # # # # # # # # # # # # # # # # # # # # # # #
# Formatting lists to prepare for CSV printing #
# # # # # # # # # # # # # # # # # # # # # # # #

for i in range(0, system_info_length):
    list_system_info[i][0] = list_system_info[i][0].lower().replace("-bit ", "")
    list_system_info[i][0] = list_system_info[i][0].lower().replace(" ", "_")
    list_system_info[i][0] = list_system_info[i][0].lower().replace("-", "_")
    if i == 11:
        for j in range(0, number_of_cpus):
            if "cpu" not in list_system_info[i+4*j][0]:
                list_system_info[i+4*j][0] = "cpu" + str(j) + "_" + list_system_info[i+4*j][0]
                list_system_info[i+4*j+1][0] = "cpu" + str(j) + "_" + list_system_info[i+4*j+1][0]
                list_system_info[i+4*j+2][0] = "cpu" + str(j) + "_" + list_system_info[i+4*j+2][0]
                list_system_info[i+4*j+3][0] = "cpu" + str(j) + "_" + list_system_info[i+4*j+3][0]
    list_system_info[i][0] = "system_info_" + list_system_info[i][0]

for i in range(0, number_of_cpus):
    list_trace_name[i][0] = list_trace_name[i][0].lower().replace(" ", "_")
    list_branch_predictor[i][0] = list_branch_predictor[i][0].lower().replace(" ", "_") + "_branch_predictor"
    list_final_times[i][0] = list_final_times[i][0].lower().replace(" ", "_") + "_time"
    list_final_times[i + number_of_cpus][0] = list_final_times[i + number_of_cpus][0].lower().replace(" ", "_") + "_time"

for i in range(0, len(list_colon)):
    list_colon[i][0] = list_colon[i][0].lower().replace(" ", "_")
    list_colon[i][0] = list_colon[i][0].lower().replace("-", "_")
    list_colon[i][0] = list_colon[i][0].lower().replace("(", "")

# Define the number of list_colon entries taken by stats
warmup_finished_stats_length = 3 * number_of_cpus
finished_stats_length = 4 * number_of_cpus
branch_stats_length = 9 * number_of_cpus

# To be defined later
total_stats_length = 0
roi_stats_length = 0

# When this happens, ChampSim prints an extra parameter
if number_of_DRAM_channels > 1:
    dram_stats_length = 6 * number_of_DRAM_channels + 1
else:
    dram_stats_length = 6 * number_of_DRAM_channels

# Declaration of results lists
list_total_stats = []
list_roi_stats = []
list_dram_stats = []
list_branch_prediction_stats = []
list_sim_times = [['simulation_time', '']]
list_warmup_finished_stats = [[None, None]]*warmup_finished_stats_length
list_finished_stats = [[None, None]]*finished_stats_length

# Dataframe declaration
results_df = pd.DataFrame()

for i in range(0, number_of_results):
    total_stats_length = 36 * 3 * number_of_cpus
    roi_stats_length = 54 * 3 * number_of_cpus + 2 * number_of_cpus
    found_llc_stats = True

    if "warmup" in list_colon[0][0].lower():
        list_warmup_finished_stats = list_colon[0:warmup_finished_stats_length]
        del list_colon[0:warmup_finished_stats_length]
        for j in range(0, number_of_cpus):
            list_warmup_finished_stats[1 + j * 3][0] = "warmup_complete_cpu_" + str(j) + "_" + list_warmup_finished_stats[j * 3 + 1][0]
            list_warmup_finished_stats[2 + j * 3] = list_final_times[0]
            del list_final_times[0]
    if i == 0:
        list_total_stats = list_colon[0:total_stats_length]
        del list_colon[0:total_stats_length]
        list_roi_stats = list_colon[0:roi_stats_length]
        del list_colon[0:roi_stats_length]
        list_dram_stats = list_colon[0:dram_stats_length]
        del list_colon[0:dram_stats_length]
        list_branch_prediction_stats = list_colon[0:branch_stats_length]
        del list_colon[0:branch_stats_length]
        list_sim_times[0][1] = list_colon[0][1]
        del list_colon[0]

        # Fill Dataframe
        results_df = pd.concat([results_df, pd.DataFrame(list_system_info, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_branch_predictor, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_total_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_roi_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_dram_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_branch_prediction_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_sim_times, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_warmup_finished_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        results_df = pd.concat([results_df, pd.DataFrame(list_finished_stats, columns=['Parameter', f'Value at tick {i+1}'])])

    else:
        if "heartbeat" in list_colon[0][0].lower():
            del list_colon[0:5 * number_of_cpus]
        if "llc" not in list_colon[93][0].lower():
            found_llc_stats = False
        if found_llc_stats:
            for j in range(0, total_stats_length):
                list_total_stats[j][1] = list_colon[0][1]
                del list_colon[0]
        else:
            k = 0
            for j in range(0, number_of_cpus):
                while k < total_stats_length/(number_of_cpus-j) - 15:
                    list_total_stats[k][1] = list_colon[0][1]
                    del list_colon[0]
                    k = k + 1
                for n in range(k, int(total_stats_length/(number_of_cpus-j))):
                    list_total_stats[n][1] = 0
                k = k + 15
        # Read ROI
        if found_llc_stats:
            for j in range(0, roi_stats_length):
                list_roi_stats[j][1] = list_colon[0][1]
                del list_colon[0]
        else:
            k = 0
            for j in range(0, number_of_cpus):
                while k < roi_stats_length/(number_of_cpus-j) - 23:
                    list_roi_stats[k][1] = list_colon[0][1]
                    del list_colon[0]
                    k = k + 1
                for n in range(k, int(roi_stats_length/(number_of_cpus-j))):
                    list_roi_stats[n][1] = 0
                k = k + 23
        for j in range(0, dram_stats_length):
            list_dram_stats[j][1] = list_colon[0][1]
            del list_colon[0]
        for j in range(0, branch_stats_length):
            list_branch_prediction_stats[j][1] = list_colon[0][1]
            del list_colon[0]
        list_sim_times[0][1] = list_colon[0][1]
        del list_colon[0]

        if "finished" in list_colon[0][0].lower():
            list_finished_stats = list_colon[0:finished_stats_length]
            del list_colon[0:finished_stats_length]
            for j in range(0, number_of_cpus):
                list_finished_stats[1 + j * 4][0] = "finished_complete_cpu_" + str(j) + "_" + list_finished_stats[j * 4 + 1][0]
                list_finished_stats[2 + j * 4][0] = "finished_complete_cpu_" + str(j) + "_" + list_finished_stats[j * 4 + 2][0]
                list_finished_stats[3 + j * 4] = list_final_times[0]
                del list_final_times[0]

        # Fill Dataframe:
        temp_df = pd.DataFrame()
        temp_df = pd.concat([temp_df, pd.DataFrame(list_system_info, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_branch_predictor, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_total_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_roi_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_dram_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_branch_prediction_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_sim_times, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_warmup_finished_stats, columns=['Parameter', f'Value at tick {i+1}'])])
        temp_df = pd.concat([temp_df, pd.DataFrame(list_finished_stats, columns=['Parameter', f'Value at tick {i+1}'])])

        new_column = list(temp_df.pop(f"Value at tick {i+1}"))
        results_df[f'Value at tick {i+1}'] = new_column
        results_df = results_df.set_axis(temp_df['Parameter'], axis=0)

# For debugging purposes:
'''
with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    print(results_df)

# (should be NULL)
for i in range(0, len(list_colon)):
    print(list_colon)
'''

# Correction of the Dataframe printing indexes
del results_df["Parameter"]

# Print DataFrame to CSV output file
results_df.to_csv(path_to_results + filename + '.csv', encoding='utf-8', index=True)

# CSV converter execution time
print(f'\n---\tConverted to CSV in {(time.time() - start_time):.4f} seconds\t---\n<<<\t\t\tCheck {filename}.csv\t\t\t>>>')
