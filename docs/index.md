# Software-Based Single Frame HDR Image Reconstruction

Edward Barton, Michelle Jensen, Daniel Kiel

## Problem Statement

Most practical usage of HDR imaging has been in photography and cinema using different forms of bracketing and frame blending. However, recent developments in sensor technology, like sensors with dual-gain ADCs and non-linear sensitivity, single-shot HDR is increasingly pervasive. Even with these hardware-based advancements, there is still more information that can be recovered in software. HDR imaging techniques are showing their importance in computational imaging and computer vision applications. For instance, we will be focusing on object detection and recognition in saturated regions for applications such as autonomous vehicles.

The current state-of-the-art in still image HDR is a derivation of bracketing that does mosaic alignment and exposure merge, followed by an image processing pipeline that includes demosaic and tone-mapping. In single-shot HDR, using a skip-connected autoencoder deep convolutional neural network (CNN), the reconstruction function is learned. The single-shot method is restricted to highlight reconstruction without denoising. The state-of-the-art in motion relies heavily on HDR sensor technology. For a high-frame-rate camera, exposure bracketing can be employed to create a standard frame rate video from frame blending while using optical flow combined with patch-based synthesis for motion compensation. In addition, a similar function based on alternating exposures is learned through a deep neural network.

We narrowed the scope of our investigation to the reconstruction of a high dynamic range (HDR) image from a single Bayer color filtered frame in software. In the majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters with a repeating 2x2 block: red, green, green, blue. The resulting frame requires interpolation to fill in the remaining two-thirds of color information to create an RGB image. During this interpolation, a white balancing operation is performed that often boosts data recorded in either or both of the red and blue channels beyond 1.0 (the max value in standard dynamic range systems). This additional highlight information in the white balanced image can be used to interpolate missing lightness detail and hue in other clipped channels.

## Methods

### Pixel-wise Separation of Lightness and Color Properties

The pixel-wise methods used are based on the ability to separate lightness information from the colorfulness and hue information that makes up a color. The methods rely on CIE LCh [1] and HSV [2] as the reconstruction color spaces, respectively. Though minor implementation details differ – RGB to LCh conversion requires multiple color transforms – the methods follow the same general algorithm. We copy an unclipped, white-balanced image in camera RGB space and clip it at the defined min and max values for the scale. A conversion to the reconstruction space is applied to both copies of the image. In the reconstruction space we stack the lightness channel (L in LCh, V in HSV) of the unclipped representation with the linearly interpolated color channels of the clipped and unclipped representation. We then apply the reverse transform from the reconstruction space to RGB space. These pixel-wise reconstructions follow white balance in the camera pipe, but precede any digital gain stage and final display RGB space conversions (sRGB, BT.709, etc).

In the HSV method, one implementation that was found in the open-source community in the app dcraw, used linear interpolation of clipped values and unclipped values combined to create the reconstruction. In our method, we did no linear interpolation as to recover the full lightness information given by the sensor. Due to the nature of HSV channels not being perceptually linear and being relative values, lightness changes with hue, as does saturation. We also found that by keeping the clipped saturation instead of linearly interpolating between the two representations eliminated harsh artifacting at transition edges between different channels clipping. 

**TODO: PUT SATURATION ARTIFACTING ALONG WITH FULL HSV RECONSTRUCTION**

The LCh method is an absolute transform when specified with a white point. In our case D65 was used. It is perceptually linear and device agnostic. Meaning a linear change in one channel will result in a linear visually perceived change in a space that is independent of acquisition or display. The combination of these two design choices mean the three channels are perceptually distinct from each other, unlike HSV where lightness varies between hues. This method involved combining the lightness channel of the unclipped image with the hue and colorfulness of the clipped image without linear interpolation. Despite the extra color transforms and non-linear transformations, we saw no drop in performance when compared to HSV reconstruction.

**TODO: PUT LCH RECONSTRUCTION**

### Deep Convolutional Neural Network

The work done by Eilertsen et al. involves using a "fully convolutional deep hybrid dynamic range autoencoder network". The encoder converts SDR input to latent set and the log transform skip connections help the decoder to reconstruct the HDR image in log domain. The skip connections help to restore lightness information as the fine detail is lost through the down-sampling at each step of the encoder. This network was trained on rasterized, display space images that are output from the camera raw pipeline. This is in opposition to the pixel-wise methods which operate on camera RGB space images before any useful data can be clipped after white-balance and sRGB transform.

**TODO: PUT CNN RECONSTRUCTION**

## Performance and Evaluation

The dataset used is a subset of the the “HDR+ Burst Photography Dataset” [5][6] compiled and created by a Google Research team. We chose this dataset in part for the number of images, but mostly because the images are largely unmodified raw data and carry color transform metadata needed for our pipeline. Most of the images are around 12MP at a 4:3 ratio. We used the first image from each burst set which contained an average of 6 frames per burst.

The pixel-wise methods are the more compute efficient algorithms, as expected. **might need to change this to Dan's numbers** On a 2.9GHz 6th Gen Intel i7 MacBook Pro using SIMD instructions, the full pipeline from 4:3 ratio, 4K clipped raw binned to 1K reconstructed log space took roughly 4 ms per image. This translates to about 225 fps. Due to the nature of the Halide language, there is no way to perform branch statements without pre-computing possible outcomes. Therefore, both LCh and HSV reconstructions are performed and the correct representation is chosen based on used input. This unified pipeline run on the whole dataset of 3640 DNGs ran at 19.4287 sec, or roughly 187 fps. The same unified pipeline modified for a 2K output resolution averaged roughly 61 fps.

We did not modify the CNN or create an optimized implementation as the reference implementation is written to use CUDA instructions via Tensorflow. The HDRCNN took roughly **insert ms per image**, translating to roughly **insert fps here** on **insert resolution here** images. This is markedly slower than pixel-wise methods. However, the drop in performance might be reconciled in evaluation of the final recovery.

With the pixel-wise methods, it's possible to define a mathematical upper-bound on the number of photographic stops (EV) of light that are recoverable in linear space for each image. A photographic stop is equal to a doubling of light. For HSV the calculation is fairly simple. It is the base-2 log of the ratio between the maximum and minimum RGB white balance multipliers. This is because the HSV conversion uses the maximum intensity of the three RGB channels for the lightness representation. Therefore, if all channels are fully saturated at 1.0 before white balance, then the lightness representation will the channel with the highest white balance multiplier.

## **Detectron Stuff**

## **Conclusions**

## **References**

## **Project Artifacts**

* [Initial Proposal](proposal.md)

* [Midterm Report](midterm_report.md)
