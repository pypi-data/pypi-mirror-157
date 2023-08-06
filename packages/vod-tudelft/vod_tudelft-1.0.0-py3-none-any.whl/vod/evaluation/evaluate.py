import argparse
import os
import evaluation_common as kitti
from kitti_official_evaluate import get_official_eval_result
from vod import get_frame_list_from_folder


class Evaluation:
    def __init__(self, test_annotation_file):
        self.test_annotation_file = test_annotation_file

    def evaluate(self,
                 result_path,
                 current_class=None,
                 score_thresh=-1,
                 ):

        if current_class is None:
            current_class = [0]

        val_image_ids = get_frame_list_from_folder(result_path)

        dt_annotations = kitti.get_label_annotations(result_path, val_image_ids)

        if score_thresh > 0:
            dt_annotations = kitti.filter_annotations_low_score(dt_annotations, score_thresh)

        gt_annotations = kitti.get_label_annotations(self.test_annotation_file, val_image_ids)

        results = [get_official_eval_result(gt_annotations, dt_annotations, current_class),
                   get_official_eval_result(gt_annotations, dt_annotations, current_class, custom_method=3)]

        return results

# The following code can be used to evaluate the results of the VOD model, when the package is imported.
# def parse_args():
#     parser = argparse.ArgumentParser(description='Evaluate the detections for the VOD dataset.')
#     parser.add_argument('annotation_location', help='Path to the annotation files.')
#     parser.add_argument('detection_location', help='Path to the detection files.')
#     arguments = parser.parse_args()
#     return arguments
#
#
# if __name__ == '__main__':
#     args = parse_args()
#
#     evaluation = Evaluation(test_annotation_file=args.annotation_location)
#
#     print(evaluation.evaluate(
#         result_path=os.path.join(args.detection_location),
#         current_class=[0, 1, 2]))
