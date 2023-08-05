# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: response.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eresponse.proto\x1a\x19google/protobuf/any.proto\"$\n\tResponses\x12\x17\n\x07matches\x18\x01 \x03(\x0b\x32\x06.Match\"\xf0\x01\n\x05Match\x12\x13\n\x04span\x18\x01 \x01(\x0b\x32\x05.Span\x12*\n\nattributes\x18\x02 \x03(\x0b\x32\x16.Match.AttributesEntry\x12*\n\nunderscore\x18\x03 \x03(\x0b\x32\x16.Match.UnderscoreEntry\x1a\x31\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1aG\n\x0fUnderscoreEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12#\n\x05value\x18\x02 \x01(\x0b\x32\x14.google.protobuf.Any:\x02\x38\x01\"`\n\x06Labels\x12!\n\x05items\x18\x01 \x03(\x0b\x32\x12.Labels.ItemsEntry\x1a\x33\n\nItemsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x14\n\x05value\x18\x02 \x01(\x0b\x32\x05.Span:\x02\x38\x01\"\"\n\x04Span\x12\r\n\x05start\x18\x01 \x01(\t\x12\x0b\n\x03\x65nd\x18\x02 \x01(\tb\x06proto3')



_RESPONSES = DESCRIPTOR.message_types_by_name['Responses']
_MATCH = DESCRIPTOR.message_types_by_name['Match']
_MATCH_ATTRIBUTESENTRY = _MATCH.nested_types_by_name['AttributesEntry']
_MATCH_UNDERSCOREENTRY = _MATCH.nested_types_by_name['UnderscoreEntry']
_LABELS = DESCRIPTOR.message_types_by_name['Labels']
_LABELS_ITEMSENTRY = _LABELS.nested_types_by_name['ItemsEntry']
_SPAN = DESCRIPTOR.message_types_by_name['Span']
Responses = _reflection.GeneratedProtocolMessageType('Responses', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSES,
  '__module__' : 'response_pb2'
  # @@protoc_insertion_point(class_scope:Responses)
  })
_sym_db.RegisterMessage(Responses)

Match = _reflection.GeneratedProtocolMessageType('Match', (_message.Message,), {

  'AttributesEntry' : _reflection.GeneratedProtocolMessageType('AttributesEntry', (_message.Message,), {
    'DESCRIPTOR' : _MATCH_ATTRIBUTESENTRY,
    '__module__' : 'response_pb2'
    # @@protoc_insertion_point(class_scope:Match.AttributesEntry)
    })
  ,

  'UnderscoreEntry' : _reflection.GeneratedProtocolMessageType('UnderscoreEntry', (_message.Message,), {
    'DESCRIPTOR' : _MATCH_UNDERSCOREENTRY,
    '__module__' : 'response_pb2'
    # @@protoc_insertion_point(class_scope:Match.UnderscoreEntry)
    })
  ,
  'DESCRIPTOR' : _MATCH,
  '__module__' : 'response_pb2'
  # @@protoc_insertion_point(class_scope:Match)
  })
_sym_db.RegisterMessage(Match)
_sym_db.RegisterMessage(Match.AttributesEntry)
_sym_db.RegisterMessage(Match.UnderscoreEntry)

Labels = _reflection.GeneratedProtocolMessageType('Labels', (_message.Message,), {

  'ItemsEntry' : _reflection.GeneratedProtocolMessageType('ItemsEntry', (_message.Message,), {
    'DESCRIPTOR' : _LABELS_ITEMSENTRY,
    '__module__' : 'response_pb2'
    # @@protoc_insertion_point(class_scope:Labels.ItemsEntry)
    })
  ,
  'DESCRIPTOR' : _LABELS,
  '__module__' : 'response_pb2'
  # @@protoc_insertion_point(class_scope:Labels)
  })
_sym_db.RegisterMessage(Labels)
_sym_db.RegisterMessage(Labels.ItemsEntry)

Span = _reflection.GeneratedProtocolMessageType('Span', (_message.Message,), {
  'DESCRIPTOR' : _SPAN,
  '__module__' : 'response_pb2'
  # @@protoc_insertion_point(class_scope:Span)
  })
_sym_db.RegisterMessage(Span)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MATCH_ATTRIBUTESENTRY._options = None
  _MATCH_ATTRIBUTESENTRY._serialized_options = b'8\001'
  _MATCH_UNDERSCOREENTRY._options = None
  _MATCH_UNDERSCOREENTRY._serialized_options = b'8\001'
  _LABELS_ITEMSENTRY._options = None
  _LABELS_ITEMSENTRY._serialized_options = b'8\001'
  _RESPONSES._serialized_start=45
  _RESPONSES._serialized_end=81
  _MATCH._serialized_start=84
  _MATCH._serialized_end=324
  _MATCH_ATTRIBUTESENTRY._serialized_start=202
  _MATCH_ATTRIBUTESENTRY._serialized_end=251
  _MATCH_UNDERSCOREENTRY._serialized_start=253
  _MATCH_UNDERSCOREENTRY._serialized_end=324
  _LABELS._serialized_start=326
  _LABELS._serialized_end=422
  _LABELS_ITEMSENTRY._serialized_start=371
  _LABELS_ITEMSENTRY._serialized_end=422
  _SPAN._serialized_start=424
  _SPAN._serialized_end=458
# @@protoc_insertion_point(module_scope)
