import os
import re

lastoutput = None


def getLO():
    global lastoutput
    return lastoutput

def setLO(LO):
    global lastoutput
    lastoutput = LO
    print("Last output: "+lastoutput)
    return lastoutput


def getFile(default=None):
    if default == None:
        default = getLO()

    if default and os.path.isfile(default):
        return default
    else:
        print("Couldn't find the default file...")
        files = [k for k in os.listdir() if '.pdf' in k]
        for i,file in enumerate(files):
            print(str(i+1)+": "+file)
        selected = input("What file do you want to use: ")
        return setLO(files[int(selected)-1])

def escapeFileString(path):
    return path
    #This doesn't work now, it does nothing

def merge():
    print("===================================")
    print("Merging Images")
    print("===================================")
    os.system("magick convert *.{tif,png} merged.pdf")
    setLO("merged.pdf")

def ocr(language="eng", pages=None):
    print("===================================")
    print("OCR")
    print("language="+str(language))
    print("===================================")

    pagesString = "--pages "+pages if pages else ""


    os.system("ocrmypdf "+escapeFileString(getFile())+" ocr.pdf -l "+language+" --force-ocr "+pagesString)
    setLO("ocr.pdf")

def changePage(startpage=None, style="arabic"):
    print("===================================")
    print("Changing pages")
    print("startpage="+str(startpage))
    print("style="+str(style))
    print("===================================")

    file = getFile()

    if not startpage:
        os.startfile(file)
        startpage = input("Start page: ")
    os.system("python3 -m pagelabels --type \""+style+"\" --startpage 1 --firstpagenum "+startpage+" "+escapeFileString(file))
    # No need to set last output since it is the same


def bookmark():
    print("===================================")
    print("Bookmarking")
    print("===================================")
    file = getFile()
    os.startfile(file)
    # Creates file if it is not there
    if not os.path.isfile("bookmarks.txt"):
        with open("bookmarks.txt", "w") as file:
            pass
    os.startfile("bookmarks.txt")
    input("Press any key after editing bookmarks.txt")
    genBookmarkFile()
    updatePDFMetadata(file)
    
def dumpMetadata(pdfFile, outFile="pdftkdumped-metadata.txt"):
    print("Extracting metadata, this may take a few minutes!")
    os.system("pdftk "+escapeFileString(pdfFile)+" dump_data_utf8 output "+outFile)

def updatePDFMetadata(pdfFile, bookmarkFile="pdftkbookmarks.txt"):
    os.system("pdftk "+escapeFileString(pdfFile)+" update_info_utf8 "+escapeFileString(bookmarkFile)+" output final.pdf")
    setLO("final.pdf")

def genBookmarkFile():
    lines = open("bookmarks.txt", "r", encoding='utf-8').readlines()
    with open("pdftkbookmarks.txt", "w", encoding='utf8') as out:
        for line in lines:
            title = re.sub("^\s*", "",re.findall("^\s*.+(?=\s\d)", line)[0])
            #Try without this replacement since I discovered update_info_utf8
            #for word, initial in {"ø":"o", "æ":"ae", "å":"aa"}.items():
            #    title = title.replace(word.lower(), initial.lower())
            #    title = title.replace(word.upper(), initial.upper())
            pagenum = re.findall("[0-9]+$", line)[0]
            headinglevel = len(re.findall("^\s*", line)[0])+1
            print(title + " " + pagenum)
            out.writelines(["\nBookmarkBegin", "\nBookmarkTitle: "+title, "\nBookmarkLevel: "+str(headinglevel), "\nBookmarkPageNumber: "+str(pagenum)])

# This is used internally so that we can separate extraction with and without bookmarks
def extractPagesFromFile(file, pagerange):
    os.system("pdfsak --extract-pages "+str(pagerange[0])+"-"+str(pagerange[1])+" -if \""+escapeFileString(file)+"\" -o extractedpages.pdf --overwrite")
    setLO("extractedpages.pdf")

def extractPagesWithoutBookmarks():
    print("===================================")
    print("Extracting Pages WITHOUT Bookmarks")
    print("===================================")
    file = getFile()
    pagerange = handleExtractionInput()
    extractPagesFromFile(file, pagerange)

def handleExtractionInput():
    pageoffset = input("Page offset (e.g. 50-70): ")
    pagerange = pageoffset.split("-")
    
    return pagerange

