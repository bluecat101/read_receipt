# import io
import os
# import re  # 正規表現

# # Imports the Google Cloud client library
# from google.cloud import vision

# # Instantiates a client
# client = vision.ImageAnnotatorClient()

# # The name of the image file to annotate
# file_name = os.path.abspath('ion.jpg')

# # Loads the image into memory
# with io.open(file_name, 'rb') as image_file:
#     content = image_file.read()

# image = vision.Image(content=content)

# # Performs label detection on the image file
# response =  client.document_text_detection(
#         image=image,
#         image_context={'language_hints': ['ja']}
#     )

# # レスポンスからテキストデータを抽出
# # print(response)
# # print("--")
# # print(response.full_text_annotation)


# # 取得する情報----
# ## date(year,month,day)
# ## total
# ## each item
# ## each price
# ## each discount
# ## 
# # ----


# paragraph=''

# output_text = ''
# for page in response.full_text_annotation.pages:
#   for block in page.blocks:
#     for paragraph in block.paragraphs:
#       for word in paragraph.words:
#         output_text += ''.join([
#           symbol.text for symbol in word.symbols
#         ])
#         paragraph += ''.join([
#           symbol.text for symbol in word.symbols
#         ])
#       output_text += '\n'
#       if paragraph
#       paragraph=''
# print(output_text)
path =os.path.abspath('ion.jpg')
"""Detects text in the file."""
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()
with io.open(path, 'rb') as image_file:
    content = image_file.read()
image = vision.Image(content=content)
response = client.text_detection(image=image)
texts = response.text_annotations
print('Texts:')
for text in texts:
    print('\n"{}"'.format(text.description))
    vertices = (['({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices])
    print('bounds: {}'.format(','.join(vertices)))
if response.error.message:
    raise Exception(
        '{}\nFor more info on error messages, check: '
        'https://cloud.google.com/apis/design/errors'.format(
            response.error.message))