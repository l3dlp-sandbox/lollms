# Title LollmsDiffusers
# Licence: MIT
# Author : Paris Neo
    # All rights are reserved

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.utilities import PackageManager, check_and_install_torch, find_next_available_filename, install_cuda, check_torch_version

import sys
import requests
from typing import List, Dict, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.tti import LollmsTTI
from lollms.utilities import git_pull
from tqdm import tqdm
import threading

import pipmaster as pm
if not pm.is_installed("torch"):
    pm.install_or_update("torch torchvision torchaudio", "https://download.pytorch.org/whl/cu121")

import torch
if not torch.cuda.is_available():
    pm.install_or_update("torch torchvision torchaudio", "https://download.pytorch.org/whl/cu121")



def adjust_dimensions(value: int) -> int:
    """Adjusts the given value to be divisible by 8."""
    return (value // 8) * 8

def download_file(url, folder_path, local_filename):
    # Make sure 'folder_path' exists
    folder_path.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        with open(folder_path / local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                progress_bar.update(len(chunk))
        progress_bar.close()

    return local_filename

def install_model(lollms_app:LollmsApplication, model_url):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    diffusers_folder = shared_folder / "diffusers"
    if not PackageManager.check_package_installed("diffusers"):
        PackageManager.install_or_update("diffusers")
    if not PackageManager.check_package_installed("torch"):
        check_and_install_torch(True)

    if not PackageManager.check_package_installed("torch"):
        PackageManager.install_package("torch torchvision torchaudio", "https://download.pytorch.org/whl/cu121")

    if not PackageManager.check_package_installed("transformers"):
        PackageManager.install_package("transformers")

    if not PackageManager.check_package_installed("diffusers"):
        PackageManager.install_package("diffusers")

    import torch
    from diffusers import PixArtSigmaPipeline

    # You can replace the checkpoint id with "PixArt-alpha/PixArt-Sigma-XL-2-512-MS" too.
    pipe = PixArtSigmaPipeline.from_pretrained(
        "PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", torch_dtype=torch.float16
    )    


def install_diffusers(lollms_app:LollmsApplication):
    root_dir = lollms_app.lollms_paths.personal_path
    shared_folder = root_dir/"shared"
    diffusers_folder = shared_folder / "diffusers"
    diffusers_folder.mkdir(exist_ok=True, parents=True)
    models_dir = diffusers_folder / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    PackageManager.reinstall("diffusers")
    PackageManager.reinstall("xformers")
        



def upgrade_diffusers(lollms_app:LollmsApplication):
    PackageManager.install_or_update("diffusers")
    PackageManager.install_or_update("xformers")


class LollmsDiffusers(LollmsTTI):
    has_controlnet = False
    def __init__(
                    self, 
                    app:LollmsApplication, 
                    wm = "Artbot", 
                    ):
        if not PackageManager.check_package_installed("torch"):
            PackageManager.install_package("torch torchvision torchaudio", "https://download.pytorch.org/whl/cu121")

        if not PackageManager.check_package_installed("transformers"):
            PackageManager.install_package("transformers")

        if not PackageManager.check_package_installed("diffusers"):
            PackageManager.install_package("diffusers")
        
        super().__init__("diffusers",app)
        self.ready = False
        # Get the current directory
        lollms_paths = app.lollms_paths
        root_dir = lollms_paths.personal_path
        
        self.wm = wm

        shared_folder = root_dir/"shared"
        self.diffusers_folder = shared_folder / "diffusers"
        self.output_dir = root_dir / "outputs/diffusers"
        self.models_dir = self.diffusers_folder / "models"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

       
        ASCIIColors.red("   _           _ _                    _ _  __  __                          ")
        ASCIIColors.red("  | |         | | |                  | (_)/ _|/ _|                         ")
        ASCIIColors.red("  | |     ___ | | |_ __ ___  ___   __| |_| |_| |_ _   _ ___  ___ _ __ ___  ")
        ASCIIColors.red("  | |    / _ \| | | '_ ` _ \/ __| / _` | |  _|  _| | | / __|/ _ \ '__/ __| ")
        ASCIIColors.red("  | |___| (_) | | | | | | | \__ \| (_| | | | | | | |_| \__ \  __/ |  \__ \ ")
        ASCIIColors.red("  |______\___/|_|_|_| |_| |_|___/ \__,_|_|_| |_|  \__,_|___/\___|_|  |___/ ")
        ASCIIColors.red("                              ______                                       ")
        ASCIIColors.red("                             |______|                                      ")

        import torch 
        if not PackageManager.check_package_installed("diffusers"):
            check_and_install_torch("nvidia" in self.app.config.hardware_mode)            
            PackageManager.install_or_update("diffusers")
            PackageManager.install_or_update("sentencepiece")
            PackageManager.install_or_update("accelerate")
        try:
            if "stable-diffusion-3" in app.config.diffusers_model:
                from diffusers import StableDiffusion3Pipeline # AutoPipelineForImage2Image#PixArtSigmaPipeline
                self.model = StableDiffusion3Pipeline.from_pretrained(
                    app.config.diffusers_model, torch_dtype=torch.float16, cache_dir=self.models_dir,
                    use_safetensors=True,
                )
            else:
                from diffusers import AutoPipelineForText2Image # AutoPipelineForImage2Image#PixArtSigmaPipeline
                self.model = AutoPipelineForText2Image.from_pretrained(
                    app.config.diffusers_model, torch_dtype=torch.float16, cache_dir=self.models_dir,
                    use_safetensors=True,
                )
            
            # AutoPipelineForText2Image
            # self.model = StableDiffusionPipeline.from_pretrained(
            #     "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16, cache_dir=self.models_dir,
            #     use_safetensors=True,
            # ) # app.config.diffusers_model
            # Enable memory optimizations.
            try:
                if app.config.diffusers_offloading_mode=="sequential_cpu_offload":
                    self.model.enable_sequential_cpu_offload()
                elif app.coinfig.diffusers_offloading_mode=="model_cpu_offload":
                    self.model.enable_model_cpu_offload()
            except:
                pass
        except Exception as ex:
            self.model= None
            trace_exception(ex)
    @staticmethod
    def verify(app:LollmsApplication):
        # Clone repository
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        diffusers_folder = shared_folder / "diffusers"
        return diffusers_folder.exists()
    
    def get(app:LollmsApplication):
        root_dir = app.lollms_paths.personal_path
        shared_folder = root_dir/"shared"
        diffusers_folder = shared_folder / "diffusers"
        diffusers_script_path = diffusers_folder / "lollms_diffusers.py"
        git_pull(diffusers_folder)
        
        if diffusers_script_path.exists():
            ASCIIColors.success("lollms_diffusers found.")
            ASCIIColors.success("Loading source file...",end="")
            # use importlib to load the module from the file path
            from lollms.services.diffusers.lollms_diffusers import LollmsDiffusers
            ASCIIColors.success("ok")
            return LollmsDiffusers

    def get_scheduler_by_name(self, scheduler_name="LMS"):
        if scheduler_name == "LMS":
            from diffusers import LMSDiscreteScheduler
            return LMSDiscreteScheduler(
                beta_start=0.00085, 
                beta_end=0.012, 
                beta_schedule="scaled_linear"
            )
        elif scheduler_name == "Euler":
            from diffusers import EulerDiscreteScheduler
            return LMSDiscreteScheduler()
        elif scheduler_name == "DDPMS":
            from diffusers import DDPMScheduler
            return DDPMScheduler()
        elif scheduler_name == "DDIMS":
            from diffusers import DDIMScheduler
            return DDIMScheduler()
        
        
            
    def paint(
                self,
                positive_prompt,
                negative_prompt,
                sampler_name="",
                seed=-1,
                scale=7.5,
                steps=20,
                img2img_denoising_strength=0.9,
                width=512,
                height=512,
                restore_faces=True,
                output_path=None
                ):
        import torch
        if sampler_name!="":
            sc = self.get_scheduler_by_name(sampler_name)
            if sc:
                self.model.scheduler = sc
        width = adjust_dimensions(int(width))
        height = adjust_dimensions(int(height))
        if output_path is None:
            output_path = self.output_dir
        if seed!=-1:
            generator = torch.Generator("cuda").manual_seed(seed)
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps, generator=generator).images[0]
        else:
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps).images[0]
        output_path = Path(output_path)
        fn = find_next_available_filename(output_path,"diff_img_")
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
    def paint_from_images(self, positive_prompt: str, 
                            images: List[str], 
                            negative_prompt: str = "",
                            sampler_name="",
                            seed=-1,
                            scale=7.5,
                            steps=20,
                            img2img_denoising_strength=0.9,
                            width=512,
                            height=512,
                            restore_faces=True,
                            output_path=None
                            ) -> List[Dict[str, str]]:
        import torch
        if sampler_name!="":
            sc = self.get_scheduler_by_name(sampler_name)
            if sc:
                self.model.scheduler = sc

        if output_path is None:
            output_path = self.output_dir
        if seed!=-1:
            generator = torch.Generator("cuda").manual_seed(seed)
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps, generator=generator).images[0]
        else:
            image = self.model(positive_prompt, negative_prompt=negative_prompt, height=height, width=width, guidance_scale=scale, num_inference_steps=steps).images[0]
        output_path = Path(output_path)
        fn = find_next_available_filename(output_path,"diff_img_")
        # Save the image
        image.save(fn)
        return fn, {"prompt":positive_prompt, "negative_prompt":negative_prompt}
    
