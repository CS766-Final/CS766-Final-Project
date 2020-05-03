# Software-Based Single Frame HDR Image Reconstruction

Edward Barton, Michelle Jensen, Daniel Kiel

## Problem Statement

Most practical usage of HDR imaging has been in photography and cinema using different forms of bracketing and frame blending. However, recent developments in sensor technology, like sensors with dual-gain ADCs and non-linear sensitivity, single-shot HDR is increasingly pervasive. Even with these hardware-based advancements, there is still more information that can be recovered in software. HDR imaging techniques are showing their importance in computational imaging and computer vision applications. For instance, we will be focusing on object detection and recognition in saturated regions for applications such as autonomous vehicles.

The current state-of-the-art in still image HDR is a derivation of bracketing that does mosaic alignment and exposure merge, followed by an image processing pipeline that includes demosaic and tone-mapping. In single-shot HDR, using a skip-connected autoencoder deep convolutional neural network (CNN), the reconstruction function is learned. The single-shot method is restricted to highlight reconstruction without denoising. The state-of-the-art in motion relies heavily on HDR sensor technology. For a high-frame-rate camera, exposure bracketing can be employed to create a standard frame rate video from frame blending while using optical flow combined with patch-based synthesis for motion compensation. In addition, a similar function based on alternating exposures is learned through a deep neural network.

We narrowed the scope of our investigation to the reconstruction of a high dynamic range (HDR) image from a single Bayer color filtered frame in software. In the majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters with a repeating 2x2 block: red, green, green, blue. The resulting frame requires interpolation to fill in the remaining two-thirds of color information to create an RGB image. During this interpolation, a white balancing operation is performed that often boosts data recorded in either or both of the red and blue channels beyond 1.0 (the max value in standard dynamic range systems). This additional highlight information in the white balanced image can be used to interpolate missing lightness detail and hue in other clipped channels.

## Methods

### Pixel-wise Separation of Lightness and Color Properties

The pixel-wise methods used are based on the ability to separate lightness information from the colorfulness and hue information that makes up a color. The methods rely on CIE LCh [[1]][Ref 1] and HSV [[2]][Ref 2] as the reconstruction color spaces, respectively. Though minor implementation details differ – RGB to LCh conversion requires multiple color transforms – the methods follow the same general algorithm. We copy an unclipped, white-balanced image in camera RGB space and clip it at the defined min and max values for the scale. A conversion to the reconstruction space is applied to both copies of the image. In the reconstruction space we stack the lightness channel (L in LCh, V in HSV) of the unclipped representation with the linearly interpolated color channels of the clipped and unclipped representation. We then apply the reverse transform from the reconstruction space to RGB space. These pixel-wise reconstructions follow white balance in the camera pipe, but precede any digital gain stage and final display RGB space conversions (sRGB, BT.709, etc).

In the HSV method, one implementation that was found in the open-source community in the app dcraw, used linear interpolation of clipped values and unclipped values to create the reconstruction. In our method, we did no linear interpolation as to recover the full lightness information given by the sensor. Due to the nature of HSV channels not being perceptually linear and being relative values, lightness changes with hue, as does saturation. We also found that using the clipped saturation instead of linearly interpolating between the two representations eliminated harsh artifacting at channel clipping boundaries. 

**TODO: PUT SATURATION ARTIFACTING ALONG WITH FULL HSV RECONSTRUCTION**

The LCh method is an absolute transform when specified with a white point. In our case D65 was used. It is perceptually linear and device agnostic. Meaning a linear change in one channel will result in a linear visually perceived change in a space that is independent of acquisition or display. The combination of these two design choices mean the three channels are perceptually distinct from each other, unlike HSV where lightness varies between hues. This method involved combining the lightness channel of the unclipped image with the hue and colorfulness of the clipped image without linear interpolation. Despite the extra color transforms and non-linear transformations, we saw no drop in performance when compared to HSV reconstruction.

**TODO: PUT LCH RECONSTRUCTION**

### Deep Convolutional Neural Network

The work done by Eilertsen et al. [[3]][Ref 3] involves using a "fully convolutional deep hybrid dynamic range autoencoder network". The encoder converts SDR input to a latent set and the log transform skip connections help the decoder to reconstruct the HDR image in log domain. The skip connections help to restore lightness information as the fine detail is lost through the down-sampling at each step of the encoder. This network was trained on rasterized, display space images that are output from the camera raw pipeline. This is in opposition to the pixel-wise methods which operate on camera RGB space images before any useful data can be clipped after white-balance and sRGB transform.

