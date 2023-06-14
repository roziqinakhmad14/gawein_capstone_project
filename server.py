# import numpy as np
from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

with open('model_pkl', 'rb') as f:
  model = pickle.load(f)

with open('vectorizer_pkl', 'rb') as f:
  vectorizer = pickle.load(f)

@app.route('/api', methods=['POST'])
def predict():
  data = request.args.get('cv')
  feature = vectorizer.transform([data])
  prediction = model.predict(feature)[0]
  return jsonify({'result': prediction})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
