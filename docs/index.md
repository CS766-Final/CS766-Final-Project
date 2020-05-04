# Software-Based Single Frame HDR Image Reconstruction

Edward Barton, Michelle Jensen, Daniel Kiel

## Problem Statement

Most practical usage of high-dynamic-range (HDR) imaging has been in photography and cinema using different forms of bracketing and frame blending. However, recent developments in sensor technology, like sensors with dual-gain ADCs and non-linear sensitivity, single-shot HDR is increasingly pervasive. Even with these hardware-based advancements, there is still more information that can be recovered in software. HDR imaging techniques are showing their importance in computational imaging and computer vision applications. For instance, we will be focusing on object detection and recognition in saturated regions for applications such as autonomous vehicles.

The current state-of-the-art in still image HDR is a derivation of bracketing that does mosaic alignment and exposure merge, followed by an image processing pipeline that includes demosaic and tone-mapping. In single-shot HDR, using a skip-connected autoencoder deep convolutional neural network (CNN), the reconstruction function is learned. The single-shot method is restricted to highlight reconstruction without denoising. The state-of-the-art in motion relies heavily on HDR sensor technology. For a high-frame-rate camera, exposure bracketing can be employed to create a standard frame rate video from frame blending while using optical flow combined with patch-based synthesis for motion compensation. In addition, a similar function based on alternating exposures is learned through a deep neural network.

We narrowed the scope of our investigation to the reconstruction of a HDR image from a single Bayer color filtered frame in software. In the majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters with a repeating 2x2 block: red, green, green, blue. The resulting frame requires interpolation to fill in the remaining two-thirds of color information to create an RGB image. During this interpolation, a white balancing operation is performed that often boosts data recorded in either one or both of the red and blue channels beyond 1.0 (the max value in standard-dynamic-range systems). This additional highlight information in the white balanced image can be used to interpolate missing lightness detail and hue in other clipped channels.

## Methods

### Processing the Images

To process the images, we work directly from camera raw images in the Adobe DNG format. A raw pipeline was implemented using Halide. As the focus of this project is on real-time methods for use in embedded/low-compute systems, we perform 4x4 green channel binning and 2x2 red/blue channel binning as opposed to high detail demosaic. We simulate ADC clipping with an early gain stage in the raw pipeline. This will allow us to determine the level of overexposure at which each method can no longer produce desirable results. Reconstructed images result in values greater than 1.0, meaning we must encode the data such that all values are able to be written to 8-bit files. We encode the SDR image with both a standard 2.2 gamma power curve and Hybrid Log-Gamma. [[1]][ref 1] The reconstructed images are all encoded with HLG. HLG was chosen because of similarity in characteristic to standard gamma curves while also being able to encode the range 0.0 to 12.0 before clipping. This has been sufficient for our purposes, but it is possible to exhaust the range of this encoding, so other encodings may need to be taken into consideration in other situations.

### Pixel-wise Separation of Lightness and Color Properties

The pixel-wise methods used are based on the ability to separate lightness information from the colorfulness and hue information that makes up a color. The methods rely on CIE LCh [[2]][ref 2] and HSV [[3]][ref 3] as the reconstruction color spaces, respectively. Though minor implementation details differ – RGB to LCh conversion requires multiple color transforms – the methods follow the same general algorithm. We copy an unclipped, white balanced image in camera RGB space and clip it at the defined minimum and maximum values for the scale. A conversion to the reconstruction space is applied to both copies of the image. In the reconstruction space, we stack the lightness channel (L in LCh, V in HSV) of the unclipped representation with the linearly interpolated color channels of the clipped and unclipped representation. We then apply the reverse transform from the reconstruction space to the RGB space. These pixel-wise reconstructions follow white balance in the camera pipe but precede any digital gain stage and final display RGB space conversions (sRGB, BT.709, etc).

In the HSV method, one implementation that was found in the open-source community in the app dcraw used linear interpolation of clipped values and unclipped values to create the reconstruction. In our method, we did no linear interpolation to recover the full lightness information given by the sensor. Due to the nature of HSV channels not being perceptually linear and being relative values, lightness changes with hue, as does saturation. We also found that using the clipped saturation instead of linearly interpolating between the two representations eliminated harsh artifacting at channel clipping boundaries and discoloring across the region.

