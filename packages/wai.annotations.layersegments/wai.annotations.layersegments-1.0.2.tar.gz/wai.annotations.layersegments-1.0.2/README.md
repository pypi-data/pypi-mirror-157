# wai-annotations-layersegments
wai.annotations module that manages image segmentation annotations where layers are stored in separate mask files.

The manual is available here:

https://ufdl.cms.waikato.ac.nz/wai-annotations-manual/

## Plugins
### FROM-LAYER-SEGMENTS-IS
Reads in the layer-segments image-segmentation format from disk, where each label has a binary PNG storing the mask for that label

#### Domain(s):
- **Image Segmentation Domain**

#### Options:
```
usage: from-layer-segments-is [-I FILENAME] [-i FILENAME] [-N FILENAME] [-n FILENAME] [-o FILENAME] [--seed SEED] [--invert] [--label-separator SEPARATOR] --labels LABEL [LABEL ...] [--lenient] [--image-path-rel PATH]

optional arguments:
  -I FILENAME, --inputs-file FILENAME
                        Files containing lists of input files (can use glob syntax)
  -i FILENAME, --input FILENAME
                        Input files (can use glob syntax)
  -N FILENAME, --negatives-file FILENAME
                        Files containing lists of negative files (can use glob syntax)
  -n FILENAME, --negative FILENAME
                        Files that have no annotations (can use glob syntax)
  -o FILENAME, --output-file FILENAME
                        optional file to write read filenames into
  --seed SEED           the seed to use for randomisation
  --invert              inverts the colors in the annotations (b/w <-> w/b)
  --label-separator SEPARATOR
                        the separator between the base filename and the label
  --labels LABEL [LABEL ...]
                        specifies the labels for each index
  --lenient             converts non-binary images with only two unique colors into binary ones rather than throwing an exception
  --image-path-rel PATH
                        Relative path to image files from annotations
```

### TO-LAYER-SEGMENTS-IS
Writes the layer-segments image-segmentation format to disk

#### Domain(s):
- **Image Segmentation Domain**

#### Options:
```
usage: to-layer-segments-is [--annotations-only] [--label-separator SEPARATOR] -o PATH [--split-names SPLIT NAME [SPLIT NAME ...]] [--split-ratios RATIO [RATIO ...]]

optional arguments:
  --annotations-only    skip the writing of data files, outputting only the annotation files
  --label-separator SEPARATOR
                        the separator between the base filename and the label
  -o PATH, --output PATH
                        the directory to write the annotation images to
  --split-names SPLIT NAME [SPLIT NAME ...]
                        the names to use for the splits
  --split-ratios RATIO [RATIO ...]
                        the ratios to use for the splits
```
