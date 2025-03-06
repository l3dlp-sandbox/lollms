import requests
from typing import Optional, Dict
from lollms.ttv import LollmsTTV
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import os
from pathlib import Path

class LollmsLumaLabs(LollmsTTV):
    def __init__(self, app, output_folder:str|Path=None):
        """
        Initializes the NovitaAITextToVideo binding.

        Args:
            api_key (str): The API key for authentication.
            base_url (str): The base URL for the Novita.ai API. Defaults to "https://api.novita.ai/v3/async".
        """
        # Check for the LUMALABS_KEY environment variable if no API key is provided
        api_key = os.getenv("LUMALABS_KEY","")
        service_config = TypedConfig(
            ConfigTemplate([
                {"name":"api_key", "type":"str", "value":api_key, "help":"A valid Lumalabs AI key to generate text using anthropic api"},
            ]),
            BaseConfig(config={
                "api_key": "",     # use avx2
            })
        )

        super().__init__("lumalabs", app, service_config, output_folder)

        self.base_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.service_config.api_key}",
            "content-type": "application/json"
        }

    def settings_updated(self):
        self.base_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.service_config.api_key}",
            "content-type": "application/json"
        }

    def generate_video(self, prompt: str, aspect_ratio: str = "16:9",                  
                       loop: bool = False, num_frames: int = 60, 
                       fps: int = 30, keyframes: Optional[Dict] = None)-> str:
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop
        }
        
        if keyframes:
            payload["keyframes"] = keyframes

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        generation_data = response.json()
        video_url = generation_data['assets']['video']
        
        # Download the video
        video_response = requests.get(video_url)
        video_response.raise_for_status()
        
        output_path = "output.mp4"
        with open(output_path, 'wb') as f:
            f.write(video_response.content)
        
        return output_path

    def generate_video_by_frames(self, prompts, frames, negative_prompt, fps = 8, num_inference_steps = 50, guidance_scale = 6, seed = None):
        pass # TODO : implement

    def extend_video(self, prompt: str, generation_id: str, reverse: bool = False) -> str:
        keyframes = {
            "frame0" if not reverse else "frame1": {
                "type": "generation",
                "id": generation_id
            }
        }
        return self.generate_video(prompt, keyframes=keyframes)

    def image_to_video(self, prompt: str, image_url: str, is_end_frame: bool = False) -> str:
        keyframes = {
            "frame0" if not is_end_frame else "frame1": {
                "type": "image",
                "url": image_url
            }
        }
        return self.generate_video(prompt, keyframes=keyframes)

# Usage example:
if __name__ == "__main__":
    luma_video = LumaLabsVideo("your-api-key-here")
    prompt = "A panda, dressed in a small, red jacket and a tiny hat, sits on a wooden stool in a serene bamboo forest. The panda's fluffy paws strum a miniature acoustic guitar, producing soft, melodic tunes."
    output_video = luma_video.generate_video(prompt)
    print(f"Video generated and saved to: {output_video}")