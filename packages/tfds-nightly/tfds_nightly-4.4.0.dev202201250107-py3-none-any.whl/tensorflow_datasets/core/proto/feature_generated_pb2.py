# coding=utf-8
# Copyright 2022 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: skip-file

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: feature.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
    name='feature.proto',
    package='tensorflow_datasets',
    syntax='proto3',
    serialized_options=b'\370\001\001',
    serialized_pb=b'\n\rfeature.proto\x12\x13tensorflow_datasets\"\xa0\x01\n\x0c\x46\x65\x61turesDict\x12\x41\n\x08\x66\x65\x61tures\x18\x01 \x03(\x0b\x32/.tensorflow_datasets.FeaturesDict.FeaturesEntry\x1aM\n\rFeaturesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.tensorflow_datasets.Feature:\x02\x38\x01\"\xe2\x04\n\x07\x46\x65\x61ture\x12\x19\n\x11python_class_name\x18\x01 \x01(\t\x12\x38\n\x0cjson_feature\x18\x02 \x01(\x0b\x32 .tensorflow_datasets.JsonFeatureH\x00\x12:\n\rfeatures_dict\x18\x03 \x01(\x0b\x32!.tensorflow_datasets.FeaturesDictH\x00\x12\x34\n\x06tensor\x18\x04 \x01(\x0b\x32\".tensorflow_datasets.TensorFeatureH\x00\x12\x36\n\x0b\x63lass_label\x18\x05 \x01(\x0b\x32\x1f.tensorflow_datasets.ClassLabelH\x00\x12\x32\n\x05image\x18\x06 \x01(\x0b\x32!.tensorflow_datasets.ImageFeatureH\x00\x12\x32\n\x05video\x18\x07 \x01(\x0b\x32!.tensorflow_datasets.VideoFeatureH\x00\x12\x32\n\x05\x61udio\x18\x08 \x01(\x0b\x32!.tensorflow_datasets.AudioFeatureH\x00\x12?\n\x0c\x62ounding_box\x18\t \x01(\x0b\x32\'.tensorflow_datasets.BoundingBoxFeatureH\x00\x12\x30\n\x04text\x18\n \x01(\x0b\x32 .tensorflow_datasets.TextFeatureH\x00\x12>\n\x0btranslation\x18\x0b \x01(\x0b\x32\'.tensorflow_datasets.TranslationFeatureH\x00\x42\t\n\x07\x63ontent\"\x1b\n\x0bJsonFeature\x12\x0c\n\x04json\x18\x01 \x01(\t\"\x1b\n\x05Shape\x12\x12\n\ndimensions\x18\x01 \x03(\x03\"[\n\rTensorFeature\x12)\n\x05shape\x18\x01 \x01(\x0b\x32\x1a.tensorflow_datasets.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x10\n\x08\x65ncoding\x18\x03 \x01(\t\"!\n\nClassLabel\x12\x13\n\x0bnum_classes\x18\x01 \x01(\x03\"\xa7\x01\n\x0cImageFeature\x12)\n\x05shape\x18\x01 \x01(\x0b\x32\x1a.tensorflow_datasets.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x17\n\x0f\x65ncoding_format\x18\x03 \x01(\t\x12\x14\n\x0cuse_colormap\x18\x04 \x01(\x08\x12.\n\x05label\x18\x05 \x01(\x0b\x32\x1f.tensorflow_datasets.ClassLabel\"\x92\x01\n\x0cVideoFeature\x12)\n\x05shape\x18\x01 \x01(\x0b\x32\x1a.tensorflow_datasets.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x17\n\x0f\x65ncoding_format\x18\x03 \x01(\t\x12\x14\n\x0cuse_colormap\x18\x04 \x01(\x08\x12\x19\n\x11\x66\x66mpeg_extra_args\x18\x05 \x03(\t\"\x84\x01\n\x0c\x41udioFeature\x12)\n\x05shape\x18\x01 \x01(\x0b\x32\x1a.tensorflow_datasets.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x13\n\x0b\x66ile_format\x18\x03 \x01(\t\x12\x13\n\x0bsample_rate\x18\x04 \x01(\x03\x12\x10\n\x08\x65ncoding\x18\x05 \x01(\t\"N\n\x12\x42oundingBoxFeature\x12)\n\x05shape\x18\x01 \x01(\x0b\x32\x1a.tensorflow_datasets.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\"\r\n\x0bTextFeature\"O\n\x12TranslationFeature\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12&\n\x1evariable_languages_per_example\x18\x02 \x01(\x08\x42\x03\xf8\x01\x01\x62\x06proto3'
)

