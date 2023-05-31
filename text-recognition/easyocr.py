import easyocr
reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
result = reader.readtext('chinese.jpg')

# the output will be in a list format
# each item represents a bounding box,
# the text detected and confident level, respectively.

print("result",result)

# Note 1: ['ch_sim','en'] is the list of languages you want to read. 
# You can pass several languages at once but not all languages can be used together. 
# English is compatible with every language and languages that share common characters are usually compatible with each other.

# Note 2: Instead of the filepath chinese.jpg, 
# you can also pass an OpenCV image object (numpy array) or an image file as bytes. 
# A URL to a raw image is also acceptable.

# Note 3: The line reader = easyocr.Reader(['ch_sim','en']) is for loading a model into memory. 
# It takes some time but it needs to be run only once.

# You can also set detail=0 for simpler output.

reader.readtext('chinese.jpg', detail = 0)