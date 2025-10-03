# Shepard and Metzler Cube problem prediction model

This project, completed for ECE 9611 Intro to Machine Learning, aims to create a machine learning model that can solve Shepard and Metzler cube problems.

> **FOR ECE 9611 TA**\
> Our dataset for Phase 1, is too large to upload to GitHub.\
> You can run the generation code on your own machine if you wish, but beware that datasets can become several GB!.\
> We are using an alternative storage solution for our dataset. We can provide you access to this should you desire.\

## The data
We are generating images of Shepard and Metzler cubes represented in various angles.
- There are 41 polycubes from n=1 to n=5.
- We are rounding angles to the nearest 20 degrees. There are 2 axes, so (360/20)^2 = 324 viewing angles
- This leads to 13,284 independent images.
- We need to pair each image to **all** other images for the training set, creating a total number of (13,284)^2= 176,464,656 image pairs.
- It is infeasible to generate 176 million images at our student-level scale, so we will randomly select 0.33% of the data, or 582,333 images for model training.

## Components
This project is build from multiple parts:
- **Dataset generator**: Lists all possible shapes that can be made from 1 to n cubes, and at all possible angles of which they can be represented. Finally, it puts them in pairs to create cube problems.
- **Dataset renderer**: From the pairs created by the generator, the renderer creates images of the cubes at the specified angles. This data is used to train the model.
- **Model**: Trained from the images, which are labelled as 'SAME' or 'DIFFERENT'. Predicts whether two images are of the same shape or not.
- **Interactive demo**: A GUI demo that allows you to create cube shapes and rotate them to any angle, allowing free-form creation of Shepard and Metzler cube problems, which are then solved by the model in real-time. This demo allows us to test the efficacy of the model.

## Credits
Creators of this project:
- James Nicholls
- Xiang Li
- Kelvin Zheng
- Anthony Barros

Other projects used:
- https://github.com/mikepound/cubes
    - This algorithm was used for generating all polycubes from 1 to n.
    - See `data_generate/polycube_generator/` for implementation