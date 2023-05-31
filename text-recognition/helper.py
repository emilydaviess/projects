# helper function file with functions
from PIL import Image
from PyPDF2 import PdfReader

# convert the PDFs into imagesf
def save_pdf_to_img(pdf_file_path): 
    reader = PdfReader(pdf_file_path)
    count = 0
    for page in reader.pages:
        count+=1
        for image in page.images:
            with open("images/"+str(count)+"_"+image.name, "wb") as fp:
                fp.write(image.data)

save_pdf_to_img('ticket1.pdf')




