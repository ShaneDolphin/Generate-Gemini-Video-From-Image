#!/usr/bin/env python3
"""
Google Gemini Video Generation Script
Generates a video from an image using Google's Veo model via Gemini API
"""

import os
import time
import requests
import json
import base64
from pathlib import Path

def upload_file_to_gemini(api_key, file_path):
    """Upload file to Gemini and return file URI"""
    upload_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"

    # Get file info
    file_name = Path(file_path).name
    file_size = os.path.getsize(file_path)

    # Initial upload request
    headers = {
        'X-Goog-Upload-Protocol': 'resumable',
        'X-Goog-Upload-Command': 'start',
        'X-Goog-Upload-Header-Content-Length': str(file_size),
        'X-Goog-Upload-Header-Content-Type': 'image/png',
        'Content-Type': 'application/json'
    }

    metadata = {
        'file': {
            'display_name': file_name
        }
    }

    response = requests.post(upload_url, headers=headers, json=metadata)
    if response.status_code != 200:
        raise Exception(f"Failed to start upload: {response.text}")

    upload_uri = response.headers['X-Goog-Upload-URL']

    # Upload file content
    with open(file_path, 'rb') as f:
        file_data = f.read()

    upload_headers = {
        'Content-Length': str(file_size),
        'X-Goog-Upload-Offset': '0',
        'X-Goog-Upload-Command': 'upload, finalize'
    }

    response = requests.post(upload_uri, headers=upload_headers, data=file_data)
    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.text}")

    file_info = response.json()
    return file_info['file']['uri']

def encode_image_to_base64(image_path):
    """Encode image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_video(api_key, image_path, prompt):
    """Generate video using Veo model via Gemini API"""
    # Use the Veo video generation endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate-001:predictLongRunning"

    # Encode image to base64
    image_base64 = encode_image_to_base64(image_path)

    payload = {
        "instances": [
            {
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_base64,
                    "mimeType": "image/png"
                }
            }
        ],
        "parameters": {
            "resolution": "1080p",        # Options: "720p", "1080p"
            "aspectRatio": "16:9",        # Options: "16:9", "9:16", "1:1"
            "includeAudio": false,        # Options: true, false
            # Additional parameters you can add:
            # "duration": 5,              # Video length in seconds (1-10)
            # "fps": 24,                  # Frames per second (24, 30, 60)
            # "style": "realistic",       # Style options: "realistic", "animated", "cinematic"
            # "motionIntensity": "medium" # Motion level: "low", "medium", "high"
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }

    response = requests.post(url, headers=headers, json=payload)

    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Failed to start video generation (status {response.status_code}): {response.text}")

    return response.json()

def poll_video_generation(api_key, operation_name):
    """Poll the video generation operation until complete"""
    url = f"https://generativelanguage.googleapis.com/v1alpha/{operation_name}?key={api_key}"

    while True:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to poll operation: {response.text}")

        result = response.json()

        if result.get('done', False):
            return result

        print("Video generation in progress...")
        time.sleep(10)  # Wait 10 seconds before polling again

def main():
    # Configuration
    api_key = "yourGoogleGeminiAPIkeywillgohere"
    image_path = "/path/to/file/yourimage.png"
    prompt = "This is a video of an attractive woman putting a bunch of mustard packets in her mouth and then chewing really slowly"

    try:
        print("Starting video generation...")
        operation_result = generate_video(api_key, image_path, prompt)

        # Extract operation name from the response
        operation_name = operation_result.get('name')
        if not operation_name:
            raise Exception("No operation name returned from video generation")

        print(f"Video generation started. Operation: {operation_name}")
        print("Polling for completion... (this may take several minutes)")

        # Poll until the operation is complete
        final_result = poll_video_generation(api_key, operation_name)

        # Save the result
        output_file = "generated_video_response.json"
        with open(output_file, 'w') as f:
            json.dump(final_result, f, indent=2)

        print(f"Video generation completed! Response saved to {output_file}")

        # Extract and download the video
        if 'response' in final_result and 'generateVideoResponse' in final_result['response']:
            generated_samples = final_result['response']['generateVideoResponse'].get('generatedSamples', [])
            if generated_samples:
                video_uri = generated_samples[0].get('video', {}).get('uri')
                if video_uri:
                    print(f"Video URI found: {video_uri}")
                    print("Downloading video...")

                    # Download the video from the URI
                    video_response = requests.get(f"{video_uri}&key={api_key}")
                    if video_response.status_code == 200:
                        with open("generated_video.mp4", "wb") as f:
                            f.write(video_response.content)
                        print("Video saved as generated_video.mp4")
                    else:
                        print(f"Failed to download video: {video_response.status_code}")
                else:
                    print("No video URI found in response")
            else:
                print("No generated samples found in response")
        else:
            print("Unexpected response format")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())