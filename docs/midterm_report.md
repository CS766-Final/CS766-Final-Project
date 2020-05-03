# **Midterm Report**

 Eddie Barton, Michelle Jensen, and Dan Kiel

### Problem Statement

We will be investigating the reconstruction of a high dynamic range (HDR) image from a single Bayer color filtered frame. In the majority of digital single-sensor cameras, the sensor captures color via mosaicked color filters with a repeating 2x2 block: red, green, green, blue. The resulting frame requires interpolation to fill in the remaining two-thirds of color information to create an RGB image. During this interpolation, a white balancing operation is performed that often boosts data recorded in either or both of the red and blue channels beyond 1.0 (the max value in standard dynamic range systems). This additional highlight information in the white balanced image can be used to interpolate missing lightness detail and hue.

Most practical usage of HDR imaging has been in photography and cinema using different forms of bracketing and frame blending. However, recent developments in sensor technology, like sensors with dual-gain ADCs and non-linear sensitivity, single-shot HDR is increasingly pervasive. Even with these hardware-based advancements, there is still more information that can be recovered in software. HDR imaging techniques are showing their importance in computational imaging and computer vision applications. For instance, we will be focusing on object detection and recognition in saturated regions for applications such as autonomous vehicles.

The current state-of-the-art in still image HDR is a derivation of bracketing that does mosaic alignment and exposure merge, followed by an image processing pipeline that includes demosaic and tone-mapping. In single-shot HDR, using a skip-connected autoencoder deep convolutional neural network (CNN), the reconstruction function is learned. The single-shot method is restricted to highlight reconstruction without denoising. The state-of-the-art in motion relies heavily on HDR sensor technology. For a high-frame-rate camera, exposure bracketing can be employed to create a standard frame rate video from frame blending while using optical flow combined with patch-based synthesis for motion compensation. In addition, a similar function based on alternating exposures is learned through a deep neural network.

### Project Approach

We first plan to build from naïve classical pixel-wise approaches that interpolate detail from a single pixel. Next, we will evaluate classical region-based methods that take pixels from neighboring saturated regions into consideration. In addition, we will investigate modern approaches built on machine learning. To determine the applicability of the single shot HDR methods to our goal of object detection, we will test how well object detection works on the output of the previously described processes.

### Current Progress

So far the images we have tested have been a couple that we had lying around and were good enough to ensure that our overall process is working correctly. We are currently working on sourcing images from the “HDR+ Burst Photography Dataset” [[5]][Ref 5] [[6]][Ref 6] compiled and created by a Google Research team. We chose this dataset in part for the sheer number of images, but mostly because we can get the images as DNG that include all the information we need to do the color mapping. We will end up taking a subset of this dataset that includes both objects that Detectron2 is able to detect as well as objects that are close to being blown out in the highlights.

To process the images, we work directly from camera raw images in the Adobe DNG format. A crude raw pipeline was implemented using rawpy to extract the mosaiced image and the necessary metadata for color transforms. As the focus of this project is on real-time methods for use in embedded/low-compute systems, we perform 2-stage 2x2 pixel binning as opposed to high detail demosaic. This yields ~2MP images when working from the Google HDR+ dataset. We simulate ADC clipping with an early gain stage in the raw pipeline. This will allow us to determine the level of overexposure at which each method can no longer produce detectable objects with good confidence. We will also need to determine what a ‘good’ confidence is for the posed problem. Reconstructed images result in values greater than 1.0 meaning we must encode the data such that all values are able to be written to 8-bit files. In the figures below we encode the SDR image with both a standard 2.2 gamma power curve and Hybrid Log-Gamma. [[10]][Ref 10] The reconstructed images are all encoded with HLG. HLG was chosen because of similarity in characteristic to standard gamma curves while also being able to encode the range 0.0 to 12.0 before clipping. This has been sufficient for our purposes, but it is possible that we can exhaust the range of this encoding, so other encodings will be taken into consideration.

The pixel-wise methods used are based on the ability to separate lightness information from the colorfulness and hue information that makes up a color. The methods rely on the CIE LCh [[1]][Ref 1] and HSV [[2]][Ref 2] as the reconstruction color spaces, respectively. Though minor implementation details differ – RGB to LCh conversion requires multiple color transforms – the methods follow the same general algorithm. We copy an unclipped, white-balanced image in camera RGB space and clip it at the defined min and max values for the scale. A conversion to the reconstruction space is applied to both copies of the image. In the reconstruction space we stack the lightness channel (L in LCh, V in HSV) of the unclipped representation with the color channels of the clipped representation. We then apply the reverse transform from the reconstruction space to RGB space. These pixel-wise reconstructions follow white balance in the camera pipe, but precede any digital gain staging and final display RGB space conversions (sRGB, BT.709, etc).

![Comparison of reconstructions and encodings of the same image](/pictures/midterm_report_collage.png)

<img src = "docs/pictures/midterm_report_collage.png">

Initial impressions are that HSV reconstruction performs best for visual quality and computational efficiency. The method uses the maximum of R, G, and B to construct the lightness while LCh works from a linear combination of the three to construct the lightness values. This along with the cube root encoding in the LCh transform can explain the softer roll-off and reduced lightness values when compared to HSV. This higher contrast in HSV leads us to the hypothesis that it will perform better with object detection since it is better suited to reconstruct distinct edges.

