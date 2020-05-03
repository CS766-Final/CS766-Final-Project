import json
import os

if __name__ == "__main__":
    thing_classes=["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
    thing_classes_ints = list(range(len(thing_classes)))
    thing_classes_interest = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,25]

    path = "/media/djkong7/dataset/"

    # Original parsing to figure out subset images.
    # # Write all results to one file
    # with open(os.path.join(path,"all_results.save.json"), "r") as f:
    #     results = json.load(f)

    # candidate_imgs = {}
    # for result in results:
    #     for key,value in result.items():
    #         search = [i for i in thing_classes_interest if i in value["sdr_log_1"]["pred_classes"]]
    #         if len(search) > 0:
    #             candidate_imgs[key] = search

    # best = {key:val for key,val in candidate_imgs.items() if len(val) > 1}
    # print(sorted(list(best.keys())))


    # Combine all cnn_sdrlog results files due to oom issues while running detectron
    # all_results = []
    # with open("../subset.json") as f:
    #     imgs = json.load(f)

    # sub_dirs = sorted([os.path.join(path, img) for img in imgs])
    
    # for folder in sub_dirs:
    #     if 'results_cnn_sdrlog.json' in os.listdir(folder):
    #         with open(os.path.join(folder,'results_cnn_sdrlog.json')) as f:
    #             results = json.load(f)
            
    #         # Keep a master list of all results
    #         all_results.append({os.path.basename(folder):results})

    # # Write all results to one file
    # with open(os.path.join(path,'all_results_cnn_sdrlog.json'), 'w+') as f:
    #         f.write(json.dumps(all_results))

    # Combining the multiple result sets
    # with open("../subset.json") as f:
    #     imgs = json.load(f)

    # with open(os.path.join(path,"all_results_cnn_sdrlog.json")) as f:
    #     cnn_sdrlog = json.load(f)

    # with open(os.path.join(path,"all_results_hsv_lch.json")) as f:
    #     hsv_lch = json.load(f)

    # all_results = {}

    # for img in imgs:
    #     hsv_lch_dict = [dic for dic in hsv_lch if img in dic][0]
    #     cnn_sdrlog_dict = [dic for dic in cnn_sdrlog if img in dic][0]

    #     hsv_lch_dict[img].update(cnn_sdrlog_dict[img])

    #     all_results.update(hsv_lch_dict)

    # # Write all results to one file
    # with open(os.path.join(path,'all_results_all.json'), 'w+') as f:
    #         f.write(json.dumps(all_results))
    

    with open(os.path.join(path,"all_results_all.json")) as f:
        all_results = json.load(f)

    for img,results in all_results.items():
        for gain in [2,3]:
            cnn = results[f"cnn_+{gain}ev"]
            hsv = results[f"hsv_+{gain}ev"]
            lch = results[f"lch_+{gain}ev"]
            sdr_log = results[f"sdr_log_+{gain}ev"]

            for found_object in sdr_log:
                candidates = [candidate for candidate in cnn if found_object["pred_class"] == candidate["pred_class"]]
                for candidate in candidates:
                    match = True
                    for cand_pos,obj_pos in zip(candidate["box"],found_object["box"]):
                        match = (match and (obj_pos-2 <= cand_pos <= obj_pos+2))

                    if match:
                        found_object["score"]-candidate["score"]



