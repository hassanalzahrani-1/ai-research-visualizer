#!/usr/bin/env python3
"""
Simple CLI for Scenario.com Image Generation
Usage: python generate.py "your prompt here"
"""

import sys
import argparse
from image_generator import ScenarioImageGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate images using Scenario.com API')
    parser.add_argument('prompt', help='Text prompt for image generation')
    parser.add_argument('--width', type=int, default=1024, help='Image width (default: 1024)')
    parser.add_argument('--height', type=int, default=1024, help='Image height (default: 1024)')
    parser.add_argument('--samples', type=int, default=1, help='Number of images to generate (default: 1)')
    parser.add_argument('--steps', type=int, default=28, help='Number of inference steps (default: 28)')
    parser.add_argument('--guidance', type=float, default=3.5, help='Guidance scale (default: 3.5)')
    parser.add_argument('--negative-prompt', help='Negative prompt to avoid certain elements')
    
    args = parser.parse_args()
    
    try:
        # Initialize generator
        generator = ScenarioImageGenerator()
        
        # Prepare kwargs
        kwargs = {
            'width': args.width,
            'height': args.height,
            'samples': args.samples,
            'steps': args.steps,
            'guidance': args.guidance
        }
        
        if args.negative_prompt:
            kwargs['negative_prompt'] = args.negative_prompt
        
        # Generate image
        print(f"🎨 Generating image for: '{args.prompt}'")
        result = generator.generate_image(args.prompt, **kwargs)
        
        if result:
            print(f"✅ Successfully generated {len(result)} image(s)!")
            for filepath in result:
                print(f"📁 {filepath}")
        else:
            print("❌ Failed to generate image")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