In the coming weeks we aim to implement the gradient domain based reconstruction method. [[3]][Ref 3] It requires solving Dirichlet conditioned boundary value problems over clipped regions. The difficulty lies in fully understanding the BVP’s described and then writing these in a computationally efficient manner. We have reached out to some knowledgeable in this subject and await replies. We are considering excluding this method if quick enough progress is not made. The CNN based method from Eilertsen et al. [[4]][Ref 4] is running successfully using CUDA with the authors’ dataset. In the coming days we will test images from the HDR+ dataset.

Instead of implementing our own edge and object detection system as originally planned, we have decided to use Detectron2, FAIR’s (Facebook AI Research) state-of-the-art object detection system. [[7]][Ref 7] Primarily because it is more advanced and may prove closer to a situation of computer vision applications like autonomous driving. Other methods such as detection using correlation filters [[11]][Ref 11] are still under consideration due to our goal of real-time computation.

### Project Performance Evaluations

The final goal is to determine which HDR detail reconstruction works best in the detection of objects that may have been lost due to the overexposed parts of the image. This will be determined by two criteria: 1)  whether or not the object is detected and  2) the confidence interval given by the detection method. We decide not to measure metrics of the reconstructed image against the ground truth because these do not necessarily directly correlate to the detection method indicating an obstruction. However, if the detection algorithm can indicate and identify the obstruction correctly, that reconstruction produces non-negligible spatial detail.  In addition, we will also be benchmarking each reconstruction method. Hardware optimized versions must be written. We are considering Numba and Halide as the implementation languages.

### New Project Timeline

* **April 1st:** Project Mid-Term Report Due

* **April 1st - April 20th:** Create Benchmarking Tools, Build Pipeline, Try Gradient Domain Approach

* **April 20th - April 26th:**  Finishing Touches on Project - Get examples and data by running pipeline and benchmarking tools on our set of images

* **April 27th - May 4th:** Work on Final Webpage and Video Presentation

* **May 4th:** Final Project Webpage Due & Video Presentation Due

### References

[1] Cyril, “Recovering Highlights with dcraw using LCH blending,” _Blown-highlight recovery with dcraw in LCH coordinates_, 14-Apr-2007. [Online]. Available: <http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html.>

[2]  U. Fuchs and N. K. B. Jensen, “UFRaw,” _UFRaw_. 17-Jun-2015. <http://ufraw.sourceforge.net/Guide.html>

[3] M. N. Rouf, C. Lau, and W. Heidrich, “Gradient Domain Color Restoration of Clipped Highlights,” _Computer Science at University of British Columbia._ [Online]. Available: <http://www.cs.ubc.ca/labs/imager/tr/2012/GradientDomainColorRestoration/.>

[4] G. Eilertsen, J. Kronander, G. Denes, R. K. Mantiuk, and J. Unger, “HDR image reconstruction from a single exposure using deep CNNs,” _ACM Transactions on Graphics,_ vol. 36, no. 6, pp. 1–15, 2017.

[5][6] S. W. Hasinoff, D. Sharlet, R. Geiss, A. Adams, J. T. Barron, F. Kainz, J. Chen, and M. Levoy, “Burst photography for high dynamic range and low-light imaging on mobile cameras,” _ACM Transactions on Graphics,_ vol. 35, no. 6, pp. 1–12, Nov. 2016.
<https://dl.acm.org/doi/10.1145/2980179.2980254>

[7] Facebook AI Research, “Detectron 2,” GitHub. [Online]. Available: <https://github.com/facebookresearch/detectron2.>

[8] Kgo, “Tesla self-driving car fails to detect truck in fatal crash,” _ABC7 San Francisco,_ 01-Jul-2016. [Online]. Available: <https://abc7news.com/1410042/.>

[9] S. H. Naghavi and H. Pourreza, “Real-Time Object Detection and Classification for Autonomous Driving,” _2018 8th International Conference on Computer and Knowledge Engineering (ICCKE),_ 2018.

[10] “ESSENTIAL PARAMETER VALUES FOR THE EXTENDED IMAGE DYNAMIC RANGE TELEVISION (EIDRTV) SYSTEM FOR PROGRAMME PRODUCTION ARIB STANDARD ,” 03-Jul-2015. [Online]. Available: <https://www.arib.or.jp/english/html/overview/doc/2-STD-B67v1_0.pdf.>

[11] S. Han, M.-J. Kim, S. Park, and J. Paik, “Fast Vehicle Detection using Correlation Filters,” _IEIE Transactions on Smart Processing & Computing,_ vol. 6, no. 5, pp. 309–316, 2017.

[comment]: # (These are the reference style links to sites.)

[Ref 1]: <http://people.zoy.org/~cyril/dcraw_lchblend/highlight_recovery_dcraw_lch_patch.html>

[Ref 2]: <http://ufraw.sourceforge.net/Guide.html>

[Ref 3]: <http://www.cs.ubc.ca/labs/imager/tr/2012/GradientDomainColorRestoration/>

[Ref 4]: https://dl.acm.org/doi/10.1145/3130800.3130816

[Ref 5]: <http://hdrplusdata.org/dataset.html>

[Ref 6]: <https://static.googleusercontent.com/media/hdrplusdata.org/en//hdrplus.pdf>

[Ref 7]: <https://github.com/facebookresearch/detectron2>

[Ref 8]: <https://abc7news.com/1410042/>

[Ref 9]: <https://ieeexplore.ieee.org/document/8566491>

[Ref 10]: <https://www.arib.or.jp/english/html/overview/doc/2-STD-B67v1_0.pdf>

[Ref 11]: <https://www.researchgate.net/publication/323030631_Fast_Vehicle_Detection_using_Correlation_Filters>
