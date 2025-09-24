# Shepard and Metzler Cube problem prediction model

This project, completed for ECE 9611 Intro to Machine Learning, aims to create a machine learning model that can solve Shepard and Metzler cube problems.

> **FOR ECE 9611 TA**\
> To see our dataset for Phase 1, please go to `data_generate/paired_cubes.csv`\
> The images are too large to store on GitHub, so only text data is available.\
> We are using an alternative storage solution for the image data. We can provide you access to this should you desire.

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
- https://github.com/tjgokken/polycube-generator/tree/main/src
    - Using GPT-4 to convert to Python, this algorithm was used for generating all polycubes from 1 to n.
    - See `data_generate/polycube_generator/` for implementation