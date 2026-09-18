from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

#Load Model
model = joblib.load("house_model.pkl")

@app.route("/")

def home():
    return "House price prediction API"

@app.route("/predict", methods=["post"])
def predict():
    data = request.json
    size = data["size"]
    prediction = model.predict([[size]])

    return jsonify(
        {
            "house_size" : size,
            "predicted_price" : float(prediction[0])
        }
    )

if __name__ == "__main__":
    app.run(port=5000, debug=True)