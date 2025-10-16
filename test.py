from openai import OpenAI


inst = OpenAI(
    api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDUyMTdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.c4CaWrA49GhabtUadSEbFCvXT5dB_DqFr8tRxY3gcG8",
    base_url="https://aipipe.org/openai/v1",
)

instance = inst.chat.completions.create(
    model="gpt-4", messages=[{"role": "user", "content": "Hello!"}]
)

print(instance.choices[0].message)
