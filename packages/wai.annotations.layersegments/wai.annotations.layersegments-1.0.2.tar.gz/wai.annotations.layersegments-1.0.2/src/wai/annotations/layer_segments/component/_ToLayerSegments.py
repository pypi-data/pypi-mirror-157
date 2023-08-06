import numpy as np
from PIL import Image

from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import RequiresNoFinalisation
from wai.annotations.domain.image.segmentation import ImageSegmentationInstance
from ..util import LayerSegmentsOutputFormat


class ToLayerSegments(
    RequiresNoFinalisation,
    ProcessorComponent[ImageSegmentationInstance, LayerSegmentsOutputFormat]
):
    """
    Converts the internal image-segmentation format into the one-image-per-label
    annotation format.
    """
    def process_element(
            self,
            element: ImageSegmentationInstance,
            then: ThenFunction[LayerSegmentsOutputFormat],
            done: DoneFunction
    ):
        # Handle negatives
        if element.annotations is None:
            return then(LayerSegmentsOutputFormat(element.data, {}))

        then(
            LayerSegmentsOutputFormat(
                element.data,
                element.annotations.label_images
            )
        )