**TODO: PUT CNN RECONSTRUCTION**

## Performance and Evaluation

The dataset used is a subset of the the “HDR+ Burst Photography Dataset” [[4]][Ref 4][[5]][Ref 5] compiled and created by a Google Research team. We chose this dataset in part for the number of images, but mostly because the images are largely unmodified raw data and carry color transform metadata needed for our pipeline. Most of the images are around 12MP at a 4:3 ratio. We used the first image from each burst set which contained an average of 6 frames per burst.

The pixel-wise methods are the more compute efficient algorithms, as expected. **might need to change this to Dan's numbers** On a 2.9GHz 6th Gen Intel i7 MacBook Pro using SIMD instructions, the full pipeline from 4:3 ratio, 4K clipped raw binned to 1K reconstructed log space took roughly 4 ms per image. This translates to about 250 fps. Due to the nature of the Halide language, there is no way to perform branch statements without pre-computing possible outcomes. Therefore, both LCh and HSV reconstructions are performed and the correct representation is chosen based on used input. This unified pipeline run on the whole dataset of 3640 DNGs ran at 19.4287 sec, or roughly 187 fps. The same unified pipeline modified for a 2K output resolution averaged roughly 61 fps.

We did not modify the CNN or create an optimized implementation as the reference implementation is written to use CUDA instructions via Tensorflow. The HDRCNN took roughly **insert ms per image**, translating to roughly **insert fps here** on **insert resolution here** images. This is markedly slower than pixel-wise methods. However, the drop in performance might be reconciled in evaluation of the final recovery.

With the pixel-wise methods, it's possible to define a mathematical upper-bound on the number of photographic stops (EV) of light that are recoverable in linear space for each image. A photographic stop is equal to a doubling of light. For HSV the calculation is fairly simple. It is the base-2 log of the ratio between the maximum and minimum RGB white balance multipliers. This is because the HSV conversion uses the maximum intensity of the three RGB channels for the lightness representation. Therefore, if all channels are fully saturated at 1.0 before white balance, then the lightness representation will be the channel with the highest white balance multiplier. In most cases the minimum is 1 (the green channel), and the expression can be reduced to use just the max.

