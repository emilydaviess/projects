import pytesseract
import cv2
from PIL import Image
import pandas
import numpy
from google.cloud import vision
import io
import datetime
import os
import re
from dateutil import parser

class Ticket(object):

    def __init__(self, ticket_name):
        name = "Tickets and Invoices for Text Recognition"
        self.ticket_name = ticket_name
    
    # set a dictionary with the fields we need to look for on the ticket/invoice to identify which values we need to pull
    ticket_fields = {
        "date": ["Notes",2],
        "time": ["Notes",4],
        "supplier": ["Customer / Supplier",1],
        "haulier": ["Haulier",1],
        "ref_num": ["Ref. No.",1],
        "ticket_number": ["DELIVERY TICKET No.",1],
        "desc_of_goods": ["Description of Goods",1],
        "waste_code": ["Waste Code",1],
        "permit_number": ["NUMBER:",1],
        "lorry_reg": ["Notes",1],
        "weight": ["Notes",5]
    }

    def apply_brightness_contrast(self, brightness = 0, contrast = 0):
        img = cv2.imread(self.ticket_name)
        img = cv2.resize(img, (2500,2500), 0, 0, cv2.INTER_AREA)

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow
            
            enhanced_img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)
        else:
            enhanced_img = img.copy()
        
        if contrast != 0:
            f = 131*(contrast + 127)/(127*(131-contrast))
            alpha_c = f
            gamma_c = 127*(1-f)
            
            enhanced_img = cv2.addWeighted(enhanced_img, alpha_c, enhanced_img, 0, gamma_c)
        
        img_results = numpy.hstack((img, enhanced_img))
        cv2.imshow("img_results",img_results)
        cv2.waitKey(500)

        return enhanced_img

    def detect_document(self):
        '''  ----------------------------------------------------------------------------------------------------------
        This function accesses GOOGLE's vision API, uses their OCR deep learning software to analyse an image and 
        detect any handwriting present. A string is then cleaned and returned. The argument here is simply the path of ticket (ticket_name)
        to the image which you would like to analyse in PNG format
        ---------------------------------------------------------------------------------------------------------- '''

        brightness = -85
        contrast = 70
        img_file_name = "enhanced_img.jpg"

        # convert img to grey-scale for easier reading
        img = self.apply_brightness_contrast(brightness=brightness, contrast=contrast)
        image_data = Image.fromarray(img) # formulate an image from an array
        image_data.save(img_file_name) # save enhanced_image

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="key.json"
        """Detects document features in an image."""
        client = vision.ImageAnnotatorClient()

        with io.open(img_file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        full_text = response.full_text_annotation.text
        
        # Retrieves the text annotations from the response
        text_annotations = response.text_annotations
        print("---------------------------------")
        # prints the detected text (and combinations of) - this may be what we want to use for finding things such as Haulage
        annotation_array = []
        for text in text_annotations:
            annotation_array.append(text.description)
            #print(text.description)

        # the first element in the array contains everything we need however we need to split them out into separate elements by /n (new line)
        annotation_array = annotation_array[0]
        annotation_array = annotation_array.splitlines()
        print("annotation_array",annotation_array)
        ticket_values_df = pandas.DataFrame(columns=['date','time','supplier','haulier','ref_num','ticket_number','desc_of_goods','waste_code','permit_number','lorry_reg','weight'])
        for field in self.ticket_fields:
            # self.ticket_fields [0] = value/field to look for in invoice
            # self.ticket_fields [1] = n - number of elements to look from value to get the result
            
            # for now, look for the date/timestamp like this as there is nothing on the ticket which makes it easy to identify a date. i'd like to strip this out eventually and use lookups like in the dictionary i.e. Haulier
            if field in ['date','time', 'weight', 'lorry_reg']:
                # look through values in array and look for the element which looks like a date
                for annotation in annotation_array:
                    # timestamp
                    if field == 'time':
                        try:
                            datetime.datetime.strptime(annotation, "%H:%M").time()
                            result = annotation
                            ticket_values_df.at[0,field] = result
                        except:
                            pass
                    
                    # timestamp
                    if field == 'date':
                        try:
                            datetime.datetime.strptime(annotation, '%d-%m-%Y')
                            result = annotation
                            ticket_values_df.at[0,field] = result
                        except:
                            pass

                    # weight
                    if field == 'weight':
                        if " kg" in annotation:
                            result = annotation
                            ticket_values_df.at[0,field] = result

                    # lorry_reg
                    if field == 'lorry_reg':
                        #  define a regular expression pattern to match UK registration plates
                        pattern = r"^(?=.{1,7})(([a-zA-Z]?){1,3}(\d){1,3}([a-zA-Z]?){1,4})$"
                        if re.search(pattern, annotation):
                            result = annotation
                            ticket_values_df.at[0,field] = result

                continue

            value = self.ticket_fields[field][0]
            n = self.ticket_fields[field][1]
            result = self.pull_annotation_value(annotation_array,value,n)
            ticket_values_df.at[0,field] = result

        print(ticket_values_df)
        return ticket_values_df

    def pull_annotation_value(self,annotation_array,field,n):
        # search for the item we're looking for i.e. Haulier and then pull the next value in the array to get the value of annotation
        annotation_value = annotation_array[(annotation_array.index(field))+n]
        return annotation_value
            
first_ticket = Ticket('images/38_I0.jpg')
full_text = first_ticket.detect_document()