_FEATURESDICT_FEATURESENTRY = _descriptor.Descriptor(
    name='FeaturesEntry',
    full_name='tensorflow_datasets.FeaturesDict.FeaturesEntry',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='key',
            full_name='tensorflow_datasets.FeaturesDict.FeaturesEntry.key',
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='value',
            full_name='tensorflow_datasets.FeaturesDict.FeaturesEntry.value',
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b'8\001',
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=122,
    serialized_end=199,
)

_FEATURESDICT = _descriptor.Descriptor(
    name='FeaturesDict',
    full_name='tensorflow_datasets.FeaturesDict',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='features',
            full_name='tensorflow_datasets.FeaturesDict.features',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[
        _FEATURESDICT_FEATURESENTRY,
    ],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=39,
    serialized_end=199,
)

_FEATURE = _descriptor.Descriptor(
    name='Feature',
    full_name='tensorflow_datasets.Feature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='python_class_name',
            full_name='tensorflow_datasets.Feature.python_class_name',
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='json_feature',
            full_name='tensorflow_datasets.Feature.json_feature',
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='features_dict',
            full_name='tensorflow_datasets.Feature.features_dict',
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='tensor',
            full_name='tensorflow_datasets.Feature.tensor',
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='class_label',
            full_name='tensorflow_datasets.Feature.class_label',
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='image',
            full_name='tensorflow_datasets.Feature.image',
            index=5,
            number=6,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='video',
            full_name='tensorflow_datasets.Feature.video',
            index=6,
            number=7,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='audio',
            full_name='tensorflow_datasets.Feature.audio',
            index=7,
            number=8,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='bounding_box',
            full_name='tensorflow_datasets.Feature.bounding_box',
            index=8,
            number=9,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='text',
            full_name='tensorflow_datasets.Feature.text',
            index=9,
            number=10,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='translation',
            full_name='tensorflow_datasets.Feature.translation',
            index=10,
            number=11,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
        _descriptor.OneofDescriptor(
            name='content',
            full_name='tensorflow_datasets.Feature.content',
            index=0,
            containing_type=None,
            fields=[]),
    ],
    serialized_start=202,
    serialized_end=812,
)

_JSONFEATURE = _descriptor.Descriptor(
    name='JsonFeature',
    full_name='tensorflow_datasets.JsonFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='json',
            full_name='tensorflow_datasets.JsonFeature.json',
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=814,
    serialized_end=841,
)

_SHAPE = _descriptor.Descriptor(
    name='Shape',
    full_name='tensorflow_datasets.Shape',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='dimensions',
            full_name='tensorflow_datasets.Shape.dimensions',
            index=0,
            number=1,
            type=3,
            cpp_type=2,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=843,
    serialized_end=870,
)

_TENSORFEATURE = _descriptor.Descriptor(
    name='TensorFeature',
    full_name='tensorflow_datasets.TensorFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='shape',
            full_name='tensorflow_datasets.TensorFeature.shape',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='dtype',
            full_name='tensorflow_datasets.TensorFeature.dtype',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='encoding',
            full_name='tensorflow_datasets.TensorFeature.encoding',
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=872,
    serialized_end=963,
)

_CLASSLABEL = _descriptor.Descriptor(
    name='ClassLabel',
    full_name='tensorflow_datasets.ClassLabel',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='num_classes',
            full_name='tensorflow_datasets.ClassLabel.num_classes',
            index=0,
            number=1,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=965,
    serialized_end=998,
)

_IMAGEFEATURE = _descriptor.Descriptor(
    name='ImageFeature',
    full_name='tensorflow_datasets.ImageFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='shape',
            full_name='tensorflow_datasets.ImageFeature.shape',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='dtype',
            full_name='tensorflow_datasets.ImageFeature.dtype',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='encoding_format',
            full_name='tensorflow_datasets.ImageFeature.encoding_format',
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='use_colormap',
            full_name='tensorflow_datasets.ImageFeature.use_colormap',
            index=3,
            number=4,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='label',
            full_name='tensorflow_datasets.ImageFeature.label',
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1001,
    serialized_end=1168,
)

_VIDEOFEATURE = _descriptor.Descriptor(
    name='VideoFeature',
    full_name='tensorflow_datasets.VideoFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='shape',
            full_name='tensorflow_datasets.VideoFeature.shape',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='dtype',
            full_name='tensorflow_datasets.VideoFeature.dtype',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='encoding_format',
            full_name='tensorflow_datasets.VideoFeature.encoding_format',
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='use_colormap',
            full_name='tensorflow_datasets.VideoFeature.use_colormap',
            index=3,
            number=4,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='ffmpeg_extra_args',
            full_name='tensorflow_datasets.VideoFeature.ffmpeg_extra_args',
            index=4,
            number=5,
            type=9,
            cpp_type=9,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1171,
    serialized_end=1317,
)