| <img style="transform:rotate(180deg)" src="./pictures/62CL_20150215_180549_095/sdr_log_+2ev.png"> | <img style="transform:rotate(180deg)" src="./pictures/62CL_20150215_180549_095/hsv_+2ev_sat_artifact.png"> | <img style="transform:rotate(180deg)" src="./pictures/62CL_20150215_180549_095/hsv_+2ev.png"> |
| ------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------: |
| SDR encoded in HLG                                                                                |                                    HSV linearly interpolated saturation                                    |                                  HSV copy clipped saturation                                  |

The LCh method is an absolute transform when specified with a white point. In our case, D65 was used. It is perceptually linear and device agnostic. Meaning a linear change in one channel will result in a linear visually perceived change. The combination of these two design choices means the three channels are perceptually distinct from each other, unlike HSV where lightness varies between hues. This method involved combining the lightness channel of the unclipped image with the hue and colorfulness of the clipped image without linear interpolation. Despite the extra color transforms and non-linear transformations, we saw no drop in performance when compared to the HSV reconstruction.

| <img style="transform:rotate(180deg)" src="./pictures/62CL_20150215_180549_095/sdr_log_+2ev.png"> | <img style="transform:rotate(180deg)" src="./pictures/62CL_20150215_180549_095/sdr_log_+2ev.png"> |
| :-----------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------: |
|                                        SDR encoded in HLG                                         |                                        LCh reconstruction                                         |

### Deep Convolutional Neural Network

The work done by Eilertsen et al. [[4]][ref 4] involves using a "fully convolutional deep hybrid dynamic range autoencoder network". The encoder converts SDR input to a latent set and the log transform skip connections help the decoder to reconstruct the HDR image in the log domain. The skip connections help to restore lightness information as the fine detail is lost through the down-sampling at each step of the encoder. This network was trained on rasterized, display space images that are output from the camera raw pipeline. This is in opposition to the pixel-wise methods which operate on camera RGB space images before any useful data can be clipped after white balance and sRGB transform.

| <img style="transform:rotate(180deg);" src="./pictures/62CL_20150215_180549_095/cnn_+2ev.png"> |
| :--------------------------------------------------------------------------------------------: |
|                                       CNN reconstruction                                       |

## Performance and Evaluation

The dataset used is a subset of the “HDR+ Burst Photography Dataset” [[5]][ref 5][[6]][ref 6] that was compiled and created by a Google Research team. We chose this dataset in part for the number of images, but mostly because the images are largely unmodified raw data and carry color transform metadata needed for our pipeline. Most of the images are around 12MP at a 4:3 ratio. We used the first image from each burst set which contained an average of 6 frames per burst.

The pixel-wise methods are the more computationally efficient algorithms, as expected. On a 4.2GHz Intel i7-6700K using SIMD instructions, the full pipeline processed 4:3 ratio, 4K raw binned to 1K reconstructed log space. Due to the nature of the Halide language and SIMD/GPU devices, there is no way to perform branch statements without pre-computing possible outcomes. Therefore, both the LCh and HSV reconstructions are performed simultaneously and the correct representation is chosen based on user input defined in the run command. This unified pipeline runs on a subset of ~400 DNGs ran at 1.7 sec or roughly 250 fps.

We did not modify the CNN or create an optimized implementation as the reference implementation is written to use CUDA instructions via Tensorflow. Running on a Nvidia GTX 980, the HDRCNN took roughly 350ms per image, translating to roughly 3 fps on 1K 4:3 images. This is markedly slower than the pixel-wise methods. However, more modern hardware should be able to run the CNN more efficiently. The GTX 980 has only 4GB of GDDR5 VRAM and lacks any tensor cores. While running the CNN, tensorflow makes note that more performance may be possible if there were more VRAM. The latest Nvidia card of the 80 series, the RTX 2080 ships with 8GB of VRAM and around 350 tensor cores. With all that being said, the drop in performance might be reconciled in the evaluation of the final recovery.

With the pixel-wise methods, it's possible to define a mathematical upper-bound on the number of photographic stops (EV) of light that are recoverable in linear space for each image. A photographic stop is equal to a doubling of light. For HSV the calculation is fairly simple. It is the base-2 log of the ratio between the maximum and minimum RGB white balance multipliers. This is because the HSV conversion uses the maximum intensity of the three RGB channels for the lightness representation. Therefore, if all channels are fully saturated at 1.0 before the white balance, then the lightness representation will be the channel with the highest white balance multiplier. In most cases, the minimum is 1.0 (the green channel), and the expression can be reduced to use just the max.

