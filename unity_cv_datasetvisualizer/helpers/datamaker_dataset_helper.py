from typing import Dict

from SoloDataset import Dataset

def get_instance_by_capture_idx(
        instances: Dict[int, Dataset], index: int) \
        -> int:
    """ Gets the instance in instances that contains the given capture index

    :param instances: Dictionary of instances
    :type instances: Dict[int, Tuple[AnnotationDefinitions, MetricDefinitions, Captures, int, str]]
    :param index: Capture index that we want
    :type index: int

    :return: key in dictionary
    :rtype: int
    """
    total = 0
    keys = list(instances.keys())
    keys.sort()
    for key in keys:
        total = total + instances[key].length()
        if int(index) <= total - 1:
            return key


def get_dataset_length_with_instances(
        instances: Dict[int, Dataset],
        until_instance: int = -1) -> \
        int:
    """ Gets the total length of a dataset that goes over multiple instances (aka. Datamaker dataset)
    optionally you can specify until which instance you want to count 
    (the order is based by the natural ordering of keys)

    :param instances: Dictionary of instances
    :type instances: Dict[int, Tuple[AnnotationDefinitions, MetricDefinitions, Captures, int, str]]
    :param until_instance: optional, will stop counting when it reaches the specified instance (non-inclusive)
    :type until_instance: int
    :return: length
    :rtype: int
    """
    total = 0
    keys = list(instances.keys())
    keys.sort()
    for key in keys:
        if 0 <= until_instance <= key:
            break
        total = total + instances[key].length()
    return total