# TODO Fix it so that the bookmarks aren't applied to the whole file
def extractPagesWithBookmarks(withoutBookmarks):
    print("===================================")
    print("Extracting Pages With Bookmarks")
    print("===================================")
    file = getFile()
    pagerange = handleExtractionInput()
    extractPagesFromFile(file, pagerange)

    dumpMetadata(file)
    with open("pdftkdumped-metadata.txt", "r",encoding='utf8') as dumpedFile:
        filecontent = dumpedFile.read()
        regex = "(BookmarkBegin)\n(BookmarkTitle:\s)(.+)\n(BookmarkLevel:\s)(\d+)\n(BookmarkPageNumber: )(\d+)"
        
        allBookmarks = re.findall(regex, filecontent)
        # Checks all bookmarks, to see if they are in range
        with open("pdftksplitbookmarks.txt", "w", encoding='utf8') as newfile:
            for bookmark in allBookmarks:
                # the page number of bookmark is in the 7th capturegroup
                if int(pagerange[0]) <= int(bookmark[6]) <= int(pagerange[1]):
                    newfile.write(bookmark[0]+"\n")
                    newfile.write(bookmark[1]+bookmark[2]+"\n")
                    newfile.write(bookmark[3]+bookmark[4]+"\n")
                    newfile.write(bookmark[5]+str(int(bookmark[6])-int(pagerange[0])+1)+"\n")
        updatePDFMetadata(getFile(), "pdftksplitbookmarks.txt")
    # Do the page offsetting, save the file, then apply bookmarks using function

def splitPDFtoPNG():
    print("===================================")
    print("Splitting PDF to PNG")
    print("===================================")
    os.system("pdftoppm -png "+escapeFileString(getFile())+" in")

def clearPageLabels():
    file = getFile()
    dumpMetadata(file)

    with open("pdftkdumped-metadata.txt", "r",encoding='utf8') as dumpedFile:
        filecontent = dumpedFile.read()
        regex = "PageLabelBegin\n.+\n.+\n.+\nPageLabelNumStyle.+"
        
        withoutPageLabels = re.sub(regex, "", filecontent)
        # Checks all bookmarks, to see if they are in range
        with open("pdftksplitbookmarks.txt", "w", encoding='utf8') as newfile:
            newfile.write(withoutPageLabels)
        updatePDFMetadata(file, "pdftksplitbookmarks.txt")

def manualEditMetadata():
    file = getFile()
    print("Extracting metadata, this may take a few minutes!")
    dumpMetadata(file)
    input("Press ENTER after editing metadata file!")
    updatePDFMetadata(file, "pdftkdumped-metadata.txt")


def openCurrentFile():
    os.startfile(getFile())

def renameCurrentFile():
    if not getLO():
        print("There needs to be a selected file to rename. Currently there is no 'current file'!")
        print("Please select one!")
        getFile()

    newName = input("New name: ")
    split = os.path.splitext(newName)
    if split[1] == "":
        newName = newName+".pdf"
    print(f"Renaming '{getLO()}' to '{newName}'!")
    os.rename(getLO(), newName)


## parses steps and their options
def parseStepOptions(step):
    regex = "^([\d\w]+)(\((.+)\))?"
    parseString = re.findall(regex, step)
    if len(parseString) != 1:
        raise Exception("One of the steps didn't match the correct format")

    parseString = parseString[0]

    # Parse options if any
    options = {}
    if parseString[2] != '':
        options = parseString[2].split(";")
        for i, option in enumerate(options):
            options[i] = tuple(option.split("="))
        options = dict(options)
  

    return {
        "step": parseString[0],
        "options": options
    }

functionmap = {
    "1": ["merge", merge],
    "2": ["OCR(language=eng,pages=all)", ocr],
    "3": ["Change Pages(style=arabic;startpage)", changePage],
    "4": ["Bookmark", bookmark],
    "ex": ["Extract pages and bookmarks", extractPagesWithBookmarks],
    "exwb": ["Extract pages without bookmarks (way faster)", extractPagesWithoutBookmarks],
    "spl": ["Split PDF to PNG", splitPDFtoPNG],
    "clr": ["Remove all page labels", clearPageLabels],
    "editmeta": ["Manually edit metadata", manualEditMetadata],
    "o": ["Open current file", openCurrentFile],
    "rn": ["Rename Output", renameCurrentFile]
}



def UI():
    for key, item in functionmap.items():
        print(key+": "+item[0])

    steps = input("Order of steps(default 1,2,3,4): ").split(",")

    # If no input there will be a default order of steps, merging .tif files into a ocr'd, pagecorrected, and bookmarked file
    if steps == ['']:
        steps=["1", "2", "3", "4"]

    for i,step in enumerate(steps):
        steps[i] = parseStepOptions(step)

    for step in steps:
        print(step)
        functionmap[step["step"]][1](**step["options"])

    input("DONE... Press key to exit!")


UI()