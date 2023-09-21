import os
import sys
import json
from PIL import Image
import re
import webuiapi # https://github.com/mix1009/sdwebuiapi

# Read the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)

# Extract the variables from the configuration
host = config['host']
port = config['port']
model = config['model']
negative_prompt = config['negative_prompt']
cfg_scale = config['cfg_scale']
sampler_name = config['sampler_name']
steps = config['steps']
width = config['width']
height = config['height']
denoising_strength = config['denoising_strength']
MAX_SIZE = config['MAX_SIZE']
baseImage = config['baseImage']
numberOfPartsToSplit = config['numberOfPartsToSplit']
depthToTraverse = config['depthToTraverse']
depthPrompts = config['depthPrompts']

# Define a constant for the image directory
IMAGES_DIR = './images/'


def listModels():
    # List available models 
    models = api.util_get_model_names()
    print(models)


def createBaseImage(prompt):
    print("Hitting the local Stable Diffusion for the base image. This may take a minute ...")

    api = webuiapi.WebUIApi(host='127.0.0.1', port=7860)

    # Select a model
    api.util_set_model('sdvn6Realxl_detailface')

    # wait for job complete
    api.util_wait_for_ready()

    print(f"Prompt:\n{prompt}\n")

    result = api.txt2img(prompt=prompt,
                        negative_prompt=negative_prompt,
                        seed=-1,
                        cfg_scale=cfg_scale,
                        n_iter=1,
                        sampler_index=sampler_name,
                        steps=steps,
                        width=width,
                        height=height,
                        )

    # uncomment for debugging
    #print(result);

    # Handle the resulting images by saving them to ./images
    imgnum=1
    for i in result.images:
        filename=f"{IMAGES_DIR}tmp.png"
        i.save(filename)
        imgnum+=1


def replaceImage(fileName, prompt):
    print(f"Hitting the local Stable Diffusion for the img2img work on {fileName}...")

    api = webuiapi.WebUIApi(host='127.0.0.1', port=7860)

    image = Image.open(f"{IMAGES_DIR}{fileName}")

    # Select a model
    api.util_set_model('sdvn6Realxl_detailface')

    # wait for job complete
    api.util_wait_for_ready()

    # print(f"Prompt:\n{prompt}\n")

    result = api.img2img(prompt=prompt,
                        images=[image],
                        negative_prompt="nsfw, nude, naked",
                        seed=-1,
                        cfg_scale=7,
                        n_iter=1,
                        sampler_name='DPM++ 2M Karras',
                        steps=20,
                        width=512,
                        height=512,
                        denoising_strength=0.45,
                        resize_mode=1,
                        inpainting_fill=0,
                        )

    # uncomment for debugging
    # print(result);

    # Handle the resulting images by saving them to ./images
    imgnum=1
    for i in result.images:
        savefile = f"{IMAGES_DIR}{fileName}"
        # savefile.replace(".png", f".-opt-{imgnum}.png") # uncomment if n_iter is > 1
        i.save(savefile)
        imgnum+=1


def splitImage(fileName, numberOfParts, depth, prompts):
    currentDepth = 1
    imagesDir = IMAGES_DIR

    print(f"Working on depth {currentDepth} of {depth}")

    print(f"Splitting image {fileName} into {numberOfParts} parts.")
    image = Image.open(imagesDir + fileName)
    w, h = image.size
    
    # Determine rows and columns
    cols = int(numberOfParts ** 0.5)
    rows = cols
    
    if cols * rows != numberOfParts:
        # Adjust for non-square numbers
        if numberOfParts % cols == 0:
            rows = numberOfParts // cols
        else:
            cols = numberOfParts // rows

    part_w = w // cols
    part_h = h // rows

    for i in range(rows):
        for j in range(cols):
            part = image.crop((j * part_w, i * part_h, (j + 1) * part_w, (i + 1) * part_h))

            # Save each part using the given naming convention
            partFileName = fileName.replace(".png", f".{i * cols + j + 1}.png")
            part.save(imagesDir + partFileName)

            # Replace the image part
            if currentDepth < len(prompts):
                replaceImage(partFileName, prompts[currentDepth])

            # Recursive call
            if currentDepth < depth and currentDepth < len(prompts):
                splitImage(partFileName, numberOfParts, depth - currentDepth, prompts[currentDepth])

    currentDepth += 1
    output = mergeImage(fileName, depth)
    print(f"Merged image saved as: {output}")


def mergeImage(baseImage, depth):
    assert depth > 0, "Depth must be greater than 1"
    
    imagesDir = IMAGES_DIR
    imagesSubDir = imagesDir + baseImage.replace(".png", "-parts") + '/'
    os.mkdir(imagesSubDir)
    
    # Construct the search pattern based on baseImage and depth
    prefix = baseImage.replace(".png", "")
    pattern = re.escape(prefix) + r"\.\d+\.png" if depth > 2 else re.escape(prefix) + r"\.\d+\.png"
    
    # List all images in the directory and filter based on the pattern
    all_files = os.listdir(imagesDir)
    matching_files = [f for f in all_files if re.match(pattern, f)]

    # Custom sort function to sort based on numerical value after prefix
    def custom_sort(filename):
        # Extract the number after the prefix for sorting
        return int(filename.split('.')[-2])

    matching_files = sorted(matching_files, key=custom_sort)
    
    # Calculate the dimensions for the merged image
    sample_image = Image.open(imagesDir + matching_files[0])
    w, h = sample_image.size
    merged_width = int(len(matching_files) ** 0.5 * w)
    merged_height = int(len(matching_files) ** 0.5 * h)
    
    # Create an empty image to paste the smaller images into
    merged_image = Image.new('RGB', (merged_width, merged_height))
    
    # Split size calculation
    split_size = int(len(matching_files) ** 0.5)
    
    for idx, filename in enumerate(matching_files):
        image = Image.open(imagesDir + filename)
        
        x_offset = (idx % split_size) * w
        y_offset = (idx // split_size) * h
        
        merged_image.paste(image, (x_offset, y_offset))
        os.replace(imagesDir + filename, imagesSubDir + filename)

    
    MAX_SIZE = 1024

    # Check if the image dimensions exceed the maximum size
    if merged_image.width > MAX_SIZE or merged_image.height > MAX_SIZE:
        # Calculate the ratio to resize the image proportionally
        ratio = min(MAX_SIZE / merged_image.width, MAX_SIZE / merged_image.height)
        new_width = int(merged_image.width * ratio)
        new_height = int(merged_image.height * ratio)

        # Resize the image
        merged_image = merged_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Save the image
    output_filename = prefix + ".png"
    merged_image.save(imagesDir + output_filename)


    # Save or return the merged image (you can modify as needed)
    # output_filename = prefix + "_merged.png"
    output_filename = prefix + ".png"
    merged_image.save(imagesDir + output_filename)
    
    return output_filename


splitImage(baseImage, numberOfPartsToSplit, depthToTraverse, depthPrompts)
