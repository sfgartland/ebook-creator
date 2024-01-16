import os

inputfile = "Aristotle et al_1996_Aristotle.pdf"

pageRanges = [
    "55-55",
    "37-41",
    "215-220",
    "222-226",
    "235-236",
    "238-244",
    "247-260",
    "266-282",
    "20-27",
    "61-81",
    "123-131",
    "83-86",
    "206-213"
]

def genCom(pagerange, output):
    return f'python "C:\\Users\\sfgar\\programing\\ebook-creator\\merge-and-ocr typer.py" exwb --file "{inputfile}" --pagerange "{pagerange}" --output "{output}"'

for i,pagerange in enumerate(pageRanges):
    com = genCom(pagerange,f"aristotle-{str(i+1)}.pdf")
    os.system(com)