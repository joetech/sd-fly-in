import os
import sys
from PIL import Image


def create_images(prompt):
    print("Hitting the local Stable Diffusion for the base image. This may take a minute ...")

    api = webuiapi.WebUIApi(host='127.0.0.1', port=7860)

    # List available models 
    models = api.util_get_model_names()
    print(models)

    # Select a model
    api.util_set_model('realistic')

    # wait for job complete
    api.util_wait_for_ready()

    print(f"Prompt:\n{prompt}\n")

    result = api.txt2img(prompt=prompt,
                        negative_prompt="nsfw, nude, naked",
                        seed=-1,
                        cfg_scale=7,
                        n_iter=1,
                        sampler_index='DPM++ 2M Karras',
                        steps=20,
                        width=512,
                        height=512,
                        )

    # uncomment for debugging
    #print(result);

    # Handle the resulting images by saving them to ./images
    imgnum=1
    for i in result.images:
        filename=f"./tmp/{imgnum}.png"
        i.save(filename)
        imgnum+=1


def replaceImage(fileName, prompt):
    # Modify the image based on the prompt and save it
    pass


def splitImage(fileName, numberOfParts, depth, prompts):
    currentDepth = 1
    imagesDir = "./images/"

    print(f"Working on depth {currentDepth} of {depth}")

    currentPrompt = prompts.pop(0)

    print(f"Splitting image {fileName} into {numberOfParts} parts.")
    image = Image.open(imagesDir + fileName)
    w, h = image.size
    split_size = int(numberOfParts ** 0.5)
    part_w = w // split_size
    part_h = h // split_size


    for i in range(split_size):
        for j in range(split_size):
            part = image.crop((j * part_w, i * part_h, (j + 1) * part_w, (i + 1) * part_h))

            # Save each part using the given naming convention
            partFileName = fileName.replace(".png", f".{i * split_size + j + 1}.png")
            part.save(imagesDir + partFileName)

            # Replace the image part (assuming replaceImage function is defined elsewhere)
            replaceImage(partFileName, currentPrompt)

            # Recursive call (if depth is not zero and prompts is not empty)
            if depth > 1 and prompts:
                splitImage(partFileName, numberOfParts, depth-1, prompts)

    currentDepth += 1





prompt = "abstract splash of color cyberpunk woman, highly detailed, sharp focus, realistic, masterpiece, amazing, colorful, glistening"

#createBaseImage(prompt)
splitImage("1.png", 4, 4, [
    "abstract splash of color cyberpunk man, highly detailed, sharp focus, realistic, masterpiece, amazing, colorful, glistening",
    "abstract splash of color cyberpunk dog, highly detailed, sharp focus, realistic, masterpiece, amazing, colorful, glistening",
    "abstract splash of color cyberpunk cat, highly detailed, sharp focus, realistic, masterpiece, amazing, colorful, glistening",
])





# n = len(sys.argv)
# img_name = 'input.png'
# dimY = 2
# dimX = 2
# fps = dimY*dimX

# if n >= 3:
#     dimY = int(sys.argv[1])
#     dimX = int(sys.argv[2])
#     if n >= 4:
#         img_name = str(sys.argv[3])
#         if n >= 4:
#             fps = int(sys.argv[4])
    

# img = imageio.v2.imread(os.path.join('./', img_name))
# h, w = img.shape[:2]
# spacY = h / dimY
# spacX = w / dimX
# imagesNames = []

# #forward move
# for j in range(dimY):
#     for i in range(dimX):
#         curImageName = str(j) + 'x' + str(i) + '.png'
#         imagesNames.append(curImageName)
#         crop_img = img[int(j*spacY):int((j+1)*(spacY)), int(i*spacX):int((i+1)*(spacX+1))]
#         imageio.v2.imwrite("cropped/" + str(curImageName), crop_img)
        
# #backwards move
# for j in reversed(range(dimY)):
#     for i in reversed(range(dimX)):
#         if ((i == dimY-1 and j == dimX-1) or (i == 0 and j == 0)):
#             continue
#         curImageName = str(j) + 'x' + str(i) + '.png'
#         imagesNames.append(curImageName)
#         crop_img = img[int(j*spacY):int((j+1)*(spacY)), int(i*spacX):int((i+1)*(spacX+1))]
#         imageio.v2.imwrite("cropped/" + str(curImageName), crop_img)

# images = list()
# for filename in imagesNames:
#     images.append(imageio.v2.imread('./cropped/' + filename))
# imageio.mimsave('./output.gif', images, format='GIF', fps=fps) 