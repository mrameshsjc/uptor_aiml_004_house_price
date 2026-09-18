import  requests

url = "http://127.0.0.1:5000"

output = requests.get(url)
print(output.status_code)
print(output.text)

url = "http://127.0.0.1:5000/predict"

data = {"size":3000}
response = requests.post(url, json=data)
print(response.status_code)
print(response.json())