![wb = \begin{bmatrix}m_r \\ m_g \\ m_b\end{bmatrix}\;m \in \R](https://render.githubusercontent.com/render/math?math=wb%20%3D%20%5Cbegin%7Bbmatrix%7Dm_r%20%5C%5C%20m_g%20%5C%5C%20m_b%5Cend%7Bbmatrix%7D%5C%3Bm%20%5Cin%20%5CR)

![\log_2{\max(wb)}](https://render.githubusercontent.com/render/math?math=%5Clog_2%7B%5Cmax(wb)%7D)

LCh recovery depends less on the raw RGB intensities and their corresponding multipliers. This is because of the intermediate color transform from RGB to CIE XYZ before the LCh transform. The Y channel of XYZ represents the linear luminance, while X and Z contain all chromaticities at that luminance. Y is the dot product of the white balanced RGB values and the second row of the camera RGB to XYZ transform matrix. This transform matrix is derived from the color metadata stored in the files. From this we can bound the reconstruction in XYZ space using a similar method above. The dot product tends to produce values less than just taking the max and leads to softer edges and transitions, creating smoother roll-off.

![\log_2{Y}](https://render.githubusercontent.com/render/math?math=%5Clog_2%7BY%7D)

Something to note with the pixel-wise methods, is that they can only reconstruct hue and saturation values when just one channel in the raw image is clipped. Once two channels clip, these methods only recover lightness. This results in gray regions between the hue restored pixels and full lightness pixels. The CNN and classical methods that take regions into account will fare much better in this regard, except in their failure cases where the result is non-deterministic.

Bounding the usable recovery range of the CNN is more difficult as we don't know the function used for the recovery. We do know, however, that the failure cases for the network result in unusable images entirely. In cases where large portions of the frame are clipped, tearing can occur. Whereas in the worst case of the pixel-wise methods, we will have patches of gray, but still discernable transitions. Despite these cases, HDRCNN shows great ability to recover hue and detail across reasonably sized clipped regions.

**TODO: SHOW CNN IMAGE TEARING AND GOOD RECOVERY**

## Downstream Application: Detectron2

## Conclusions

## References

[1] Cyril, “Recovering Highlights with dcraw using LCH blending,” _Blown-highlight recovery with dcraw in LCH coordinates_, 14-Apr-2007. [Online]. Available: <http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html.>

[2]  U. Fuchs and N. K. B. Jensen, “UFRaw,” _UFRaw_. 17-Jun-2015. <http://ufraw.sourceforge.net/Guide.html>

[3] G. Eilertsen, J. Kronander, G. Denes, R. K. Mantiuk, and J. Unger, “HDR image reconstruction from a single exposure using deep CNNs,” _ACM Transactions on Graphics,_ vol. 36, no. 6, pp. 1–15, 2017.

[4][5] S. W. Hasinoff, D. Sharlet, R. Geiss, A. Adams, J. T. Barron, F. Kainz, J. Chen, and M. Levoy, “Burst photography for high dynamic range and low-light imaging on mobile cameras,” _ACM Transactions on Graphics,_ vol. 35, no. 6, pp. 1–12, Nov. 2016.
<https://dl.acm.org/doi/10.1145/2980179.2980254>

## Gallery

|                             SDR                              |                           SDR HLG                            |                           HSV HLG                            |                           LCh HLG                            |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| <img width="100%" style="transform:rotate(90deg);" src="https://dl.boxcloud.com/api/2.0/internal_files/660778378772/versions/700715116772/representations/png_paged_2048x2048/content/1.png?access_token=1!BHYzZsEDEmKTf6NLuwKKSmYISDvBBpipWOZYJSwverbQSjOTWXnxtqcCQm3WmVLANXfKig-GNk2U3YGqN9nUHvpJvP8Gl0v640C7lodE7tK5HHgMMQ0XObtQl3hve6py2ifHoRsJDNZrLQ4rSS1Lpmw6Sx2vohIGUvWNh828uWCkRh8SXstEIbaLcLLnQ-5NP1kkRjVCYF2QQTMSv1uMHsbyoTIMEevhREUeljr--oJQgtODB1mV-5Xj9xOnHZwJGRL1SnGncMqlUaayul0bCNZ7a3f6rYhNpQkG8Av4DLHlAfcarGx-b6vix272gAgFsMHLpHjkoe_V9KybUtmchpta3vPljd6LWhhx_z_XqcfspEYqWTy41x2GbvQYCCDPkj-kvaznhL4cuLgX37SBKrNQY44vLB7wIX2JjlMe_kM2_ELjqbiH-vnROzUr0JxKagdo-ZxqPZGalTqh4dXm4KyjP0lmQqeCVtq1_27uaRHdD20nsF09FJphH0jpTb7mPr-x6edxh6QGsi3yYfRjzJyZVMlmU_Lxf5qMCi3CNjCF3859pNbFHH0bW26X5eyAKwQ.&box_client_name=box-content-preview&box_client_version=2.40.0"> | <img width="100%" style="transform:rotate(90deg);" src="https://dl.boxcloud.com/api/2.0/internal_files/660774404950/versions/700710877750/representations/png_paged_2048x2048/content/1.png?access_token=1!NoyHlHHTMLv2S1cTquQoLLEX1U6K4yi26h2uACBoP2QGEmVcwnaRgY78D5At1kPtmxQVVey9EkqGOi-4mWDpmhBalp6lojA6ZD_PbFECU7QSQW2_DDVEHtEwEycFfnEDSyu1cTvFqidNpgS7O2HjqiCGCC5BUFAyxOoswGuir1CdaEfmqBTepC3EmKDf268z_ACw8OlWbGT6Vf4leafHYZq7c8vzCM7MFyRMWPYtQAAd2PN7A2DasYJgLbz08YHP6bS40Xw-AB2QC4KBBPYVTsz4du1px7Bu0rd7svOPZpCK1Mh6G5YAAFNHPgaq_HBVTNVQ4MkrrM-PdR4RpDAtLOdesvcRICPPudeMNJx1Ovv9MhGMjDNp5cvXjnOhrtLHCnirquGkyidFeCvbC-WfktRvETKYCXTtvI4SeXlCuCiLHspxwXluq3U2VDmSLb4PvaBrSlWIsmeAc10PPpUUR3CBgdjcu8wfOk7ShbEH4725Mu6XJhnyL1IQELnGGeh1BT5X5YrpAQZDkRih1B5nHxhm7-9_QpkSIJx9zsrkOpoR8lsBYg6yvJuG8ge6i0iJWTs.&box_client_name=box-content-preview&box_client_version=2.40.0"> | <img width="100%" style="transform:rotate(90deg);" src="https://dl.boxcloud.com/api/2.0/internal_files/660778428725/versions/700715188325/representations/png_paged_2048x2048/content/1.png?access_token=1!_BzXCpfHop7hMI3r287uyfs5rtkUsz1dCLjDl2DMtp_0s1bOjO-Y0V8SSz7tbfvQeHi3ldK1w03-BetMi6i1ecazQdrb7_gE5d8Bk_EM8HAc3z6grZuG_J9brWxfaBfT5xATa4fqjJLt3FSTIjHsPQRB2m_gAciHyFcywvMHMCoRSQwFzrU5nSmxJBMs60AfTc3Bnl9Om55sgkeZWL9IyVrhHRiFO3yQeMYRqT950UyT1-gWMS6vBYCoALfe6KHnZXmQYGbr1yC4YjnmWepSCknecB_8WsYLZm3GZNRGXpWaojIMp9iAt-pWXvN4IuM_YQ7L34LwaXu37KZEfrtF7wZZCXUrKJ1j5hGxW-wezAZKaP2Z_viPXuyFo2R7rSjzzMKgpqf8oX4yAaM5V7EGhD5hzvK5MIZML83oLggCyeLFh1zgxTFr97_KGr5C_HASSUbnPF89NZQoQsqVKQgdsVtO5cxahPeZRZnfnGAc1Hyha_4Bh2MELYUmdOEpLPbH_iznztfcjTY_4SYnBdrivnjxtOv45WEmXq_Md3B9d2mqEwF8hGvY-2Xz89hSx2eQSV8.&box_client_name=box-content-preview&box_client_version=2.40.0"> | <img width="100%" style="transform:rotate(90deg);" src="https://dl.boxcloud.com/api/2.0/internal_files/660778491486/versions/700715231886/representations/png_paged_2048x2048/content/1.png?access_token=1!bj0ovoKFqjTm6Rwy1Kd_wReI76tC4kIVHigrFE2TDli5dGHaG23DTqr3c8X2zLZXU0oto9htZpevGJ45_Sxsi5KmjeEfBTq8WSpcUSj8TNq7t49oYCg-OTeKHeOC5DuGwbb5XmUyMBdLzg0O0gLpWnXmKHBN_ctxq1Qm1JTDk6mwXAGN4v7AIfC-cerAOvLzVLV5lhmi_600w08wrYyszACNceKQbZ0-xYxFfL4hphF0cZYsLKlsjL9xUT_lxOp3hh6BQ3_4MIJRwbSp-mT7bLurkZOS6g537bbrjzyW0CAPh9_g9XDrhT47y9Fugcm_QHeP5sI2IEIT5oI8cRr_WFlA8RHSUMOZhYPort1C4mma3Sczb-7hCdcHnqAfbHjcyz1aDrSOpr-cC2N1arO2NpydfF8edrycvh8RDQv72Uj1lNBpFhW548MWyPPnAKRUlUw_FtoxVPRceAJ-IjZEFwjmklQ1_noM2HtFXYeMh06UW73PE-VdPalfuNlVbb44a2G1TiemZqQvvnYzMJ32D3xFpmwAymAtfs83fvCS4ogpjXGAXAgJLiG8gWe-jF37RPE.&box_client_name=box-content-preview&box_client_version=2.40.0"> |
|                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |
|                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |                  <img width=256 src="url">                   |

## Project Artifacts

* [GitHub Repo](https://github.com/CS766-Final/CS766-Final-Project)

* [Initial Proposal](proposal.md)

* [Midterm Report](midterm_report.md)

[comment]: # (These are the reference style links to references.)
[Ref 1]: <http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html>

[Ref 2]: <http://ufraw.sourceforge.net/Guide.html>

[Ref 3]: https://dl.acm.org/doi/10.1145/3130800.3130816

[Ref 4]: <http://hdrplusdata.org/dataset.html>

[Ref 5]: <https://static.googleusercontent.com/media/hdrplusdata.org/en//hdrplus.pdf>