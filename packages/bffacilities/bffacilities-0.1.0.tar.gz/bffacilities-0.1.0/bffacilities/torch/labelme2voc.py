import json
import os
import os.path as osp
from tqdm import tqdm
from PIL import Image
import numpy as np
# from labelme.label_file import LabelFile, PY2, QT4, utils, io
import shutil as sh
import glob
import imgviz
import labelme

__version__ = "0.1.1"


class Labelme2Vocor():

    def __init__(self, input_dir, output_dir, noviz=False, debug=False, **kwargs):
        if osp.exists(output_dir):
            print("****Output directory already exists: ", output_dir, " They may need to ne deleted...")
            # sh.rmtree(output_dir)
            # return
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(osp.join(output_dir, "JPEGImages"), exist_ok=True)
        os.makedirs(osp.join(output_dir, "SegmentationClass"), exist_ok=True)
        os.makedirs(osp.join(output_dir, "SegmentationClassPNG"), exist_ok=True)

        if not noviz:
            os.makedirs(osp.join(output_dir, "SegmentationClassVisualization"), exist_ok=True)
        print("Creating dataset:", output_dir)

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.noviz = noviz
        self.debug = debug

    def setClasses(self, classes):
        """不含 background
        """
        self.class_names = classes
        self.class_name_to_id = {}
        for i, cn in enumerate(classes):
            self.class_name_to_id[cn] = i + 1
        self.class_name_to_id["_background_"] = 0
        self._write_out()

    def getClassesFromFile(self, classfile):
        """
        根据文件获取 class

        ```
        __ignore__
        _background_
        class1
        class2
        ```
        """
        ## get class names
        contents = []
        with open(classfile, "r") as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                contents.append(line)

        class_names = []
        class_name_to_id = {}  # name: 1
        for i, line in enumerate(contents):
            class_id = i - 1  # starts with -1
            class_name = line.strip()
            if len(class_name) == 0:
                continue
            class_name_to_id[class_name] = class_id
            if class_id == -1:
                assert class_name == "__ignore__"
                continue
            elif class_id == 0:
                assert class_name == "_background_"
            class_names.append(class_name)

        class_names = tuple(class_names)

        self.class_names = class_names
        self.class_name_to_id = class_name_to_id
        self._write_out()

    def _write_out(self):
        out_class_names_file = osp.join(self.output_dir, "class_names.txt")

        with open(out_class_names_file, "w") as f:
            f.writelines("\n".join(self.class_names))
        print("Class_names:", self.class_names)
        print("Saved class_names:", out_class_names_file)

    def output(self, ordered_keys=None):
        """
        Arguments:
            ordered_keys(list(str))
        """
        print("Generating dataset from:", self.input_dir, " ====> ", self.output_dir)
        for filename in tqdm(glob.glob(osp.join(self.input_dir, "*.json"))):

            label_file = labelme.LabelFile(filename=filename)
            base = osp.splitext(osp.basename(filename))[0]

            out_img_file = osp.join(self.output_dir, "JPEGImages", base + ".jpg")

            with open(out_img_file, "wb") as f:
                f.write(label_file.imageData)

            if ordered_keys is not None:
                newshapes = []
                for ok in ordered_keys:
                    for shape in label_file.shapes:
                        if shape["label"] == ok:
                            newshapes.append(shape)
                label_file.shapes=newshapes

            img = labelme.utils.img_data_to_arr(label_file.imageData)

            lbl, _ = labelme.utils.shapes_to_label(
                img_shape=img.shape,
                shapes=label_file.shapes,
                label_name_to_value=self.class_name_to_id,
            )

            out_png_file = osp.join(self.output_dir, "SegmentationClassPNG", base + ".png")
            labelme.utils.lblsave(out_png_file, lbl)

            # out_lbl_file = osp.join(self.output_dir, "SegmentationClass", base + ".npy")
            # np.save(out_lbl_file, lbl)
                
            if not self.noviz:
                out_viz_file = osp.join(self.output_dir, "SegmentationClassVisualization", base + ".jpg",)

                if img.shape[0] == 1: # gray img
                    img = imgviz.rgb2gray(img)
                h, w = img.shape[:2]
                
                viz = imgviz.label2rgb(
                    label=lbl,
                    # img=imgviz.rgb2gray(img),
                    img=img,
                    font_size=max(10, w // 10),
                    label_names=self.class_names,
                    loc="rb",
                )
                imgviz.io.imsave(out_viz_file, viz)

            
            if self.debug:
                print(label_file.shapes)
                break

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser("labelme2voc")
    parser.add_argument("--input", type=str, required=True, help="Input Directory contains *.json annotation")
    parser.add_argument("--output", type=str, required=True, help="Output Directory, should be different from input")
    parser.add_argument("--classfile", type=str, default="class_names.txt",  help="Specify file contains class names" )
    parser.add_argument("--orderkeys", type=str, default=None, help="Orderedkyes for classes in label file" )

    args = vars(parser.parse_args(args))
    voc = Labelme2Vocor(args["input"], args["output"])
    voc.getClassesFromFile(args["classfile"])
    voc.output(args["orderkeys"])

if __name__ == "__main__":
    main()
