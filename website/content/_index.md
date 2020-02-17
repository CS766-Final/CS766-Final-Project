---
title: "CS 766 Computer Vision Spring 2020 Project Proposal"
date: 2020-02-17T09:34:15-06:00
draft: true
---

## Eddie Barton, Michelle Jensen, and Dan Kiel

### Problem Statement

We will be investigating the reconstruction of a high dynamic range (HDR) image from a single Bayer color filtered frame [1]. In the majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters with a repeating 2x2 block: red, green, green, blue. The resulting frame requires interpolation to fill in the remaining two-thirds of color information to create an RGB image. During this interpolation, a white balancing operation is performed that often boosts data recorded in either or both of the red and blue channels beyond 1.0 (the max value in standard dynamic range systems). This additional highlight information in the white balanced image can be used to interpolate missing lightness detail and hue.

Most practical usage of HDR imaging has been in photography and cinema using different forms of bracketing and frame blending. However, recent developments in sensor technology, like sensors with dual-gain ADCs and non-linear sensitivity, single-shot HDR is increasingly pervasive. Even with these hardware-based advancements, there is still more information that can be recovered in software. HDR imaging techniques are showing their importance in computational imaging and computer vision applications. For instance, we will be focusing on object detection and recognition in saturated regions for applications such as autonomous vehicles.

The current state-of-the-art in still image HDR[2][3] is a derivation of bracketing that does mosaic alignment and exposure merge, followed by an image processing pipeline that includes demosaic and tone-mapping. In single-shot HDR, using a skip-connected autoencoder deep convolutional neural networks (CNN), the reconstruction function is learned. The single-shot method[4] is restricted to highlight reconstruction without denoising. The state-of-the-art in motion relies heavily on HDR sensor technology. For a high-frame-rate camera, exposure bracketing can be employed to create a standard frame rate video from frame blending while using optical flow combined with patch-based synthesis for motion compensation[5]. In addition, a similar function based on alternating exposures is learned through a deep neural network[6].

### Project Approach

We first plan to build from naive classical pixel-wise approaches that interpolate detail from a single pixel. Next, we will evaluate classical region-based methods that take pixels from neighboring saturated regions into consideration. In addition, we will investigate modern approaches built on machine learning. To determine the applicability of the methods to our goal of object detection, we will test how well object detection works on the output of the previously described processes.

### Tentative Project Results

For many modern image processing methods, visual defects are detected using the Delta E, High Dynamic Range - Visual Difference Predictor 2 (HDR-VDP2), and Peak Signal to Noise Ratio (PSNR) metrics. However, machine perception algorithms and networks will not necessarily see defects in the same manner as a human does. Therefore, we will test both the error between the synthesized saturated images and the ground truth and the success rates the object detection in reconstructed images.

### References

[1]("https://patents.google.com/patent/US3971065A/en")

[2]("https://static.googleusercontent.com/media/hdrplusdata.org/en//hdrplus.pdf")

[3][https://dl-acm-org.ezproxy.library.wisc.edu/doi/pdf/10.1145/3355089.3356508](https://dl-acm-org.ezproxy.library.wisc.edu/doi/pdf/10.1145/3355089.3356508?download=true)

[4]("http://hdrv.org/hdrcnn/material/sga17_paper_large.pdf")

[5]("https://www.ece.ucsb.edu/~psen/PaperPages/HDRVideo/")

[6]("http://faculty.cs.tamu.edu/nimak/Data/Eurographics19_HDRVideo.pdf")

### **Preliminary Project Timeline**

**February 14th:** Project Proposal Due

**February 17th - February 24th:** Literature Search

**February 24th - March 16th:** Gather Image Samples & HDR Saturation Recovery Implementation

**March 16th - March 20th:** Spring Break

**March 20th - March 24th:** Continue Work & Write Mid-Term Report

**March 25th:** Project Mid-Term Report Due

**March 25th - April 20th:** Edge and Object Detection Implementation

**April 20th - April 26th:** Finishing Touches on Project, Prep for Presentation, Work on Final Webpage

**April 27th - May 1st:** In-Class Project Presentation, Work on Final Webpage

**May 1st - May 3rd:** Finishing Touches on Webpage (if needed)

**May 4th:** Final Project Webpage Due
