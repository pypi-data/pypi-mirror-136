# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tfx/proto/orchestration/run_state.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='tfx/proto/orchestration/run_state.proto',
  package='tfx.orchestration',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\'tfx/proto/orchestration/run_state.proto\x12\x11tfx.orchestration\"\xa2\x02\n\x08RunState\x12\x30\n\x05state\x18\x01 \x01(\x0e\x32!.tfx.orchestration.RunState.State\x12@\n\x0bstatus_code\x18\x03 \x01(\x0b\x32+.tfx.orchestration.RunState.StatusCodeValue\x12\x12\n\nstatus_msg\x18\x02 \x01(\t\x1a \n\x0fStatusCodeValue\x12\r\n\x05value\x18\x01 \x01(\x05\"l\n\x05State\x12\x0b\n\x07UNKNOWN\x10\x00\x12\t\n\x05READY\x10\x01\x12\x0b\n\x07RUNNING\x10\x02\x12\x0c\n\x08\x43OMPLETE\x10\x03\x12\x0b\n\x07SKIPPED\x10\x04\x12\n\n\x06PAUSED\x10\x05\x12\x0b\n\x07STOPPED\x10\x06\x12\n\n\x06\x46\x41ILED\x10\x07\x62\x06proto3')
)



_RUNSTATE_STATE = _descriptor.EnumDescriptor(
  name='State',
  full_name='tfx.orchestration.RunState.State',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='READY', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RUNNING', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMPLETE', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SKIPPED', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PAUSED', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STOPPED', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILED', index=7, number=7,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=245,
  serialized_end=353,
)
_sym_db.RegisterEnumDescriptor(_RUNSTATE_STATE)


_RUNSTATE_STATUSCODEVALUE = _descriptor.Descriptor(
  name='StatusCodeValue',
  full_name='tfx.orchestration.RunState.StatusCodeValue',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='tfx.orchestration.RunState.StatusCodeValue.value', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=211,
  serialized_end=243,
)

_RUNSTATE = _descriptor.Descriptor(
  name='RunState',
  full_name='tfx.orchestration.RunState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='state', full_name='tfx.orchestration.RunState.state', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status_code', full_name='tfx.orchestration.RunState.status_code', index=1,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status_msg', full_name='tfx.orchestration.RunState.status_msg', index=2,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_RUNSTATE_STATUSCODEVALUE, ],
  enum_types=[
    _RUNSTATE_STATE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=63,
  serialized_end=353,
)

_RUNSTATE_STATUSCODEVALUE.containing_type = _RUNSTATE
_RUNSTATE.fields_by_name['state'].enum_type = _RUNSTATE_STATE
_RUNSTATE.fields_by_name['status_code'].message_type = _RUNSTATE_STATUSCODEVALUE
_RUNSTATE_STATE.containing_type = _RUNSTATE
DESCRIPTOR.message_types_by_name['RunState'] = _RUNSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

RunState = _reflection.GeneratedProtocolMessageType('RunState', (_message.Message,), {

  'StatusCodeValue' : _reflection.GeneratedProtocolMessageType('StatusCodeValue', (_message.Message,), {
    'DESCRIPTOR' : _RUNSTATE_STATUSCODEVALUE,
    '__module__' : 'tfx.proto.orchestration.run_state_pb2'
    # @@protoc_insertion_point(class_scope:tfx.orchestration.RunState.StatusCodeValue)
    })
  ,
  'DESCRIPTOR' : _RUNSTATE,
  '__module__' : 'tfx.proto.orchestration.run_state_pb2'
  # @@protoc_insertion_point(class_scope:tfx.orchestration.RunState)
  })
_sym_db.RegisterMessage(RunState)
_sym_db.RegisterMessage(RunState.StatusCodeValue)


# @@protoc_insertion_point(module_scope)
