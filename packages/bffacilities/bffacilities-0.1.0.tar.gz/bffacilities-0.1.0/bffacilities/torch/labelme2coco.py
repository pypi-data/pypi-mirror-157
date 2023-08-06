
import collections
import datetime
import glob
import uuid
import sys
import numpy as np
import labelme
import re
SubCategoryPatter = re.compile("(\w+)-(\w+|\d+)")

try:
    import pycocotools.mask as cocomask
except ImportError:
    print("Please install pycocotools:\n\n    pip install pycocotools\n")
    sys.exit(1)

class Labelme2Cocoer():
    """

    """
    def __init__(self, output_dir, cocomask=None, debug=False):
        """
        Arguments:
            output_dir(str)  annotations.json and image will store in this place
            
            cocomask(pytcocotools.mask): 
                @deprecated
        """
        self.output_dir = output_dir
        self.debug = debug
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(osp.join(output_dir, "JPEGImages"), exist_ok=True)
        now = datetime.datetime.now()

        ## coco data that will be write into annotations.json
        self._data_info = dict(
                description=None,
                url=None,
                version=None,
                year=now.year,
                contributor=None,
                date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            )
        self._data_licenses= [dict(url=None, id=0, name=None,)]
        self._data_images=[
                # license, url, file_name, height, width, date_captured, id
            ]
            # supercategory, id, name
        self._data_annotations=[
                # segmentation, area, iscrowd, image_id, bbox, category_id, id
            ]
        self._data_categories= None

    def classNameToId(self, labels_file, skeletondict=None):
        """
        @deprecated see setClassId

        读取 labels 文件，将 className 转换为 id，
        对于关键点名称，需要包含 Mask 名称作为前缀，并用 - 分隔

        对于关键点来说，必须有父类才行

        Currently keypoint labelname should be `xxx-1` or `xxx-2`, because it's
        easy to be ordered.

        Argument:
            labels_file (str): labels file loc,
        """
        class_id = -1  # class id 仅会给对象分配
        # dict to map class_name (str) to id (int)
        class_name_to_id = {} # key: class_name， 仅包含对象名, value: id
        categoriedict = {}
        with open(labels_file, "r") as f:
            for i, line in enumerate(f.readlines()):
                class_name = line.strip()   
                # 形如 class-subclass1
                if len(class_name) == 0:
                    continue
                
                if class_id == -1:
                    assert class_name == "__ignore__"
                    class_id += 1
                    continue

                matched = SubCategoryPatter.match(class_name)
                class_name_to_id[class_name] = class_id
                if matched is None:
                    # 检测为对象
                    categoriedict[class_id] = { 
                        "name": class_name, 
                        "supercategory": None,
                        "type": "object", 
                        "keypoints": [],
                    }
                    class_id += 1
                else:
                    # 检测为关键点
                    kp_name = class_name
                    class_name = matched[1]

                    class_id = class_name_to_id[class_name]
                    # keypoint name 也映射到相同的 id 
                    class_name_to_id[kp_name] = class_id

                    cat = categoriedict[class_id]
                    cat["type"] = "keypoint"
                    cat["keypoints"].append(kp_name)
        if self.debug:
            print("Class to id", class_name_to_id, "============")
            # raise ValueError("Test")
        self.class_name_to_id = class_name_to_id

        if self.debug:
            print("Categories Dict", categoriedict)

        categories = []
        skeleton = [] if skeletondict is None else skeletondict
        for class_id, cat in categoriedict.items():
            if cat["type"] == "object":
                categories.append({
                    "supercategory": cat["supercategory"], 
                    "id": class_id, 
                    "name": cat["name"],
                })
            elif cat["type"] == "keypoint":
                categories.append({
                    "supercategory": cat["supercategory"], 
                    "id": class_id, 
                    "name": cat["name"],
                    "keypoints": cat["keypoints"],
                    "skeleton": skeleton
                })

        self._data_categories = list(sorted(categories, key=lambda x: x["id"]))

        if self.debug:
            print("cats", self._data_categories, "============\n\n")

    def setClassId(self, class_dict):
        """ 默认背景 classId 为 0
        Args
            class_dict
            {
                "background": True, // default
                "instances": ["L1_1", "L1_2", "L1_3],
                // L1_1 L1_2 分别有关键点, L1_3 没有
                "keypoints": {
                    "L1_1": ["L2_1", "L2_2"]
                    "L1_2": ["L2_3"]
                },
                "skeleton": {

                }
            }
        """

        background = class_dict.get("background", True)
        categories = []
        if background:
            categories.append({
                "supercategory": None,
                "id": 0,
                "name": "_background_"
            })
        class_name_to_id = {
            "_background_": 0,
        }

        instances = class_dict["instances"]
        keypoints = class_dict["keypoints"] if "keypoints" in class_dict else {}
        skeleton = class_dict["skeleton"] if "skeleton" in class_dict else {}

        for i, ins_name in enumerate(instances):
            kps = keypoints.get(ins_name, [])
            skt = skeleton.get(ins_name, [])
            categories.append({
                "supercategory": None,
                "id": i + 1,
                "name": ins_name,
                "keypoints": kps,
                "skeleton": skt
            })
            class_name_to_id[ins_name] = i + 1
        self._data_categories = categories

        self.class_name_to_id = class_name_to_id
        keymap = {}
        for obj, kps in keypoints.items():
            for kp in kps:
                keymap[kp] = obj
        self._class_dict = class_dict
        self._class_dict["keymap"] = keymap

    def _kps_from_categories(self, cls_name):
        for categories in self._data_categories:
            if categories["name"] == cls_name:
                return categories["keypoints"]

    def _extractAnno(self, label_file, imshape):
        """
        this function can only find keypoints for each segclass on one image,
        
        if multiple segmentation class is on one image, group id must be set in labelme

        one part of the keypoints of segmentations will be saved

        Returns
            masks: key 为 (label, group_id)，value 为 mask

            keypoints: key 为 object class name，value 为 list((label_name, points))
        """
        masks = {}
        segmentations = collections.defaultdict(list)  # for segmentation
        keypoints = {}

        for shape in label_file.shapes:
            shape_type = shape.get("shape_type", "polygon")

            points = shape["points"]
            label = shape["label"]
            group_id = shape.get("group_id")

            if shape_type == "point": 
                # keypoint  is special
                # matched = SubCategoryPatter.match(label)
                segclass_name = self._class_dict["keymap"][label]
                if segclass_name not in keypoints:
                    keypoints[segclass_name] = []
                # points[0] 即该关键点
                keypoints[segclass_name].append((label, points[0]))
                continue

            mask = labelme.utils.shape_to_mask(imshape, points, shape_type)
            if group_id is None:
                # 保证在一副图片上的对象都是不同的 group_id
                group_id = uuid.uuid1()

            instance = (label, group_id)

            # if some instance is the same, then their masks should be intersected
            if instance in masks:
                masks[instance] = masks[instance] | mask
            else:
                masks[instance] = mask

            if shape_type == "rectangle":
                (x1, y1), (x2, y2) = points
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                # clock wise
                points = [x1, y1, x2, y1, x2, y2, x1, y2]
            else:
                # 这里直接展平，不考虑分割成几部分的情况
                points = np.asarray(points).flatten().tolist()

            segmentations[instance].append(points)
        return masks, segmentations, keypoints

    def _convert_kp(self, cls_name, keypoints, imshape=None):
        kplist = []
        kpnum = 0
        i = 0
        keypoint_in_category = self._kps_from_categories(cls_name)
        boundary = [10000, 100000, 0, 0] # Top Left  Bottom Right
        if cls_name in keypoints:
            for kp in keypoints[cls_name]:
                # kp is the 2-element-tuple list
                name = kp[0]
                if name not in keypoint_in_category:
                    raise ValueError("KeyPoint and class not match")
                assert i == keypoint_in_category.index(name)
                i += 1
                point = kp[1]
                x = point[0]
                y = point[1]
                kplist.append(x) # x
                kplist.append(y) # y
                kplist.append(2)
                kpnum += 1

                if x < boundary[1]: boundary[1] = x
                if x > boundary[3]: boundary[3] = x
                if y < boundary[0]: boundary[0] = y
                if y > boundary[2]: boundary[2] = y
        if imshape is not None:
            boundary[0] -= 50; boundary[1] -= 50
            boundary[2] += 50; boundary[3] += 50
            if boundary[0] < 0: boundary[0] = 0
            if boundary[1] < 0: boundary[1] = 0
            if boundary[2] > imshape[0]: boundary[2] = imshape[0]
            if boundary[3] > imshape[1]: boundary[3] = imshape[1]
        return kplist, kpnum, boundary
           
    def _getAnno(self, label_file, img, image_id):
        """
        Extract all annotations from single labeled json file.

        Arguments:
            label_file: label_file object
            img: img_arr
            image_id (int): 
        """
        # masks is for area
        masks, segmentations, keypoints = self._extractAnno(label_file, img.shape[:2])
        segmentations = dict(segmentations)
        # sort keypoints to get ordered value
        for _, kp in keypoints.items():
            kp.sort(key=lambda x: x[0])

        if self.debug:
            print("Mask: ", len(masks), masks.keys())
            print("Segm", len(segmentations))
            # for segclass, items in keypoints.items():
            #     print("Keypoints: ", segclass, items)
            self.masks = masks

        annotations = self._data_annotations
        if len(masks) > 0:
            for instance, mask in masks.items():
                cls_name, group_id = instance
                if cls_name not in self.class_name_to_id:
                    continue
                cls_id = self.class_name_to_id[cls_name]

                mask = np.asfortranarray(mask.astype(np.uint8))
                mask = cocomask.encode(mask)
                bbox = cocomask.toBbox(mask).flatten().tolist()
                # it calculates mask area, not box area that torch needs
                area = float(cocomask.area(mask)) 
                # following is the area that torch needs
                # area = float(bbox[2] * bbox[3])
                # bbox = [bbox[0], bbox[1], bbox[0], bbox[1]] # format for torch
                kplist, kpnum, _ = self._convert_kp(cls_name, keypoints)
                anno = dict(
                    id=len(annotations),
                    image_id=image_id,
                    category_id=cls_id,
                    segmentation=segmentations[instance],
                    area=area, 
                    bbox=bbox, 
                    iscrowd=0,
                    keypoints = kplist, # [[kp[0], kp[1], 1] for kp in kps ], # format for torch
                    num_keypoints = kpnum,
                )
                annotations.append(anno)
        else:
            # 这种情况对应只有关键点，没有 mask 的情况
            assert len(keypoints) == 1, "Unable to extract annotation from this file"
            # print("No mask found\n\n")
            # if cls_name not in keypoints:
                # print("Error in class name and keypoint list")
                
            cls_name = list(keypoints.keys())[0] # 找到 keypoint 对应的类名，这里默认只有一个类
            cls_id = self.class_name_to_id[cls_name]
   
            kplist = []
            kpnum = 0
            # print(kps, "========")
            kplist, kpnum, boundary = self._convert_kp(cls_name=cls_name, keypoints=keypoints, imshape=img.shape)
            bbox = [boundary[1], boundary[0], (boundary[3] - boundary[1]), (boundary[2] - boundary[0])]
            area = (boundary[2] - boundary[0]) * (boundary[3] - boundary[1])
            segmentation = [ 
                boundary[1], boundary[0], 
                boundary[1], boundary[2], 
                boundary[3], boundary[2], 
                boundary[3], boundary[0], 
            ]
            anno = dict(
                id=len(annotations),
                image_id=image_id,
                category_id=cls_id,
                segmentation=[segmentation],
                area=area, 
                bbox=bbox, 
                iscrowd=0,
                keypoints = kplist, # [[kp[0], kp[1], 1] for kp in kps ], # format for torch
                num_keypoints = kpnum,
            )
            annotations.append(anno)
        if self.debug:
            print(annotations)

    def generateCocoJson(self, label_files):
        """
        生成 COCO 格式的 JSON 文件

        Args
            label_files: iterateble filenames
        """
        
        out_ann_file = osp.join(self.output_dir, "annotations.json")
        for image_id, filename in tqdm(enumerate(label_files)):
            try:
                label_file = labelme.LabelFile(filename=filename)
            except:
                print("Error generating dataset from:", filename)
                continue
            # 
            base = osp.splitext(osp.basename(filename))[0]
            out_img_file = osp.join(self.output_dir, "JPEGImages", base + ".jpg")

            img = labelme.utils.img_data_to_arr(label_file.imageData)
            Image.fromarray(img).convert("RGB").save(out_img_file)
            ## 填充 images
            self._data_images.append(
                dict(
                    license=0,
                    url=None,
                    file_name=osp.relpath(out_img_file, osp.dirname(out_ann_file)),
                    height=img.shape[0],
                    width=img.shape[1],
                    date_captured=None,
                    id=image_id,
                )
            )

            self._getAnno(label_file, img, image_id)

            if self.debug:
                break


    def output(self, out_ann_file = None, dtype="instances"):
        if out_ann_file is None:
            out_ann_file = "annotations.json"
        out_ann_file = osp.join(self.output_dir, out_ann_file)
        with open(out_ann_file, "w") as f:
            data = dict(
                type=dtype,
                annotations=self._data_annotations,
                categories=self._data_categories,
                images=self._data_images,
                info=self._data_info,
                licenses=self._data_licenses
            )
            json.dump(data, f, indent=True)
