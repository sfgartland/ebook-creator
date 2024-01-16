import os
import glob
import typer
from typing_extensions import Annotated
from rich import print # Nicer printing
from rich.markup import escape
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import PromptBase, InvalidResponse

from natsort import natsorted # For better sorting of filenames

from pagerange import PageRange # Easier handling of ordering of what to merge

class PagePromt(PromptBase[PageRange]):
    """
    Promt that returns a PageRange object
    """

    validate_error_message = "[prompt.invalid]Please enter a valid input (e.g. \"1,3,10-15\")"

    def process_response(self, value: str) -> PageRange:
        try:
            return PageRange(value)
        except:
            raise InvalidResponse(self.validate_error_message)


def main(files: Annotated[list[str], typer.Option(prompt="Input files")], outputfile: Annotated[str, typer.Option(prompt="Output file")], tempoutput: str="merged.pdf", acceptfiles: bool=None, fileorder: str=None):
    # files = glob.glob("Warren_*.pdf")
    # outputFile = "Warren_Handouts MERGED.pdf"
    # tempOutput = "merged.pdf"
    files = natsorted(files) # Sort files into better order

    # Ask if the files are the correct ones
    if not acceptfiles==None:
        print(files)
        acceptfiles = typer.confirm("Are these the files you want to merge?")
        if not acceptfiles:
            print("[bold red]Exiting[/bold red] as the files are wrong!")
            return 
        
    def printFilesInOrder():
        for i in fileorder.pages:
            print(f"{escape(str(i))}:\t{escape(files[i-1])}")

    # If no order is given, ask if user want's to change them, if it is all, then just use the `natsorted` order
    if fileorder == "all":
        fileorder=PageRange(list(range(1,len(files)+1)))
    else:
        fileorder=PageRange(list(range(1,len(files)+1)))
        printFilesInOrder()
        fileorder = PageRange(PagePromt.ask("Order for merging(e.g. \"1,3,10-15\"", default=fileorder.range))

    files = list(map(lambda x: files[x-1], fileorder.pages))

    print(f"[b u]Proceeding to merge the following files[/b u]")
    printFilesInOrder()

    inputArgs = ' '.join(list(map(lambda x: f"--input-file \"{x}\"", files)))
    command = f"pdfsak {inputArgs} --output {tempoutput}"


    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Preparatory Cleanup
        if(os.path.isfile(tempoutput)):
            os.remove(tempoutput)
            print(":white_check_mark:Deleted temp output file")

        # Do the merging
        progress.add_task(description="Merging files.... (This will take some time)", total=None)
        os.system(command) #Merge the files
        print(":white_check_mark:[green]Successfully[/green] merged pdf files!")

        # Moving around files
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        os.rename(tempoutput, outputfile)
        if os.path.isfile(tempoutput):
            print("[red]Something went wrong[/red]")
        if os.path.isfile(outputfile):
            print(":white_check_mark:[green]Successfully[/green] replaced output file with the newly merged file!")

    

if __name__ == "__main__":
    typer.run(main)

    