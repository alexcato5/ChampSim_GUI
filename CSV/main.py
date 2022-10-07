import re
import csv

filename = 'results'
with open('../results/' + filename + '.txt', 'r') as results:
    text = results.read()

# Regex pattern definitions
pattern_colon = r"(.+?)\:\s+(\d+\.?\d*)\s*"
pattern_trace_name = r"\w+\s(\d+)\s\w+\s.+/(.+)"
pattern_branch_predictor = r"\w+\s+(\d+)\s+(\w+)\s+branch\s+predictor"
pattern_time = r"(.+?)(\d+).+\:\s+(\d+\.?\d*\s*hr\s+\d+\.?\d*\s*min\s*\d+\.?\d*)\s+sec"
pattern_invalid = r"(.+)\:\s*(-.*)"
# Regex find and store for all the text document
list_colon = re.findall(pattern_colon, text)
list_trace_name = re.findall(pattern_trace_name, text)
list_branch_predictor = re.findall(pattern_branch_predictor, text)
list_time = re.findall(pattern_time, text)
list_invalid = re.findall(pattern_invalid, text)

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

# Iterable lists:
list_colon_iter = iter(list_colon)

# Common stats
header_common_stats = []
values_common_stats = []
list_value = []

for i in range(0, 11, 1): # This line works regardless of the number of CPUs
    list_value = next(list_colon_iter)
    header_common_stats.append(list_value[0].replace("-bit ", ""))
    values_common_stats.append(list_value[1])

# CPU Stats

# Configuration stats
header_cpu_configuration = []
values_cpu_configuration = []

for i in range(0, number_of_cpus, 1):

    header_cpu_configuration.append("Running")
    values_cpu_configuration.append(list_trace_name[i][1])

    header_cpu_configuration.append("Branch predictor")
    values_cpu_configuration.append(list_branch_predictor[i][1])

    for j in range(0, 11, 1):
        list_value = next(list_colon_iter)
        header_cpu_configuration.append(list_value[0])
        values_cpu_configuration.append(list_value[1])

# Total stats
header_cpu_total_stats = []
values_cpu_total_stats = []

for i in range(0, number_of_cpus, 1):
    for i in range(0, 93, 1):
        list_value = next(list_colon_iter)
        header_cpu_total_stats.append(list_value[0])
        values_cpu_total_stats.append(list_value[1])

# Interest stats
header_cpu_interest_stats = []
values_cpu_interest_stats = []

for i in range(0, number_of_cpus, 1):
    for i in range(0, 138, 1):
        list_value = next(list_colon_iter)
        header_cpu_interest_stats.append(list_value[0])
        values_cpu_interest_stats.append(list_value[1])

# DRAM stats
header_DRAM_stats = []
values_DRAM_stats = []

for i in range(0, number_of_DRAM_channels, 1):
    for i in range(0, 5, 1):
        list_value = next(list_colon_iter)
        header_DRAM_stats.append(list_value[0])
        values_DRAM_stats.append(list_value[1])

# Branch prediction stats
header_cpu_branch_stats = []
values_cpu_branch_stats = []

for i in range(0, number_of_cpus, 1):
    for i in range(0, 9, 1):
        list_value = next(list_colon_iter)
        header_cpu_branch_stats.append(list_value[0])
        values_cpu_branch_stats.append(list_value[1])

# Begin CSV printing process

# Find the biggest list to use its length as a reference for the number of commas per line
lengths = [len(header_DRAM_stats), len(header_cpu_total_stats), len(header_cpu_configuration), len(header_cpu_branch_stats), len(header_cpu_interest_stats), len(header_common_stats)]
biggest_length = max(lengths)
with open('../results/' + filename + '.csv', 'w') as csv_output:
    writer = csv.writer(csv_output)
    writer.writerow(['Common Stats'] + ['']*(biggest_length-1))
    writer.writerow(header_common_stats + ['']*(biggest_length-len(header_common_stats)))
    writer.writerow(values_common_stats + ['']*(biggest_length-len(values_common_stats)))

    for i in range(0, number_of_cpus, 1):
        writer.writerow(['CPU ' + str(i) + ' Stats'] + ['']*(biggest_length-1))
        writer.writerow(['Configuration'] + ['']*(biggest_length-1)) # Ajustar número de comas vacías
        writer_start = i*len(header_cpu_configuration)
        writer_end = int((i+1)*len(header_cpu_configuration)/2)
        writer.writerow(header_cpu_configuration[writer_start:writer_end] + ['']*(biggest_length-len(header_cpu_configuration)))
        writer.writerow(values_cpu_configuration[writer_start:writer_end] + ['']*(biggest_length-len(values_cpu_configuration)))

        writer.writerow(['Total'] + ['']*(biggest_length-1))
        writer_start = int(i*len(header_cpu_total_stats))
        writer_end = int((i+1)*len(header_cpu_total_stats)/2)+1
        writer.writerow(header_cpu_total_stats[writer_start:writer_end] + ['']*(biggest_length-len(header_cpu_total_stats)))
        writer.writerow(values_cpu_total_stats[writer_start:writer_end] + ['']*(biggest_length-len(values_cpu_total_stats)))

        writer.writerow(['Region of interest'] + ['']*(biggest_length-1))
        writer.writerow(header_cpu_interest_stats + ['']*(biggest_length-len(header_cpu_interest_stats)))
        writer.writerow(values_cpu_interest_stats + ['']*(biggest_length-len(values_cpu_interest_stats)))

        writer.writerow(['Branch prediction'] + ['']*(biggest_length-1))
        writer.writerow(header_cpu_branch_stats + ['']*(biggest_length-len(header_cpu_branch_stats)))
        writer.writerow(values_cpu_branch_stats + ['']*(biggest_length-len(values_cpu_branch_stats)))

    writer.writerow(['DRAM Stats'])
    for i in range(0, number_of_DRAM_channels, 1):
        writer.writerow(['Channel ' + str(i)] + ['']*(biggest_length-1))
        writer_start = int(i*len(header_DRAM_stats))
        writer_end = int((i+1)*len(header_DRAM_stats)/2)+1
        writer.writerow(header_DRAM_stats + ['']*(biggest_length-len(header_DRAM_stats)))
        writer.writerow(values_DRAM_stats + ['']*(biggest_length-len(values_DRAM_stats)))


# Arreglar las entradas de tiempo de simulación en el CSV
# Utilizar las listas faltantes en el CSV