_AUDIOFEATURE = _descriptor.Descriptor(
    name='AudioFeature',
    full_name='tensorflow_datasets.AudioFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='shape',
            full_name='tensorflow_datasets.AudioFeature.shape',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='dtype',
            full_name='tensorflow_datasets.AudioFeature.dtype',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='file_format',
            full_name='tensorflow_datasets.AudioFeature.file_format',
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='sample_rate',
            full_name='tensorflow_datasets.AudioFeature.sample_rate',
            index=3,
            number=4,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='encoding',
            full_name='tensorflow_datasets.AudioFeature.encoding',
            index=4,
            number=5,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1320,
    serialized_end=1452,
)

_BOUNDINGBOXFEATURE = _descriptor.Descriptor(
    name='BoundingBoxFeature',
    full_name='tensorflow_datasets.BoundingBoxFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='shape',
            full_name='tensorflow_datasets.BoundingBoxFeature.shape',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='dtype',
            full_name='tensorflow_datasets.BoundingBoxFeature.dtype',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b''.decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1454,
    serialized_end=1532,
)

_TEXTFEATURE = _descriptor.Descriptor(
    name='TextFeature',
    full_name='tensorflow_datasets.TextFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1534,
    serialized_end=1547,
)

_TRANSLATIONFEATURE = _descriptor.Descriptor(
    name='TranslationFeature',
    full_name='tensorflow_datasets.TranslationFeature',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='languages',
            full_name='tensorflow_datasets.TranslationFeature.languages',
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='variable_languages_per_example',
            full_name='tensorflow_datasets.TranslationFeature.variable_languages_per_example',
            index=1,
            number=2,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[],
    serialized_start=1549,
    serialized_end=1628,
)

_FEATURESDICT_FEATURESENTRY.fields_by_name['value'].message_type = _FEATURE
_FEATURESDICT_FEATURESENTRY.containing_type = _FEATURESDICT
_FEATURESDICT.fields_by_name[
    'features'].message_type = _FEATURESDICT_FEATURESENTRY