![wb = \begin{bmatrix}m_r \ m_g \ m_b\end{bmatrix};m \in \R](https://render.githubusercontent.com/render/math?math=wb%20%3D%20%5Cbegin%7Bbmatrix%7Dm_r%20%5C%5C%20m_g%20%5C%5C%20m_b%5Cend%7Bbmatrix%7D%5C%3Bm%20%5Cin%20%5CR)

![\log_2{\max(wb)}](<https://render.githubusercontent.com/render/math?math=%5Clog_2%7B%5Cmax(wb)%7D>)

LCh recovery depends less on the raw RGB intensities and their corresponding multipliers. This is because of the intermediate color transform from RGB to CIE XYZ before the LCh transform. The Y channel of XYZ represents the linear luminance, while X and Z contain all chromaticities at that luminance. Y is the dot product of the white balanced RGB values and the second row of the camera RGB to XYZ transform matrix. This transform matrix is derived from the color metadata stored in the files and changes on a per-camera basis. From this, we can bound the reconstruction in XYZ space using a similar method above. The dot product tends to produce values less than just taking the max and leads to softer edges and transitions, creating smoother roll-off. This reduces the contrast in comparison to HSV reconstruction.

![\log_2{Y}](https://render.githubusercontent.com/render/math?math=%5Clog_2%7BY%7D)

Something important to note with the pixel-wise methods is that they can only reconstruct hue and saturation values when just one channel in the raw image is clipped. Once two channels clip, these methods only recover lightness. This results in gray regions between the hue restored pixels and full lightness pixels. The CNN and classical methods that take regions into account will fare much better in this regard, except in their failure cases where the result is non-deterministic.

| <img style="transform:rotate(180deg)" src="./pictures/JN34_20150319_183334_317/sdr_log_+2ev.png"> | <img style="transform:rotate(180deg)" src="./pictures/JN34_20150319_183334_317/hsv_+2ev.png"> | <img style="transform:rotate(180deg)" src="./pictures/JN34_20150319_183334_317/lch_+2ev.png"> |
| :-----------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------: |
|                 <img src="./pictures/0032_20160921_125350_046/sdr_log_+3ev.png">                  |                 <img src="./pictures/0032_20160921_125350_046/hsv_+3ev.png">                  |                 <img src="./pictures/0032_20160921_125350_046/lch_+3ev.png">                  |
|                                        SDR encoded in HLG                                         |                                      HSV reconstruction                                       |                                      LCh reconstruction                                       |

Bounding the usable recovery range of the CNN is more difficult as we don't know the function used for the recovery. We do know, however, that the failure cases for the network result in unusable images entirely. In cases where large portions of the frame are clipped, tearing can occur. Whereas in the worst case of the pixel-wise methods, we will have patches of gray, but still discernable transitions. Despite these cases, HDRCNN shows great ability to recover hue and detail across reasonably sized clipped regions.

| <img style="transform:rotate(180deg)" src="./pictures/JN34_20150319_183334_317/sdr_log_+2ev.png"> | <img style="transform:rotate(180deg)" src="./pictures/JN34_20150319_183334_317/cnn_+2ev.png"> |
| ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| <img src="./pictures/0032_20160921_125350_046/sdr_log_+3ev.png">                                  | <img src="./pictures/0032_20160921_125350_046/cnn_+3ev.png">                                  |
| SDR encoded in HLG                                                                                | CNN reconstruction                                                                            |

## Downstream Application: Detectron2

We wanted to see what affect, if any, highlight reconstruction had on downstream tasks. Object detection is prevalent across many fields and possibly benefit from reconstructed inputs. Facebook AI Research's (FAIR's) Detectron2 is one state of the art object detection system. Out of the box, detectron2 is pre-trained on the COCO dataset using popular CNN designs such as Faster R-CNN and RetinaNet. On top of that, it also offers different detection options like Instance Segmentation and Panoptic Segmentation. [[7]][ref 7] We settled on using the pre-trained Mask R-CNN with a ResNet+FPN backbone trained with the 3x schedule to do instance segmentation. We chose this mainly because the authors note that the ResNet+FPN backbone provides the best speed/accuracy trade off.

|                      |:---:|HSV|LCh|CNN
|                      |:---:|:---:|:---:|:---:|
|reconstruction better |:---:|237|234|179|
|SDR_log better        |:---:|180|181|231|


## Conclusions

## Gallery

SDR images in generic 2.2 power curve. Right click and open image in a new tab to view at full resolution.

|                                                      SDR                                                       |                                                        HLG                                                         |
| :------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------------: |
| <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/33TJ_20150705_191438_366/sdr_+3ev.png"> | <img style="transform:rotate(90deg);margin-top:6.25%" src="./pictures/33TJ_20150705_191438_366/sdr_log_+3ev.png">  |
|                          <img src="./pictures/6G7M_20150421_121002_835/sdr_+3ev.png">                          |                          <img src="./pictures/6G7M_20150421_121002_835/sdr_log_+3ev.png">                          |
| <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/0132_20160917_184610_200/sdr_+3ev.png"> | <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/0132_20160917_184610_200/sdr_log_+3ev.png"> |

Images reconstructed in HLG space.

|                                                    HSV HLG                                                     |                                                    LCh HLG                                                     | CNN                                                                                                            |
| :------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------: | -------------------------------------------------------------------------------------------------------------- |
| <img style="transform:rotate(90deg);margin-top:6.25%" src="./pictures/33TJ_20150705_191438_366/hsv_+3ev.png">  | <img style="transform:rotate(90deg);margin-top:6.25%" src="./pictures/33TJ_20150705_191438_366/lch_+3ev.png">  | <img style="transform:rotate(90deg);margin-top:6.25%" src="./pictures/33TJ_20150705_191438_366/cnn_+3ev.png">  |
|                          <img src="./pictures/6G7M_20150421_121002_835/hsv_+3ev.png">                          |                          <img src="./pictures/6G7M_20150421_121002_835/lch_+3ev.png">                          | <img src="./pictures/6G7M_20150421_121002_835/cnn_+3ev.png">                                                   |
| <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/0132_20160917_184610_200/hsv_+3ev.png"> | <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/0132_20160917_184610_200/lch_+3ev.png"> | <img style="transform:rotate(90deg);margin-top:6.25%;" src="./pictures/0132_20160917_184610_200/cnn_+3ev.png"> |

## References

[1] “ESSENTIAL PARAMETER VALUES FOR THE EXTENDED IMAGE DYNAMIC RANGE TELEVISION (EIDRTV) SYSTEM FOR PROGRAMME PRODUCTION ARIB STANDARD ,” 03-Jul-2015. [Online]. Available: <https://www.arib.or.jp/english/html/overview/doc/2-STD-B67v1_0.pdf.>

[2] Cyril, “Recovering Highlights with dcraw using LCH blending,” _Blown-highlight recovery with dcraw in LCH coordinates_, 14-Apr-2007. [Online]. Available: <http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html.>

[3] U. Fuchs and N. K. B. Jensen, “UFRaw,” _UFRaw_. 17-Jun-2015. <http://ufraw.sourceforge.net/Guide.html>

[4] G. Eilertsen, J. Kronander, G. Denes, R. K. Mantiuk, and J. Unger, “HDR image reconstruction from a single exposure using deep CNNs,” _ACM Transactions on Graphics,_ vol. 36, no. 6, pp. 1–15, 2017.

[5][6] S. W. Hasinoff, D. Sharlet, R. Geiss, A. Adams, J. T. Barron, F. Kainz, J. Chen, and M. Levoy, “Burst photography for high dynamic range and low-light imaging on mobile cameras,” _ACM Transactions on Graphics,_ vol. 35, no. 6, pp. 1–12, Nov. 2016.
<https://dl.acm.org/doi/10.1145/2980179.2980254>

[7] Facebook AI Research, “Detectron 2,” GitHub. [Online]. Available: <https://github.com/facebookresearch/detectron2>

## Project Artifacts

- [Main GitHub Repo](https://github.com/CS766-Final/CS766-Final-Project)

- [Test Program for Various Highlight Reconstruction Methods Repo](https://github.com/eddieab/hl_rec)

- [Initial Proposal](proposal.md)

- [Midterm Report](midterm_report.md)

[comment]: # "These are the reference style links to references."
[ref 1]: https://www.arib.or.jp/english/html/overview/doc/2-STD-B67v1_0.pdf
[ref 2]: http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html
[ref 3]: http://ufraw.sourceforge.net/Guide.html
[ref 4]: https://dl.acm.org/doi/10.1145/3130800.3130816
[ref 5]: http://hdrplusdata.org/dataset.html
[ref 6]: https://static.googleusercontent.com/media/hdrplusdata.org/en//hdrplus.pdf
[ref 7]: https://github.com/facebookresearch/detectron2
