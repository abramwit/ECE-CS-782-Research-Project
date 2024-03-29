# -*- coding: utf-8 -*-
"""sd.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HjRU2AcN902wwcXGFtqg-_-9mpjqzAIm

#Setup
"""

!git clone https://github.com/huggingface/diffusers.git

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/diffusers
# %pip install -e .       # didn't have before... necessary?
# %pip install --upgrade diffusers[torch]
# %pip install transformers

# Commented out IPython magic to ensure Python compatibility.
# %cd examples/dreambooth
# %pip install -r requirements.txt

from accelerate.utils import write_basic_config
write_basic_config()

# Import necessary libraries
import torch
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from PIL import Image
import os

pip install --upgrade diffusers[torch]

"""#Inference"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/

# Commented out IPython magic to ensure Python compatibility.
# %pwd

from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipeline.to("cuda")
pipeline("An image of a squirrel in Picasso style").images[0]

"""# Fine tuning

## Data
"""

from google.colab import drive
drive.mount('/content/drive')

"""Import $T$ and $T_{¬t}$ <text, image> Boeing 707 datasets from FGVC Aircraft data"""

class TextImageDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = self.data.iloc[idx, 0]
        img_path = os.path.join(self.root_dir, self.data.iloc[idx, 1])
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        label = self.data.iloc[idx, 2]
        return text, image, label

# Define the image transformation
transform = transforms.Compose([
    transforms.Resize(512),
    transforms.CenterCrop(512),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Load the CSV data into a PyTorch Dataset
train_dataset = TextImageDataset('/content/drive/MyDrive/Fine_tuning_data/T.csv', '/content/drive/MyDrive/Fine_tuning_data/T', transform=transform)
test_dataset = TextImageDataset('/content/drive/MyDrive/Fine_tuning_data/T_{nt}.csv', '/content/drive/MyDrive/Fine_tuning_data/T_{nt}', transform=transform)

"""Fine Tune DM on train dataset (set of 10 Boeing 707 <text, image> pairs from T)"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/diffusers/examples/dreambooth/

!accelerate launch train_dreambooth.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5"  \
  --instance_data_dir="/content/drive/MyDrive/Fine_tuning_data/T" \
  --output_dir="/content/drive/MyDrive/Fine_tuning_data/fine_tuned_weights" \
  --instance_prompt="a photo of sks Boeing 707" \
  --resolution=512 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --learning_rate=5e-6 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --max_train_steps=400 \
  --checkpointing_steps=200

from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained("/content/drive/MyDrive/Fine_tuning_data/fine_tuned_weights")
pipeline.to("cuda")
pipeline("a photo of a white sks Boeing 707 with grey bottom and blue and black striped tail facing right").images[0]