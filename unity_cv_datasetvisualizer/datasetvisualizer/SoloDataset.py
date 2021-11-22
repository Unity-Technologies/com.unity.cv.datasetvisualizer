import os
from typing import Dict, Optional

from PIL import Image
from datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights.datasets.unity_perception.captures import Captures

import visualization.visualizers as v
import json
from os import listdir
from os.path import isfile, join

from google.protobuf.json_format import MessageToDict, Parse, ParseError
from UnityVisionHub.tools.consumers.solo.parser import Solo
from UnityVisionHub.tools.consumers.protos.solo_pb2 import (
    BoundingBox2DAnnotation,
    BoundingBox3DAnnotation,
    Frame,
    InstanceSegmentationAnnotation,
    SemanticSegmentationAnnotation,
    RGBCamera,
    KeypointAnnotation
)


class Dataset:
    @staticmethod
    def check_folder_valid(base_dataset_dir: str):
        found_solo_meta = False
        found_solo_annot = False
        found_solo_metric = False
        found_solo_sensor = False
        try:
            meta_file = "metadata.json"
            annot_file = "annotation_definitions.json"
            metric_file = "metric_definitions.json"
            sensor_file = "sensor_definitions.json"
            files = [f for f in listdir(base_dataset_dir) if isfile(join(base_dataset_dir, f))]
            if meta_file in files:
                found_solo_meta = True
            if annot_file in files:
                found_solo_annot = True
            if metric_file in files:
                found_solo_metric = True
            if sensor_file in files:
                found_solo_sensor = True
            return found_solo_meta and found_solo_annot and found_solo_metric and found_solo_sensor
        except PermissionError:
            return False

    def __init__(self, data_root: str):
        if Dataset.check_folder_valid(data_root):
            try:
                self.data_root = data_root
                self.get_annotation_definitions()
                self.solo = Solo(data_root, start=0)
                self.dataset_valid = True
            except Exception as e:
                print(e)
                self.data_root = None
                self.solo = None
                self.dataset_valid = False
        else:
            self.data_root = None
            self.solo = None

            self.dataset_valid = False

    def get_annotation_definitions(self):
        f = open(os.path.join(self.data_root, "metadata" + "." + "json"), "r")
        self.metadata = json.load(f)

        f = open(os.path.join(self.data_root, "annotation_definitions.json"), "r")
        self.annotaion_definitions = json.load(f)
        return self.metadata

    def get_available_labelers(self):
        return self.metadata["annotators"]

    def length(self):
        return self.metadata["totalFrames"]

    def get_keypoint_template(self, templateId: str):
        for i in self.annotaion_definitions['annotationDefinitions']:
            if i['@type'] == 'type.unity.com/unity.solo.KeypointAnnotationDefinition':
                template = i['template']
                if template['templateId'] == templateId:
                    return template;

        return None

    def _to_annotation(self, annotation):
        if annotation == 'type.unity.com/unity.solo.SemanticSegmentationAnnotationDefinition':
            return SemanticSegmentationAnnotation()
        if annotation == 'type.unity.com/unity.solo.InstanceSegmentationAnnotationDefinition':
            return InstanceSegmentationAnnotation()
        if annotation == 'type.unity.com/unity.solo.BoundingBoxAnnotationDefinition':
            return BoundingBox2DAnnotation()
        if annotation == 'type.unity.com/unity.solo.BoundingBox3DAnnotationDefinition':
            return BoundingBox3DAnnotation()
        if annotation == 'type.unity.com/unity.solo.KeypointAnnotationDefinition':
            return KeypointAnnotation()
        return None

    def get_annotator_dictionary(self):
        available_labelers = self.get_available_labelers()
        annotator_dic = {}
        for labeler in available_labelers:
            annotator_name_state = self.AnnotatorNameState(labeler['name'], False)
            if labeler['type'] not in annotator_dic:
                annotator_dic[labeler['type']] = [annotator_name_state]
            else:
                annotator_dic[labeler['type']].append(annotator_name_state)
        return annotator_dic

    def _get_annotation_from_sensor(self, sensor, annotator, annotation):
        annotations = sensor.annotations
        ann_type = self._to_annotation(annotation)

        for a in annotations:
            if a.Is(ann_type.DESCRIPTOR):
                a.Unpack(ann_type)
                messageToDict = MessageToDict(a)
                if 'id' in messageToDict and messageToDict['id'] == annotator.name and annotator.state:
                    return messageToDict
                elif 'id' not in messageToDict and annotator.state:
                    return messageToDict

        return None

    # create AnnotatorNameState class
    class AnnotatorNameState:
        def __init__(self, name: str, state: bool):
            self.name = name
            self.state = state

    def get_solo_image_with_labelers(
            self,
            index: int,
            labelers_to_use: Dict[str, bool],
            annotator_dic: Dict[str, AnnotatorNameState],
            max_size: int = 500) -> Image:

        self.solo.jump_to(index)

        sensor = self.solo.sensors()[0]['message']
        part_a = self.solo.sequence_path
        part_b = sensor.filename
        filename = os.path.join(self.solo.sequence_path, sensor.filename)
        image = Image.open(filename)

        if labelers_to_use == None:
            labelers_to_use = []

        if 'type.unity.com/unity.solo.BoundingBoxAnnotationDefinition' in labelers_to_use and labelers_to_use[
            'type.unity.com/unity.solo.BoundingBoxAnnotationDefinition']:
            for annotator in annotator_dic['type.unity.com/unity.solo.BoundingBoxAnnotationDefinition']:
                if annotator.state:
                    bbox_data = self._get_annotation_from_sensor(sensor, annotator,
                                                                 'type.unity.com/unity.solo.BoundingBoxAnnotationDefinition')
                    image = v.draw_image_with_boxes(image, bbox_data)

        if 'type.unity.com/unity.solo.KeypointAnnotationDefinition' in labelers_to_use and labelers_to_use[
            'type.unity.com/unity.solo.KeypointAnnotationDefinition']:
            for annotator in annotator_dic['type.unity.com/unity.solo.KeypointAnnotationDefinition']:
                if annotator.state:
                    keypoint_data = self._get_annotation_from_sensor(sensor, annotator,
                                                                     'type.unity.com/unity.solo.KeypointAnnotationDefinition')
                    b = keypoint_data['templateId']
                    template = self.get_keypoint_template(b)
                    image = v.draw_image_with_keypoints(image, keypoint_data, template)

        if 'type.unity.com/unity.solo.BoundingBox3DAnnotationDefinition' in labelers_to_use and labelers_to_use[
            'type.unity.com/unity.solo.BoundingBox3DAnnotationDefinition']:
            for annotator in annotator_dic['type.unity.com/unity.solo.BoundingBox3DAnnotationDefinition']:
                if annotator.state:
                    bbox_3d_data = self._get_annotation_from_sensor(sensor, annotator,
                                                                    'type.unity.com/unity.solo.BoundingBox3DAnnotationDefinition')
                    image = v.draw_image_with_box_3d(image, sensor, bbox_3d_data, None)

                    image.thumbnail((max_size, max_size))

        if 'type.unity.com/unity.solo.SemanticSegmentationAnnotationDefinition' in labelers_to_use and labelers_to_use[
            'type.unity.com/unity.solo.SemanticSegmentationAnnotationDefinition']:
            for annotator in annotator_dic['type.unity.com/unity.solo.SemanticSegmentationAnnotationDefinition']:
                if annotator.state:
                    seg_data = self._get_annotation_from_sensor(sensor, annotator,
                                                                'type.unity.com/unity.solo.SemanticSegmentationAnnotationDefinition')
                    seg_filename = os.path.join(self.solo.sequence_path, seg_data['filename'])
                    seg = Image.open(seg_filename)
                    image = v.draw_image_with_segmentation(
                        image, seg
                    )

        if 'type.unity.com/unity.solo.InstanceSegmentationAnnotationDefinition' in labelers_to_use and labelers_to_use[
            'type.unity.com/unity.solo.InstanceSegmentationAnnotationDefinition']:
            for annotator in annotator_dic['type.unity.com/unity.solo.InstanceSegmentationAnnotationDefinition']:
                if annotator.state:
                    seg_data = self._get_annotation_from_sensor(sensor, annotator,
                                                                'type.unity.com/unity.solo.InstanceSegmentationAnnotationDefinition')
                    seg_filename = os.path.join(self.solo.sequence_path, seg_data['filename'])
                    seg = Image.open(seg_filename)
                    image = v.draw_image_with_segmentation(
                        image, seg
                    )

        return image
