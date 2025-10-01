# Scenario.com Image Generator

A simple Python application that generates images using the Scenario.com API. This app securely manages API credentials and provides both interactive and command-line interfaces for image generation.

## Features

- 🎨 Generate images from text prompts using Scenario.com API
- 🔐 Secure API key management with environment variables
- 📁 Automatic image downloading and organization
- 🖥️ Interactive CLI interface
- ⚡ Command-line script for quick generation
- 🛡️ Git-safe configuration (API keys are hidden)

## Setup

### 1. Clone or Download

If you haven't already, navigate to your project directory.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Scenario.com API Credentials

1. Sign up at [Scenario.com](https://scenario.com)
2. Go to your dashboard and find your API credentials
3. You'll need both an API Key and API Secret

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```env
   SCENARIO_API_KEY=your_actual_api_key_here
   SCENARIO_API_SECRET=your_actual_api_secret_here
   OUTPUT_DIR=generated_images
   ```

**Important**: The `.env` file is automatically hidden from Git to protect your API keys.

## Usage

### Interactive Mode

Run the main application for an interactive experience:

```bash
python image_generator.py
```

This will prompt you for:
- Image description/prompt
- Optional parameters (width, height, number of samples)

### Command Line Mode

For quick image generation:

```bash
python generate.py "a majestic lion in a grassy savanna, golden hour, photorealistic"
```

#### Command Line Options

```bash
python generate.py "your prompt" --width 1024 --height 1024 --samples 2 --steps 30 --guidance 4.0 --negative-prompt "blurry, low quality"
```

Available options:
- `--width`: Image width in pixels (default: 1024)
- `--height`: Image height in pixels (default: 1024)
- `--samples`: Number of images to generate (default: 1)
- `--steps`: Number of inference steps (default: 28)
- `--guidance`: Guidance scale for prompt adherence (default: 3.5)
- `--negative-prompt`: Things to avoid in the image

## Examples

### Basic Usage
```bash
python generate.py "a cute cat wearing a wizard hat"
```

### Advanced Usage
```bash
python generate.py "a futuristic cityscape at sunset" --width 1920 --height 1080 --samples 3 --negative-prompt "blurry, low resolution"
```

### Interactive Session
```bash
python image_generator.py
```
Then follow the prompts to enter your description and parameters.

## Output

Generated images are saved in the `generated_images/` directory (or the directory specified in your `.env` file) with timestamps:

```
generated_images/
├── generated_image_20241230_143022_1.png
├── generated_image_20241230_143022_2.png
└── ...
```

## Security Features

- ✅ API keys stored in `.env` file (hidden from Git)
- ✅ `.env` file is in `.gitignore`
- ✅ Example template (`.env.example`) provided for setup
- ✅ No hardcoded credentials in source code

## File Structure

```
webscrape/
├── .env.example          # Template for environment variables
├── .env                  # Your actual API keys (hidden from Git)
├── .gitignore           # Git ignore file
├── requirements.txt     # Python dependencies
├── image_generator.py   # Main application (interactive)
├── generate.py          # CLI script for quick generation
├── README.md           # This file
└── generated_images/   # Output directory for images
```

## Troubleshooting

### "API credentials not found" Error
- Make sure you've created a `.env` file
- Check that your API key and secret are correctly set in the `.env` file
- Ensure there are no extra spaces or quotes around the values

### "Job failed" Error
- Check your prompt for any restricted content
- Verify your Scenario.com account has sufficient credits
- Try reducing the image dimensions or number of samples

### Network Errors
- Check your internet connection
- Verify the Scenario.com API is accessible
- Try again after a few minutes (rate limiting)

## API Model Information

This app uses the `flux.1-dev` public model by default, which is a high-quality text-to-image model. You can modify the model in the code if you have access to other models in your Scenario.com account.

## Contributing

Feel free to submit issues or pull requests to improve this application!

## License

This project is open source. Please check Scenario.com's terms of service for API usage restrictions.
