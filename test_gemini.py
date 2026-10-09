import google.generativeai as genai

genai.configure(
    api_key="AQ.Ab8RN6J8MhmruPZG_MykFFA6grwKN95Vc9LX0vmcgeeBYEzUow"
)

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content("Say hello")

print(response.text)