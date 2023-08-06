## About The Code

This is a part of the project that we are working on it for the Cyber-Physical Group (i6) at the Technical University of Munich. In this part, we develop a script extractor to gather the information such as abstract, author(s), supervisor(s), advisor(s), date of submission, etc.

## How to install

You can install it by running the following line in your terminal:
```
pip install Extraction-CPS
```

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
```Python
from Extract_info import Extract
directory = "D:\CPS\HiWiProjects\Parse\data\mnt\current" #This is a sample directory. You have to change it to your desired directory.
# Note: if your subdirectory is started with a number, you must write it as below:
# directory = "D:\CPS\HiWiProjects\Parse\data\mnt\current\\2014"
format = "tex" #For now, the code can extract the information from LaTeX(.tex) and Text(.txt) files.
E = Extract.Extraction(directory, format)
All_information = E.Extract_all_together() #This line will give you the information if the authors and abstract are not empty.
Only_Abstracts = E.Extract_Abstract() #This will give you the English and German version of the abstract. The German version may be empty.
Only_Authors = E.Extract_Authors()
Only_Titles_en = E.Extract_Title_en() #English titles
Only_Titles_de = E.Extract_Title_de() #German titles
Only_Dates = E.Extract_Date()
Only_Supervisors = E.Extract_Supervisor()
Only_Advisors = E.Extract_Advisor()
Only_ThesisTypes = E.Extract_ThesisType()

```