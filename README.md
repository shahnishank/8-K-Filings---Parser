# 8-K-Filings---Parser

# Parser for EPS Extraction from 8-K Filings

**Overview**

The provided parser script built in Python extracts the values for Earnings Per Share (EPS) from a set of 8-K filings presented in a .html format. This script utilizes the BeautifulSoup library and regular expressions for text processing. The extracted EPS values are then subject to a set of considerations before being outputted into a .csv file alongside their corresponding file names.

**Code Summary**

1. Imports all the necessary libraries and modules, viz. os, csv, BeautifulSoup, re, Typing (to support type hints)

2. Functions:

   1. `extract_eps_value(text: str) -> Optional[float]`
       
       This function uses regular expressions to process and extract EPS values from the text, based on the patterns mentioned in the matching expressions. It is designed to cover multiple possible match patterns. You can see the constuction of some of the regex patterns that were used here.
       
       ```python
        # Code block for extract_eps_value function
       eps_patterns = [
        r"EPS\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Matching "EPS" followed by optional spaces. 
        r"Earnings\s*per\s*(?:common\s*)?share\s*(?:.*?)(-?\d+(?:\.\d+)?)(?:\s*(?:cents|cents\s*per\s*share))?", # Matching variations of "Earnings per share" or "Earnings per common share"
        r"Loss\s*per\s*(?:common\s*)?share\s*(?:.*?)(-?\d+(?:\.\d+)?)(?:\s*(?:cents|cents\s*per\s*share))?", # Matching variations like "Loss per share" or "Loss per common share"
        r"(?:earnings|diluted|basic|eps)\s*(?:per\s*(?:common\s*)?share)?\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Matching EPS variations such as "earnings per share" or "diluted EPS"
        r"(?:loss\s*per\s*share)\s*(?:.*?)(-?\d+(?:\.\d+)?)", # Match "loss per share" with optional trailing characters. 
        r"(?:EPS|Earnings\s*per\s*(?:common\s*)?share|Loss\s*per\s*(?:common\s*)?share)\s*(?:.*?)(-?\d+(?:\.\d+)?)" # Matching EPS variations such as "EPS" or "Earnings per common share" with optional preceding characters. 
       ]

       ```
       
   2. `parse_8k_files(directory: str) -> List[Tuple[str, float]]` 
   
       This function parses all the provided 8-K filings present in the specified directory, extracts the EPS values from each filing, and returns a list of tuples containing filenames and their corresponding EPS values.
       
      
       
   3. `write_to_csv(eps_values: Dict[str, float], output_file: str) -> None` 
   
       This function writes the EPS values to a .csv file. It takes in a dictionary containing the filenames as _keys_ and the corresponding EPS values as _values_.
       
     
       
   4. `prioritize_eps_values(eps_values: List[Tuple[str, float]]) -> Dict[str, float]` 
   
       This function implements the logic to put the extracted EPS values through a set of considerations provided by the user. It accepts a list of tuples containing the filenames and corresponding EPS values and returns a dictionary format where the keys are the filenames, and the values are the EPS values that pass the priority check. You can see the implementation of the prioritization logic here. 
       
       ```python
       # Code block for prioritize_eps_values function
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
       ```
       
   5. `main() -> None` 
   
       This function allows the script to be run. It specifies the directory path for the 8-K filings and the output .csv file path and controls the EPS extraction and subsequent writing functions.
       
       ```python
       # Code block for main function
       ```

**Process**

1. The script iterates through each HTML file that is present in the specified directory.
2. For each file, it extracts textual content using the BeautifulSoup library.
3. EPS values are extracted from the text using pattern matching with regular expressions.
4. Extracted EPS values are prioritized based on the provided set of considerations.
5. Finalized EPS values are written to a CSV file.

**User Input**

1. Provide the directory where the 8-K filings are stored.

2. Specify the path for the directory where the output .csv file needs to be stored.

**Additional Notes**

- While the regular expressions were designed to be as flexible as possible, there might be instances of an inaccurate value being matched as the EPS value due to the considerable variation in how the filings are written.

- While the script does include logic to handle negative values, it is not perfectly able to maintain the signage for some instances in the output file.
