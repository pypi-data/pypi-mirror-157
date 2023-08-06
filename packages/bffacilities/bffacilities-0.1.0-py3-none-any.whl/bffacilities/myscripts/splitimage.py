import os
import os.path as osp
from PIL import Image, ImageStat
from tqdm import tqdm
import numpy as np

def split(indir, outdir, size):
    # print(indir, outdir, size)
    for root, dirs, files in os.walk(indir):
        for f in tqdm(files):
            infile = osp.join(root, f)
            outfile = osp.join(outdir, f)
            outname, ext = osp.splitext(outfile)
            # print(outname, ext)
            # break
            image = Image.open(infile)
            # image.load()
            iw, ih = image.size
            sw, sh = 0, 0
            count = 0
            for sw in range(0, iw, size[0]):
                if sw + size[0] > iw:
                    sw = iw - size[0]
                for sh in range(0, ih, size[1]):
                    if sh + size[1] > ih:
                        sh = ih - size[1]
                    # print("Crop ", (sw, sh, size[0], size[1]))
                    cim = image.crop((sw, sh, sw + size[0],  sh + size[1]))
                    out = f"{outname}_{count}__{sw}__{sh}{ext}"
                    cim.save(out)
                    # print("Out ", f"{sh}/{ih}", " w ", f"{sw}/{iw}")
                    count += 1
            # print(w, h)
import shutil as sh
def filterbackground(indir, outdir, valve=3.3):
    count = 0
    for root, dirs, files in os.walk(indir):
        for i, f in tqdm(enumerate(files)):
            infile = osp.join(root, f)
            image = Image.open(infile)
            stat = ImageStat.Stat(image)
            stddev = np.round(stat.stddev, decimals=2)
            c = np.sum(stddev < valve)
            if c > 0:
                outfile = osp.join(outdir, f)
                sh.move(infile, outfile)
                count += 1
            # print(f, stddev, c)
            # if i > 6*2: break
    print(f"Moved: {count}")

def main(args = None):
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="splitimage", description="Split image into dst size.")
    parser.add_argument("-t", "--type", type=str, default="split", help="Action whether to split image or filter empty image")
    parser.add_argument("-i", "--input", type=str, default=".", help="The directory that program will walk through")
    parser.add_argument("-o", "--output", type=str, help="Output Directory")
    parser.add_argument("-s", "--size", type=str, default="192x192", help="Splited size, default is 192x192")

    args = vars(parser.parse_args(args))
    atype = args["type"]
    output = args["output"]
    if atype == "split":
        try:
            size = args["size"].split("x")
            size = list(map(int, size))
        except:
            print(f"Input size: {args['size']} is invalid. Using default size")
            size = (192, 192)
        if output is None:
            output = "split_" + args["input"]
        if not osp.exists(output):
            os.makedirs(output)
        split(args["input"], output, size)
    elif atype == "filter":
        if output is None:
            output = "remove_" + args["input"]
        if not osp.exists(output):
            os.makedirs(output)
        filterbackground(args["input"], output)