_FEATURE.fields_by_name['json_feature'].message_type = _JSONFEATURE
_FEATURE.fields_by_name['features_dict'].message_type = _FEATURESDICT
_FEATURE.fields_by_name['tensor'].message_type = _TENSORFEATURE
_FEATURE.fields_by_name['class_label'].message_type = _CLASSLABEL
_FEATURE.fields_by_name['image'].message_type = _IMAGEFEATURE
_FEATURE.fields_by_name['video'].message_type = _VIDEOFEATURE
_FEATURE.fields_by_name['audio'].message_type = _AUDIOFEATURE
_FEATURE.fields_by_name['bounding_box'].message_type = _BOUNDINGBOXFEATURE
_FEATURE.fields_by_name['text'].message_type = _TEXTFEATURE
_FEATURE.fields_by_name['translation'].message_type = _TRANSLATIONFEATURE
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['json_feature'])
_FEATURE.fields_by_name[
    'json_feature'].containing_oneof = _FEATURE.oneofs_by_name['content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['features_dict'])
_FEATURE.fields_by_name[
    'features_dict'].containing_oneof = _FEATURE.oneofs_by_name['content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['tensor'])
_FEATURE.fields_by_name['tensor'].containing_oneof = _FEATURE.oneofs_by_name[
    'content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['class_label'])
_FEATURE.fields_by_name[
    'class_label'].containing_oneof = _FEATURE.oneofs_by_name['content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['image'])
_FEATURE.fields_by_name['image'].containing_oneof = _FEATURE.oneofs_by_name[
    'content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['video'])
_FEATURE.fields_by_name['video'].containing_oneof = _FEATURE.oneofs_by_name[
    'content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['audio'])
_FEATURE.fields_by_name['audio'].containing_oneof = _FEATURE.oneofs_by_name[
    'content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['bounding_box'])
_FEATURE.fields_by_name[
    'bounding_box'].containing_oneof = _FEATURE.oneofs_by_name['content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['text'])
_FEATURE.fields_by_name['text'].containing_oneof = _FEATURE.oneofs_by_name[
    'content']
_FEATURE.oneofs_by_name['content'].fields.append(
    _FEATURE.fields_by_name['translation'])
_FEATURE.fields_by_name[
    'translation'].containing_oneof = _FEATURE.oneofs_by_name['content']
_TENSORFEATURE.fields_by_name['shape'].message_type = _SHAPE
_IMAGEFEATURE.fields_by_name['shape'].message_type = _SHAPE
_IMAGEFEATURE.fields_by_name['label'].message_type = _CLASSLABEL
_VIDEOFEATURE.fields_by_name['shape'].message_type = _SHAPE
_AUDIOFEATURE.fields_by_name['shape'].message_type = _SHAPE
_BOUNDINGBOXFEATURE.fields_by_name['shape'].message_type = _SHAPE
DESCRIPTOR.message_types_by_name['FeaturesDict'] = _FEATURESDICT
DESCRIPTOR.message_types_by_name['Feature'] = _FEATURE
DESCRIPTOR.message_types_by_name['JsonFeature'] = _JSONFEATURE
DESCRIPTOR.message_types_by_name['Shape'] = _SHAPE
DESCRIPTOR.message_types_by_name['TensorFeature'] = _TENSORFEATURE
DESCRIPTOR.message_types_by_name['ClassLabel'] = _CLASSLABEL
DESCRIPTOR.message_types_by_name['ImageFeature'] = _IMAGEFEATURE
DESCRIPTOR.message_types_by_name['VideoFeature'] = _VIDEOFEATURE
DESCRIPTOR.message_types_by_name['AudioFeature'] = _AUDIOFEATURE
DESCRIPTOR.message_types_by_name['BoundingBoxFeature'] = _BOUNDINGBOXFEATURE
DESCRIPTOR.message_types_by_name['TextFeature'] = _TEXTFEATURE
DESCRIPTOR.message_types_by_name['TranslationFeature'] = _TRANSLATIONFEATURE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FeaturesDict = _reflection.GeneratedProtocolMessageType(
    'FeaturesDict',
    (_message.Message,),
    {
        'FeaturesEntry':
            _reflection.GeneratedProtocolMessageType(
                'FeaturesEntry',
                (_message.Message,),
                {
                    'DESCRIPTOR': _FEATURESDICT_FEATURESENTRY,
                    '__module__': 'feature_pb2'
                    # @@protoc_insertion_point(class_scope:tensorflow_datasets.FeaturesDict.FeaturesEntry)
                }),
        'DESCRIPTOR':
            _FEATURESDICT,
        '__module__':
            'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.FeaturesDict)
    })
_sym_db.RegisterMessage(FeaturesDict)
_sym_db.RegisterMessage(FeaturesDict.FeaturesEntry)

Feature = _reflection.GeneratedProtocolMessageType(
    'Feature',
    (_message.Message,),
    {
        'DESCRIPTOR': _FEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.Feature)
    })
_sym_db.RegisterMessage(Feature)

JsonFeature = _reflection.GeneratedProtocolMessageType(
    'JsonFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _JSONFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.JsonFeature)
    })
_sym_db.RegisterMessage(JsonFeature)

Shape = _reflection.GeneratedProtocolMessageType(
    'Shape',
    (_message.Message,),
    {
        'DESCRIPTOR': _SHAPE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.Shape)
    })
_sym_db.RegisterMessage(Shape)

TensorFeature = _reflection.GeneratedProtocolMessageType(
    'TensorFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _TENSORFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.TensorFeature)
    })
_sym_db.RegisterMessage(TensorFeature)

ClassLabel = _reflection.GeneratedProtocolMessageType(
    'ClassLabel',
    (_message.Message,),
    {
        'DESCRIPTOR': _CLASSLABEL,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.ClassLabel)
    })
_sym_db.RegisterMessage(ClassLabel)

ImageFeature = _reflection.GeneratedProtocolMessageType(
    'ImageFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _IMAGEFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.ImageFeature)
    })
_sym_db.RegisterMessage(ImageFeature)

VideoFeature = _reflection.GeneratedProtocolMessageType(
    'VideoFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _VIDEOFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.VideoFeature)
    })
_sym_db.RegisterMessage(VideoFeature)

AudioFeature = _reflection.GeneratedProtocolMessageType(
    'AudioFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _AUDIOFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.AudioFeature)
    })
_sym_db.RegisterMessage(AudioFeature)

BoundingBoxFeature = _reflection.GeneratedProtocolMessageType(
    'BoundingBoxFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _BOUNDINGBOXFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.BoundingBoxFeature)
    })
_sym_db.RegisterMessage(BoundingBoxFeature)

TextFeature = _reflection.GeneratedProtocolMessageType(
    'TextFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _TEXTFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.TextFeature)
    })
_sym_db.RegisterMessage(TextFeature)

TranslationFeature = _reflection.GeneratedProtocolMessageType(
    'TranslationFeature',
    (_message.Message,),
    {
        'DESCRIPTOR': _TRANSLATIONFEATURE,
        '__module__': 'feature_pb2'
        # @@protoc_insertion_point(class_scope:tensorflow_datasets.TranslationFeature)
    })
_sym_db.RegisterMessage(TranslationFeature)

DESCRIPTOR._options = None
_FEATURESDICT_FEATURESENTRY._options = None
# @@protoc_insertion_point(module_scope)
