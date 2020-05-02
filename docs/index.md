# Project Title

#### Eddie Barton, Michelle Jensen, and Dan Kiel

## **Introduction**

In a majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters using a repeating 2x2 block: red, green, green, blue. This frame from this capture requires interpolation to fill in the remaining two-thirds of color information in order to create an RGB image. When this  interpolation occurs, a white balancing operation is applied that often boosts the data recorded in one or both of the red and blue channels beyond 1.0, which is the max value in standard-dynamic-range (SDR) systems. The additional highlight information in the white balanced image can be used to interpolate the missing hue and lightness detail.

We investigated the reconstruction of single shot high-dynamic-range images using a single Bayer color filtered frame. There are three different approaches examined. Two which are pixel-wise approaches involving the CIE-LCh and HSV color spaces. We examine the naïve approaches and our optimized version of them. The last approach is state-of-the-art and uses a skip-connected autoencoder deep convolutional neural network (CNN).

**something about the motivation of downstream image tasks like object detection and self driving cars...**

## **Image Set and Processing Pipeline**

The image set worked on was sourced from the "HDR+ Burst Photography Dataset" that was created and compiled by a Google Research time. Our image set of **number of images**, is a subset of these images created by taking the first image of each burst set. These images come in a DNG format which provide us information need to perform the color mapping need in the pixel-wise approaches.

To process the images, we worked directly from camera raw images in the Adobe DNG format. A crude raw pipeline was implemented using rawpy to extract the mosaiced image and the necessary metadata for color transforms. Then a 2-stage 2x2 pixel binning is performed as opposed to a high detail demosiac. **mention something to do with our motivation** This yields ~2MP images when working from the Google HDR+ dataset.  ADC(this stands for ???) clipping is simulated by having an gain stage early in the raw pipeline. In the figures below we encode the SDR image with both a standard 2.2 gamma power curve and Hybrid Log-Gamma. The reconstructed images are all encoded with HLG. HLG was chosen because of similarity in characteristic to standard gamma curves while also being able to encode the range 0.0 to 12.0 before clipping. While there are

## **Pixel-wise Approaches**

## **CNN**

## **Detectron Stuff**

## **Conclusions**

## **References**

## **Project Artifacts**

* [Initial Proposal](proposal.md)

* [Midterm Report](midterm_report.md)
