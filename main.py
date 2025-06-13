import os
import asyncio
import json
import re
from ollama import chat, ChatResponse, GenerateResponse, Client

client = Client(
    host = "http://192.168.68.84:11434"
)

to_process_path = r"To Process"

async def process_image(image_path):
    response: GenerateResponse = client.generate(
        model="gemma3:27b",
        images=[image_path],
        prompt="Use the provided image to generate a recipe. Expect the name \"Nana\" to be used. Return the recipe following this JSON format: {\"title\": \"Recipe Title\", \"author\": \"Author (if applicable)\", \"ingredients\": [\"Ingredient 1\", \"Ingredient 2\"], \"instructions\": \"Step by step instructions.\", \"notes\": \"Any additional notes.\"} Make sure to provide *only* the JSON, nothing extra.",
        format="json",
        stream=False
    )

    try:
        data = json.loads(response.response)
        print(f"Processed {image_path}: {data}")
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", data['title'])
        os.makedirs("./processed", exist_ok=True)
        with open(f"./processed/{safe_title}.json", "w") as json_file:
            json.dump(data, json_file, indent=2)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from {image_path}: {e}")
        print(f"Response: {response.response}")

async def main():
    for filename in os.listdir(to_process_path):
        if filename.endswith(".JPEG") or filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(to_process_path, filename)
            print(f"Processing \"{image_path}\"...")
            await process_image(image_path)

if __name__ == "__main__":
    asyncio.run(main())