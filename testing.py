import time
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.0-generate-preview",
    prompt="A cinematic shot of a majestic lion in the savannah.",
    config=types.GenerateVideosConfig(negative_prompt="cartoon, drawing, low quality"),
)

# Poll the operation status until the video is ready
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("parameters_example.mp4")
print("Generated video saved to parameters_example.mp4")
