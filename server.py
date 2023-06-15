# from flask import Flask, request, jsonify
import pickle
import pytesseract 
from PIL import Image
import re

# app = Flask(__name__)

def to_raw(text):
  escape_char = ['\a', '\b', '\f', '\n', '\r', '\t', '\v']
  raw_char = ['\\a', '\\b', '\\f', '\\n', '\\r', '\\t', '\\v']
  for i in range(len(escape_char)):
    text = text.replace(escape_char[i], raw_char[i])
  return text

def read_text(img_path):
  with open(img_path, 'rb') as f:
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img) 
  return text

def clean_resume(text):
  text = re.sub('http\S+\s*', ' ', text)  # remove URLs
  text = re.sub('RT|cc', ' ', text)  # remove RT and cc
  text = re.sub('#\S+', '', text)  # remove hashtags
  text = re.sub('@\S+', '  ', text)  # remove mentions
  text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)  # remove punctuations
  text = re.sub(r'[^\x00-\x7f]',r' ', text) 
  text = re.sub('\s+', ' ', text)  # remove extra whitespace
  return text

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img_path = 'D:\Documents\Bootcamp and Course\Bangkit Academy\gawein_capstone_project\resume_Meyer.jpg'
# img_path = to_raw(img_path)
# text = read_text(img_path)
# data = clean_resume(text)
# print(data)

with open(r'D:\Documents\Bootcamp and Course\Bangkit Academy\gawein_capstone_project\model_pkl', 'rb') as f:
  model = pickle.load(f)

with open(r'D:\Documents\Bootcamp and Course\Bangkit Academy\gawein_capstone_project\vectorizer_pkl', 'rb') as f:
  vectorizer = pickle.load(f)

# @app.route('/api', methods=['POST'])
# def predict():
  # data = request.args.get('cv')
img_path = to_raw(img_path)
text = read_text(img_path)
data = clean_resume(text)

feature = vectorizer.transform([data])
prediction = model.predict(feature)[0]
print(prediction)
  # return jsonify({'result': prediction})

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)
