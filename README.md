# SD Fly In
I've always admired those videos where you're looking at an image and it zooms in on one small detail that happens to be its own whole image and then it zooms in on a small detail of that and so on.  This can be automated with Stable Diffusion and image magic!

## Zoom in workflow:
- Start with a base image using a generic fantasy prompt, say, 512x512
	- save image as 1.png
- Divide the image into 4 images
- For each image upscale x 4 and then, use same generic fantasy prompt and send to img2img
	- save each "pixel image" as 1.1, 1.2, 1.3, 1.4
- Repeat above, but the next layer images are saved as 1.1.1, 1.1.2, etc. and 1.2.1, 1.2.2, etc.  Reate process maybe 10-30 times
- Once we have all the image, reduce each image to 1x1 or 2x2 or 4x4 (need to experiment to see which will be best)
- Join all the images back together to form one master image that should look pretty close to the original 1.png
- Join larger versions of "pixel images" in different configurations.
- Bonus: Build a UI to zoom in and out of the masterpiece


## Test Run 1 - Keep it small
- Goal
  - Generate the smallest usable example
- Minimum requirements:
  - Split and replace (img2img) images recursively
  - Put images back together
  - Animate?


## Learnings and Reminders
- Smallest recognizable image is 512 x 512
- Dimensions must be able to be evenly halved (no odd numbers)
