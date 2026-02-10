# SW Cellular Visualization README

This project was made for Duke Kunshan Undergraduate Signature Work Project 2025 encoding a Web Interface for Cell Segmentation Data Visualization. 

The website is currently deployed through Render: https://sw-cellvis.onrender.com/

### Goal
The aim of this project is to make Computational tools more avaliable and accessible to Biologists without requiring extensive knowledge of coding. 

Many Computational Biology softwares lack a proper UI for biologists to utilize the tools. While Cellpose has a UI for segmentation and fine-tuning, it lacks an efficient method to perform feature extraction on the output segmentation files. This web application aims to allow a user to upload files for feature extraction post-segmentation.


### This repository contains: 
- README file
- requirements: the required packages to deploy as a web application
- sw_cellvis: the python backend for data processing
- templates: HTML files for the frontend of the website
- Static: 
    - CSS files for styling
    - Images and figures
    - The final Signature Work paper


### Post-segmentation processing
The input for segmentation is an imaging file. This can be in several format including: png, jpg, tiff, etc. 
The output for segmentation though Cellpose is a .npy file

This web application takes both the original imaging file and .npy file as input to extrapolate features such as intensity, diameter, and location. 


### Future Work: 
I envision this website to have many possible future updates.
Currently, the feature of uploading a user's own images and .npy files for feature extraction is under construction.
Subsequently, additional feature extraction options and tools will become avaliable. 

In the future, this model can be extended to operate on the output of many different, commonly used cellular segmentation software.

During this project, it was envisioned that this web application could serve as a platform for a computational processing pipeline from imaging data to language-based pattern identification through the use of an image captioning model such as BLIP-2.