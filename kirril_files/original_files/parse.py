"""
Method to parse de original_files of kirril traces
"""
import os

for name in os.listdir():
    if name.endswith(".txt"):
        problem_name = name.strip(".txt")
        with open(f"./{problem_name}.txt", "r", encoding="utf-8") as origin_f:
            all_lines = origin_f.readlines()
            autom_lines = all_lines[:-4]
            traces_lines = all_lines[-4:]
            with open(
                f"../automatons/{problem_name}.txt", "w", encoding="utf-8"
            ) as autom_f:
                for line in autom_lines:
                    autom_f.write(line)
            with open(
                f"../traces/{problem_name}.json", "w", encoding="utf-8"
            ) as traces_f:
                for line in traces_lines:
                    clean_line = line.replace("],]", "]]")
                    traces_f.write(clean_line)
