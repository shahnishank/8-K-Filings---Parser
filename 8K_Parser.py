#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import csv
import re
from typing import List, Tuple, Dict, Optional

def extract_eps_value(text: str) -> Optional[float]:
    """Extract the Earnings Per Share (EPS) value from the given text.

    Args:
        text (str): The text to search for EPS values.

    Returns:
        Optional[float]: The EPS value found in the text, or None if no EPS value is found.
    """
    eps_patterns = [
        r"EPS\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Matching "EPS" followed by optional spaces. 
        r"Earnings\s*per\s*(?:common\s*)?share\s*(?:.*?)(-?\d+(?:\.\d+)?)(?:\s*(?:cents|cents\s*per\s*share))?", # Matching variations of "Earnings per share" or "Earnings per common share"
        r"Loss\s*per\s*(?:common\s*)?share\s*(?:.*?)(-?\d+(?:\.\d+)?)(?:\s*(?:cents|cents\s*per\s*share))?", # Matching variations like "Loss per share" or "Loss per common share"
        r"(?:earnings|diluted|basic|eps)\s*(?:per\s*(?:common\s*)?share)?\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Matching EPS variations such as "earnings per share" or "diluted EPS"
        r"(?:loss\s*per\s*share)\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Match "loss per share" with optional trailing characters. 
        r"(?:EPS|Earnings\s*per\s*(?:common\s*)?share|Loss\s*per\s*(?:common\s*)?share)\s*(?:.*?)(-?\d+(?:\.\d+)?)" # Matching EPS variations such as "EPS" or "Earnings per common share" with optional preceding characters. 
    ]

    positive_eps_values = []  # Storing positive EPS values
    negative_eps_values = []  # Storing negative EPS values
    for pattern in eps_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            eps_value = float(match.replace('(', '-').replace(')', ''))
            if eps_value >= 0:
                positive_eps_values.append(eps_value)
            else:
                negative_eps_values.append(eps_value)

    if positive_eps_values and negative_eps_values:
        min_positive_eps = min(positive_eps_values)
        max_negative_eps = max(negative_eps_values)
        if abs(min_positive_eps) < abs(max_negative_eps):
            return min_positive_eps
        else:
            return max_negative_eps
    elif positive_eps_values:
        return min(positive_eps_values)
    elif negative_eps_values:
        return max(negative_eps_values)
    else:
        return None

def parse_8k_files(directory: str) -> List[Tuple[str, float]]:
    """Parses all 8-K filings present in the passed directory and extracts EPS values.

    Args:
        directory(str): The directory path containing 8-K filing HTML files.

    Returns:
        List[Tuple[str, float]]: A list of tuples containing the filename and the extracted EPS value.
    """
    eps_values = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                from bs4 import BeautifulSoup
                text = BeautifulSoup(file, "html.parser").get_text()  # Extracting all the text from HTML file
                eps_value = extract_eps_value(text)  # Extracting EPS value from text
                if eps_value is not None:
                    eps_values.append((filename, eps_value))  # Appending the filename and EPS values to the list

    return eps_values

def write_to_csv(eps_values: Dict[str, float], output_file: str) -> None:
    """Writes EPS values to a .csv file.

    Args:
        eps_values (Dict[str, float]): A dictionary containing the filenames as keys and the corresponding EPS values as values.
        output_file (str): The path to the output CSV file.
    """
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "EPS"])  # Writing header row to .csv file
        for filename, eps_value in eps_values.items():
            # Formatting EPS value to maintain negative values' integrity
            if eps_value >= 0:
                writer.writerow([filename, f"{eps_value:.2f}"])  # Writing filenames and EPS values to .csv file
            else:
                writer.writerow([filename, f"({abs(eps_value):.2f})"])  # Write filename and EPS value to .csv file



def main() -> None:
    """Main function to run the EPS extraction and CSV writing process."""
    
    directory = "/temp//path/to/filings"  # Placeholder for the directory containing 8-K filing HTML files
    output_directory = "/temp/path/to/output" # Placeholder for the directory where the .csv file will bbe outputted. 
    output_file = os.path.join(output_directory, "output.csv")  # Outputting the .csv file at the location specified

    eps_values = parse_8k_files(directory)  # Parsing the provided 8-K filings and extract EPS values
    prioritized_eps_values = prioritize_eps_values(eps_values)  # Prioritizing the EPS values based on the provided considerations
    write_to_csv(prioritized_eps_values, output_file)  # Writing the resulting EPS values to a .csv file

def prioritize_eps_values(eps_values: List[Tuple[str, float]]) -> Dict[str, float]:
    """Prioritizes EPS values based on the considerations mentioned in the FAQs.

    Args:
        eps_values (List[Tuple[str, float]]): A list of tuples containing filenames and their corresponding EPS values.

    Returns:
        Dict[str, float]: A dictionary containing filenames as keys and their prioritized EPS values as values.
    """
    prioritized_eps = {}
    for filename, eps_value in eps_values:
        if filename not in prioritized_eps:
            prioritized_eps[filename] = eps_value
        else:
            current_value = prioritized_eps[filename]
            # Logic to prioritize basic EPS values over diluted EPS values
            if eps_value >= 0 and current_value < 0:
                prioritized_eps[filename] = eps_value
            elif abs(eps_value) < abs(current_value):
                prioritized_eps[filename] = eps_value
            # Logic to pick unadjusted EPS values over adjusted EPS values
            elif eps_value >= 0 and current_value >= 0:
                prioritized_eps[filename] = min(current_value, eps_value)
            # Checking for EPS values preceded by words like "net" or "total"
            elif any(pattern in str(eps_value).lower() for pattern in ["net eps", "total eps"]):
                prioritized_eps[filename] = eps_value
            # Logic to look for and pick "loss per share" patterns if no variation of "EPS" or "Earnings" is present
            elif eps_value < 0 and current_value >= 0:
                prioritized_eps[filename] = eps_value

    return prioritized_eps


if __name__ == "__main__":
    main()

