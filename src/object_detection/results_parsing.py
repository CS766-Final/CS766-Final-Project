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

    # # Combining the multiple result sets
    # with open("../subset.json") as f:
    #     imgs = json.load(f)

    # with open(os.path.join(path,"all_results_all.json")) as f:
    #     all_results = json.load(f)

    # with open(os.path.join(path,"all_results_sdrlog0.json")) as f:
    #     sdrlog0 = json.load(f)

    # for img in imgs:
    #     all_results[img].update(sdrlog0[img])


    # # Write all results to one file
    # with open(os.path.join(path,'all_results_all.json'), 'w+') as f:
    #         f.write(json.dumps(all_results))
    

    with open(os.path.join(path,"all_results_all.json")) as f:
        all_results = json.load(f)

    stats = {
        2: {
            "cnn":[],
            "hsv":[],
            "lch":[]
        },
        3: {
            "cnn":[],
            "hsv":[],
            "lch":[]
        }
    }

    for gain in stats:
        for img,results in all_results.items():
            cnn = results[f"cnn_+{gain}ev"]
            hsv = results[f"hsv_+{gain}ev"]
            lch = results[f"lch_+{gain}ev"]
            sdr_log = results[f"sdr_log_+{gain}ev"]

            classes = {}
            for method in [cnn,hsv,lch,sdr_log]:
                for detected_object in method:
                    classes[detected_object["pred_class"]] = 1
            

            averages = {}
            for pred_class in classes:
                for method_name,method in zip(["cnn","hsv","lch",'sdr_log'],[cnn,hsv,lch,sdr_log]):
                    found_objects = [candidate["score"] for candidate in method if candidate["pred_class"]==pred_class]
                    if method_name in averages:
                        averages[method_name].update({pred_class:(sum(found_objects)/len(found_objects) if len(found_objects)>0 else 0)})
                    else:
                        averages[method_name] = {pred_class:(sum(found_objects)/len(found_objects) if len(found_objects)>0 else 0)}


            differences = {}
            for pred_class in classes:
                for method_name in ["cnn","hsv","lch"]:
                    if averages[method_name][pred_class] > 0 and averages['sdr_log'][pred_class] > 0:
                        if method_name in differences:
                            differences[method_name].update({pred_class:(averages['sdr_log'][pred_class]-averages[method_name][pred_class])})
                        else:
                            differences[method_name] = {pred_class:(averages['sdr_log'][pred_class]-averages[method_name][pred_class])}


            for method_name in differences:
                stats[gain][method_name].append(sum(differences[method_name].values())/len(differences[method_name].values()))


    for gain in stats:
        for method_name in stats[gain]:
            stats[gain][method_name] = list(map(lambda x: 0 if x < 0 else 1, stats[gain][method_name]))
            stats[gain][method_name] = (sum(stats[gain][method_name]),len(stats[gain][method_name]))

    print(stats)