import os
from typing import Dict, Optional

from PIL import Image
from datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights.datasets.unity_perception.captures import Captures

import visualization.visualizers as v


class Dataset:
    @staticmethod
    def check_folder_valid(base_dataset_dir: str):
        found_dataset = False
        found_rgb = False
        try:
            children_dirs = [os.path.basename(f.path.replace("\\", "/")) for f in os.scandir(base_dataset_dir) if
                             f.is_dir()]
            for children_dir in children_dirs:
                if children_dir.startswith("Dataset"):
                    found_dataset = True
                elif children_dir.startswith("RGB"):
                    found_rgb = True
            return found_dataset and found_rgb
        except PermissionError:
            return False

    def __init__(self, data_root: str):        
        if Dataset.check_folder_valid(data_root):
            try:                
                self.ann_def = AnnotationDefinitions(data_root)                                
                self.metric_def = MetricDefinitions(data_root)
                self.cap = Captures(data_root)
                self.data_root = data_root
                self.dataset_valid = True
            except Exception as e:
                print(e)
                self.ann_def = None
                self.metric_def = None
                self.cap = None
                self.data_root = None
                self.dataset_valid = False
        else:            
            self.ann_def = None
            self.metric_def = None
            self.cap = None
            self.data_root = None
            self.dataset_valid = False

    def get_metrics_records(self):
        return self.metric_def.table.to_dict('records')

    def get_available_labelers(self):
        return [a["name"] for a in self.ann_def.table.to_dict('records')]

    def length(self):
        return len(self.cap.captures.to_dict('records'))

    def get_annotation_id(self, name: str) -> Optional[str]:
        """ gets annotation definition id of the specified annotation

        :param name: Name of the annotation we want the id of
        :type name: str
        :return: annotation definition id
        :rtype: str
        """

        for idx, a in enumerate(self.ann_def.table.to_dict('records')):
            if a["name"] == name:
                return a["id"]
        return None

    def get_annotation_index(self, name: str) -> int:
        """ gets annotation definition index of the specified annotation

        :param name: Name of the annotation we want the id of
        :type name: str
        :return: index
        :rtype: int
        """
        for idx, a in enumerate(self.ann_def.table.to_dict('records')):
            if a["name"] == name:
                return idx
        return -1

    @staticmethod
    def custom_compare_filenames(filenames):
        for i in range(len(filenames)):
            filenames[i] = int(os.path.basename(filenames[i])[4:-4])
        return filenames

    def get_image_with_labelers(
            self,
            index: int,
            labelers_to_use: Dict[str, bool],
            max_size: int = 500) -> Image:
        """ Creates a PIL image of the capture at index that has all the labelers_to_use visualized
    
        :param index: The index of the frame we want
        :type index: int
        :param labelers_to_use: Dictionary containing keys for the name of every labeler available in the given dataset
                                and the corresponding value is a boolean representing whether or not to display it
        :type labelers_to_use: Dict[str, bool]
        :param max_size: Optional (Default: 500), determines the maximum size of width and height of the created image
                         Useful for optimizing. In the visualizer, if the images were full sized: the browser would take too
                         much time to display them
        :type max_size: int
        :return: The image with the labelers
        :rtype: PIL.Image
        """
        captures = self.cap.filter(def_id=self.ann_def.table.to_dict('records')[0]["id"])
        captures = captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(drop=True)
        capture = captures.loc[index, "filename"]
        filename = os.path.join(self.data_root, capture)
        image = Image.open(filename)

        if 'bounding box' in labelers_to_use and labelers_to_use['bounding box']:
            bounding_box_definition_id = self.get_annotation_id('bounding box')
            bb_captures = self.cap.filter(def_id=bounding_box_definition_id)
            bb_captures = bb_captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(
                drop=True)
            init_definition = self.ann_def.get_definition(bounding_box_definition_id)
            label_mappings = {
                m["label_id"]: m["label_name"] for m in init_definition["spec"]
            }
            image = v.draw_image_with_boxes(
                image,
                index,
                bb_captures,
                label_mappings,
            )

        if 'keypoints' in labelers_to_use and labelers_to_use['keypoints']:
            keypoints_definition_id = self.get_annotation_id('keypoints')
            kp_captures = self.cap.filter(def_id=keypoints_definition_id)
            kp_captures = kp_captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(drop=True)
            annotations = kp_captures.loc[index, "annotation.values"]
            templates = self.ann_def.table.to_dict('records')[self.get_annotation_index('keypoints')]['spec']
            v.draw_image_with_keypoints(image, annotations, templates)

        if 'bounding box 3D' in labelers_to_use and labelers_to_use['bounding box 3D']:
            bounding_box_3d_definition_id = self.get_annotation_id('bounding box 3D')
            box_captures = self.cap.filter(def_id=bounding_box_3d_definition_id)
            box_captures = box_captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(drop=True)
            annotations = box_captures.loc[index, "annotation.values"]
            sensor = box_captures.loc[index, "sensor"]
            image = v.draw_image_with_box_3d(image, sensor, annotations, None)

        # bounding boxes and keypoints are depend on pixel coordinates so for now the thumbnail optimization applies only to
        # segmentation
        # TODO Make it so that bounding boxes and keypoints can be visualized at a lower resolution

        image.thumbnail((max_size, max_size))
        if 'semantic segmentation' in labelers_to_use and labelers_to_use['semantic segmentation']:
            semantic_segmentation_definition_id = self.get_annotation_id('semantic segmentation')

            seg_captures = self.cap.filter(def_id=semantic_segmentation_definition_id)
            seg_captures = seg_captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(drop=True)
            seg_filename = os.path.join(self.data_root, seg_captures.loc[index, "annotation.filename"])
            seg = Image.open(seg_filename)
            seg.thumbnail((max_size, max_size))

            image = v.draw_image_with_segmentation(
                image, seg
            )

        if 'instance segmentation' in labelers_to_use and labelers_to_use['instance segmentation']:
            instance_segmentation_definition_id = self.get_annotation_id('instance segmentation')

            inst_captures = self.cap.filter(def_id=instance_segmentation_definition_id)
            inst_captures = inst_captures.sort_values(by='filename', key=Dataset.custom_compare_filenames).reset_index(
                drop=True)
            inst_filename = os.path.join(self.data_root, inst_captures.loc[index, "annotation.filename"])
            inst = Image.open(inst_filename)
            inst.thumbnail((max_size, max_size))

            image = v.draw_image_with_segmentation(
                image, inst
            )

        return image
