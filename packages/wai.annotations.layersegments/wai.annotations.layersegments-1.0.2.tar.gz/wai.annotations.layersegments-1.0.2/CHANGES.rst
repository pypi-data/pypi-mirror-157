Changelog
=========

1.0.2 (2022-06-30)
------------------

- `FromLayerSegments` class now outputs logging message if setting of new annotation indices fails, as error
  occurs before the `wai.annotations - Sourced ...` logging message, making it possible to track the image
  causing the problem.
- Added `--lenient` flag to `FromLayerSegments` class which allows conversion of non-binary images with just
  two unique colors to binary ones instead of throwing an error.
- Added `--invert` flag to `FromLayerSegments` class which allows inverting the colors (b/w <-> w/b) of the
  binary annotation images.


1.0.1 (2022-05-11)
------------------

- Image segmentation annotations received `label_images` property with code from the ToLayerSegments conversion


1.0.0 (2021-05-20)
------------------

- Initial release after separation from wai.annotations main repo.
