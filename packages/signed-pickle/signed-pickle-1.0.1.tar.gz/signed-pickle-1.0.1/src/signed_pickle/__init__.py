# -*- coding: utf-8 -*-
# coding=utf-8
# signs pickled data to help ensure data integrity and security
# Based on https://pycharm-security.readthedocs.io/en/latest/checks/PIC100.html


from importlib.resources import Package, Resource
from importlib.resources import path as res_path

from .dumper_signer import DumperSigner
from .pickle_signer import PickleSigner  # nosec


def dump(obj, file=None):
    return PickleSigner(use_header=False).dump(obj, file)


def load(file):
    return PickleSigner().load(file)


def load_resource(package: Package, resource: Resource):
    with res_path(package, resource) as file:
        return load(file)


def save_resource(obj, package: Package, resource: Resource):
    with res_path(package, resource) as file:
        return dump(obj, file)


__version__: str = "1.0.1"

__all__ = [
    "dump",
    "load",
    "load_resource",
    "save_resource",
    "PickleSigner",
    "DumperSigner",
]
