import cv2
import numpy as np

# Open a typical 24 bit color image. For this kind of image there are
# 8 bits (0 to 255) per color channel
img = cv2.imread('images/3_I0.jpg')  # mandrill reference image from USC SIPI
s = 2500
img = cv2.resize(img, (s,s), 0, 0, cv2.INTER_AREA)
# cv2.imshow("img",img)
# cv2.waitKey(1000)

def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

font = cv2.FONT_HERSHEY_SIMPLEX
fcolor = (0,0,0)

blist = [0, -85, -100] # list of brightness values
clist = [0, 60, 35] # list of contrast values

out = np.zeros((s*2, s*3, 3), dtype = np.uint8)

for i, b in enumerate(blist):
    c = clist[i]
    print('b, c:  ', b,', ',c)
    row = s*int(i/3)
    col = s*(i%3)
    
    print('row, col:   ', row, ', ', col)
    
    out[row:row+s, col:col+s] = apply_brightness_contrast(img, b, c)
    msg = 'b %d' % b
    cv2.putText(out,msg,(col,row+s-22), font, .7, fcolor,1,cv2.LINE_AA)
    msg = 'c %d' % c
    cv2.putText(out,msg,(col,row+s-4), font, .7, fcolor,1,cv2.LINE_AA)
    
    cv2.putText(out, 'OpenCV',(260,30), font, 1.0, fcolor,2,cv2.LINE_AA)

cv2.imwrite('out.png', out)



def convert_to_grey_scale(self):
    # to perform OCR on an image, its important to preprocess the image. 
    # the idea is to obtain a processed image where the text to extract is in black with the background in white. 
    # to do this, we can convert to grayscale, apply a slight Gaussian blur, then Otsu's threshold to obtain a binary image. 
    # from here, we can apply morphological operations to remove noise. 
    # finally we invert the image. We perform text extraction using the --psm 6 configuration option to assume a single uniform block of text.

    # grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread('images/3_I0.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blur = cv2.GaussianBlur(gray, (3,3), 0)

    # morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening

    cv2.imshow('opening', opening)
    cv2.waitKey(5000)
    cv2.imshow('invert', invert)
    cv2.waitKey(5000)
    
    return opening

def convert_lab_colour_space(self):
    # lAB color space expresses color variations across three channels. 
    # one channel for brightness and two channels for color:
    # L-channel: representing lightness in the image
    # a-channel: representing change in color between red and green
    # b-channel: representing change in color between yellow and blue

    image = cv2.imread('images/3_I0.jpg')
    # converting to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # applying CLAHE to L-channel
    # feel free to try different values for the limit:
    clahe = cv2.createCLAHE(clipLimit=1.5)
    cl = clahe.apply(l_channel)

    # merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl,a,b))

    # converting image from LAB Color model to BGR color spcae
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # stacking the original image with the enhanced image
    result = np.hstack((image, enhanced_img))
    cv2.imshow("result",cl)
    cv2.waitKey(3000)
    
    return enhanced_img
