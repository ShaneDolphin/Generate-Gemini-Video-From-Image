# Video Generation Script

This script uses Google's Veo model via the Gemini API to generate videos from a starting image and text prompt.

## Setup

### 1. Change the API Key

Edit line 124 in `generate_video.py` to use your own Google Gemini API key:

```python
api_key = "YOUR_API_KEY_HERE"
```

Replace `"yourGoogleGeminiAPIkeywillgohere"` with your actual API key from the Google AI Studio.

### 2. Change the Starter Image Path

Edit line 125 to point to your image file:

```python
image_path = "/path/to/your/image.png"
```

The script currently supports PNG images. Make sure your image exists at the specified path.

### 3. Customize the Prompt

Edit line 126 to describe how you want your video to look:

```python
prompt = "Your custom video description here"
```

Be descriptive about the motion, actions, or changes you want to see in the generated video.

### 4. Change Output Video Name

To change the output video filename, edit line 162:

```python
with open("your_custom_name.mp4", "wb") as f:
```

Replace `"generated_video.mp4"` with your desired filename.

## Additional Parameters (Currently Commented Out)

The script includes several parameters that can be customized in the `payload` section (lines 83-87):

```python
"parameters": {
    "resolution": "1080p",        # Options: "720p", "1080p"
    "aspectRatio": "16:9",        # Options: "16:9", "9:16", "1:1"
    "generateAudio": "false",     # Options: Accepted values are "true" or "false"
    "durationSeconds": "8",       # Accepted values are "4", "6" or "8"
}
```

To enable any of these parameters, uncomment the lines and adjust the values as needed.

## Usage

1. Install required dependencies:
   ```bash
   pip install requests
   ```

2. Run the script:
   ```bash
   python3 generate_video.py
   ```

The script will:
1. Upload your image to Google's servers
2. Start the video generation process
3. Poll for completion (this can take several minutes)
4. Download the generated video when ready
5. Save the video as an MP4 file

## Output Files

- `generated_video.mp4` - The generated video file
- `generated_video_response.json` - Full API response with metadata

## Notes

- Video generation can take 5-15 minutes depending on complexity
- The script will show progress updates while waiting
- Make sure you have sufficient API quota for video generation
- Large images may take longer to process