# You may need to restart your runtime prior to this, to let your installation take effect
# Some basic setup:
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import cv2
import random

# import some common detectron2 utilities
from detectron2 import model_zoo
#from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

from matplotlib import pyplot as plt
import json

import detectron2.data.transforms as T
from detectron2.modeling import build_model
from detectron2.checkpoint import DetectionCheckpointer
import torch
import os
import json
class DefaultPredictor:
    """
    Create a simple end-to-end predictor with the given config that runs on
    single device for a single input image.
    Compared to using the model directly, this class does the following additions:
    1. Load checkpoint from `cfg.MODEL.WEIGHTS`.
    2. Always take BGR image as the input and apply conversion defined by `cfg.INPUT.FORMAT`.
    3. Apply resizing defined by `cfg.INPUT.{MIN,MAX}_SIZE_TEST`.
    4. Take one input image and produce a single output, instead of a batch.
    If you'd like to do anything more fancy, please refer to its source code
    as examples to build and use the model manually.
    Attributes:
        metadata (Metadata): the metadata of the underlying dataset, obtained from
            cfg.DATASETS.TEST.
    Examples:
    .. code-block:: python
        pred = DefaultPredictor(cfg)
        inputs = cv2.imread("input.jpg")
        outputs = pred(inputs)
    """

    def __init__(self, cfg):
        self.cfg = cfg.clone()  # cfg can be modified by model
        self.model = build_model(self.cfg)
        self.model.eval()
        self.metadata = MetadataCatalog.get(cfg.DATASETS.TEST[0])

        checkpointer = DetectionCheckpointer(self.model)
        checkpointer.load(cfg.MODEL.WEIGHTS)

        self.transform_gen = T.ResizeShortestEdge(
            [cfg.INPUT.MIN_SIZE_TEST, cfg.INPUT.MIN_SIZE_TEST], cfg.INPUT.MAX_SIZE_TEST
        )

        self.input_format = cfg.INPUT.FORMAT
        assert self.input_format in ["RGB", "BGR"], self.input_format

    def __call__(self, original_images):
        """
        Args:
            original_images (list(np.ndarray)): a list of images of shape (H, W, C) (in BGR order).
        Returns:
            predictions (dict):
                the output of the model for each image in the list.
                See :doc:`/tutorials/models` for details about the format.
        """
        with torch.no_grad():  # https://github.com/sphinx-doc/sphinx/issues/4258
            inputs = []
            for original_image in original_images:
                # Apply pre-processing to image.
                if self.input_format == "RGB":
                    # whether the model expects BGR inputs or RGB
                    original_image = original_image[:, :, ::-1]
                height, width = original_image.shape[:2]
                image = self.transform_gen.get_transform(original_image).apply_image(original_image)
                image = torch.as_tensor(image.astype("float32").transpose(2, 0, 1))

                inputs.append({"image": image, "height": height, "width": width})
            return self.model(inputs)


if __name__ == "__main__":
    cfg = get_cfg()
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml")
    predictor = DefaultPredictor(cfg)

    all_results = {}
    #image_names = ['cnn_+2ev','cnn_+3ev','sdr_log_+2ev','sdr_log_+3ev']
    #image_names = ['hsv_+2ev','hsv_+3ev','lch_+2ev','lch_+3ev']
    image_names = ['sdr_log_+0ev']
    # Path to top level dir containing dataset folders
    path = '/media/djkong7/dataset/'

    with open("../subset.json") as f:
        imgs = json.load(f)

    sub_dirs = sorted([os.path.join(path, img) for img in imgs])

    for folder in sub_dirs:
        #path_to_imgs = os.path.join(path,folder)

        if 'results_sdrlog0.json' in os.listdir(folder):
            continue

        print(folder)

        # Load all images into memory
        imgs = []
        for img in image_names:
            impath = os.path.join(folder, f'{img}.png')
            im = cv2.imread(impath)
            imgs.append(im)

        # Get predictions for each image
        outputs = predictor(imgs)

        # Compile the results
        results = {}
        for output,name,img in zip(outputs,image_names,imgs):
            # # We can use `Visualizer` to draw the predictions on the image.
            # v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
            # v = v.draw_instance_predictions(output["instances"].to("cpu"))
            # cv2.imshow("Detected image",v.get_image()[:, :, ::-1])
            # cv2.waitKey(0)

            # test = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
            # print(test)

            results[name] = []
            for box,score,pred_class in zip(output["instances"].pred_boxes.tensor.tolist(),output["instances"].scores.tolist(),output["instances"].pred_classes.tolist()):
                results[name].append(
                    {
                        "box": box,
                        "score": score,
                        "pred_class": pred_class
                    }
                )

        # Write results of current folder to file in that folder
        with open(os.path.join(folder,'results_sdrlog0.json'), 'w+') as f:
            f.write(json.dumps(results))


        # Keep a master list of all results
        all_results.update({os.path.basename(folder):results})



    # Write all results to one file
    with open(os.path.join(path,'all_results_sdrlog0.json'), 'w+') as f:
            f.write(json.dumps(all_results))

