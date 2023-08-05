# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: k8s.io/apimachinery/pkg/apis/meta/v1/generated.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from armada_client.k8s.io.apimachinery.pkg.runtime import generated_pb2 as k8s_dot_io_dot_apimachinery_dot_pkg_dot_runtime_dot_generated__pb2
from armada_client.k8s.io.apimachinery.pkg.runtime.schema import generated_pb2 as k8s_dot_io_dot_apimachinery_dot_pkg_dot_runtime_dot_schema_dot_generated__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n4k8s.io/apimachinery/pkg/apis/meta/v1/generated.proto\x12$k8s.io.apimachinery.pkg.apis.meta.v1\x1a/k8s.io/apimachinery/pkg/runtime/generated.proto\x1a\x36k8s.io/apimachinery/pkg/runtime/schema/generated.proto\"\xa9\x02\n\x08\x41PIGroup\x12\x0c\n\x04name\x18\x01 \x01(\t\x12P\n\x08versions\x18\x02 \x03(\x0b\x32>.k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersionForDiscovery\x12X\n\x10preferredVersion\x18\x03 \x01(\x0b\x32>.k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersionForDiscovery\x12\x63\n\x1aserverAddressByClientCIDRs\x18\x04 \x03(\x0b\x32?.k8s.io.apimachinery.pkg.apis.meta.v1.ServerAddressByClientCIDR\"N\n\x0c\x41PIGroupList\x12>\n\x06groups\x18\x01 \x03(\x0b\x32..k8s.io.apimachinery.pkg.apis.meta.v1.APIGroup\"\xf3\x01\n\x0b\x41PIResource\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0csingularName\x18\x06 \x01(\t\x12\x12\n\nnamespaced\x18\x02 \x01(\x08\x12\r\n\x05group\x18\x08 \x01(\t\x12\x0f\n\x07version\x18\t \x01(\t\x12\x0c\n\x04kind\x18\x03 \x01(\t\x12:\n\x05verbs\x18\x04 \x01(\x0b\x32+.k8s.io.apimachinery.pkg.apis.meta.v1.Verbs\x12\x12\n\nshortNames\x18\x05 \x03(\t\x12\x12\n\ncategories\x18\x07 \x03(\t\x12\x1a\n\x12storageVersionHash\x18\n \x01(\t\"m\n\x0f\x41PIResourceList\x12\x14\n\x0cgroupVersion\x18\x01 \x01(\t\x12\x44\n\tresources\x18\x02 \x03(\x0b\x32\x31.k8s.io.apimachinery.pkg.apis.meta.v1.APIResource\"\x84\x01\n\x0b\x41PIVersions\x12\x10\n\x08versions\x18\x01 \x03(\t\x12\x63\n\x1aserverAddressByClientCIDRs\x18\x02 \x03(\x0b\x32?.k8s.io.apimachinery.pkg.apis.meta.v1.ServerAddressByClientCIDR\"C\n\x0c\x41pplyOptions\x12\x0e\n\x06\x64ryRun\x18\x01 \x03(\t\x12\r\n\x05\x66orce\x18\x02 \x01(\x08\x12\x14\n\x0c\x66ieldManager\x18\x03 \x01(\t\"\xae\x01\n\tCondition\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x1a\n\x12observedGeneration\x18\x03 \x01(\x03\x12\x46\n\x12lastTransitionTime\x18\x04 \x01(\x0b\x32*.k8s.io.apimachinery.pkg.apis.meta.v1.Time\x12\x0e\n\x06reason\x18\x05 \x01(\t\x12\x0f\n\x07message\x18\x06 \x01(\t\"5\n\rCreateOptions\x12\x0e\n\x06\x64ryRun\x18\x01 \x03(\t\x12\x14\n\x0c\x66ieldManager\x18\x03 \x01(\t\"\xbc\x01\n\rDeleteOptions\x12\x1a\n\x12gracePeriodSeconds\x18\x01 \x01(\x03\x12J\n\rpreconditions\x18\x02 \x01(\x0b\x32\x33.k8s.io.apimachinery.pkg.apis.meta.v1.Preconditions\x12\x18\n\x10orphanDependents\x18\x03 \x01(\x08\x12\x19\n\x11propagationPolicy\x18\x04 \x01(\t\x12\x0e\n\x06\x64ryRun\x18\x05 \x03(\t\"\x1c\n\x08\x44uration\x12\x10\n\x08\x64uration\x18\x01 \x01(\x03\"\x17\n\x08\x46ieldsV1\x12\x0b\n\x03Raw\x18\x01 \x01(\x0c\"%\n\nGetOptions\x12\x17\n\x0fresourceVersion\x18\x01 \x01(\t\"(\n\tGroupKind\x12\r\n\x05group\x18\x01 \x01(\t\x12\x0c\n\x04kind\x18\x02 \x01(\t\"0\n\rGroupResource\x12\r\n\x05group\x18\x01 \x01(\t\x12\x10\n\x08resource\x18\x02 \x01(\t\".\n\x0cGroupVersion\x12\r\n\x05group\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"A\n\x18GroupVersionForDiscovery\x12\x14\n\x0cgroupVersion\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"@\n\x10GroupVersionKind\x12\r\n\x05group\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x0c\n\x04kind\x18\x03 \x01(\t\"H\n\x14GroupVersionResource\x12\r\n\x05group\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x10\n\x08resource\x18\x03 \x01(\t\"\xf8\x01\n\rLabelSelector\x12Y\n\x0bmatchLabels\x18\x01 \x03(\x0b\x32\x44.k8s.io.apimachinery.pkg.apis.meta.v1.LabelSelector.MatchLabelsEntry\x12X\n\x10matchExpressions\x18\x02 \x03(\x0b\x32>.k8s.io.apimachinery.pkg.apis.meta.v1.LabelSelectorRequirement\x1a\x32\n\x10MatchLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"I\n\x18LabelSelectorRequirement\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08operator\x18\x02 \x01(\t\x12\x0e\n\x06values\x18\x03 \x03(\t\"\x86\x01\n\x04List\x12@\n\x08metadata\x18\x01 \x01(\x0b\x32..k8s.io.apimachinery.pkg.apis.meta.v1.ListMeta\x12<\n\x05items\x18\x02 \x03(\x0b\x32-.k8s.io.apimachinery.pkg.runtime.RawExtension\"c\n\x08ListMeta\x12\x10\n\x08selfLink\x18\x01 \x01(\t\x12\x17\n\x0fresourceVersion\x18\x02 \x01(\t\x12\x10\n\x08\x63ontinue\x18\x03 \x01(\t\x12\x1a\n\x12remainingItemCount\x18\x04 \x01(\x03\"\xd7\x01\n\x0bListOptions\x12\x15\n\rlabelSelector\x18\x01 \x01(\t\x12\x15\n\rfieldSelector\x18\x02 \x01(\t\x12\r\n\x05watch\x18\x03 \x01(\x08\x12\x1b\n\x13\x61llowWatchBookmarks\x18\t \x01(\x08\x12\x17\n\x0fresourceVersion\x18\x04 \x01(\t\x12\x1c\n\x14resourceVersionMatch\x18\n \x01(\t\x12\x16\n\x0etimeoutSeconds\x18\x05 \x01(\x03\x12\r\n\x05limit\x18\x07 \x01(\x03\x12\x10\n\x08\x63ontinue\x18\x08 \x01(\t\"\xf1\x01\n\x12ManagedFieldsEntry\x12\x0f\n\x07manager\x18\x01 \x01(\t\x12\x11\n\toperation\x18\x02 \x01(\t\x12\x12\n\napiVersion\x18\x03 \x01(\t\x12\x38\n\x04time\x18\x04 \x01(\x0b\x32*.k8s.io.apimachinery.pkg.apis.meta.v1.Time\x12\x12\n\nfieldsType\x18\x06 \x01(\t\x12@\n\x08\x66ieldsV1\x18\x07 \x01(\x0b\x32..k8s.io.apimachinery.pkg.apis.meta.v1.FieldsV1\x12\x13\n\x0bsubresource\x18\x08 \x01(\t\"+\n\tMicroTime\x12\x0f\n\x07seconds\x18\x01 \x01(\x03\x12\r\n\x05nanos\x18\x02 \x01(\x05\"\x93\x06\n\nObjectMeta\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0cgenerateName\x18\x02 \x01(\t\x12\x11\n\tnamespace\x18\x03 \x01(\t\x12\x10\n\x08selfLink\x18\x04 \x01(\t\x12\x0b\n\x03uid\x18\x05 \x01(\t\x12\x17\n\x0fresourceVersion\x18\x06 \x01(\t\x12\x12\n\ngeneration\x18\x07 \x01(\x03\x12\x45\n\x11\x63reationTimestamp\x18\x08 \x01(\x0b\x32*.k8s.io.apimachinery.pkg.apis.meta.v1.Time\x12\x45\n\x11\x64\x65letionTimestamp\x18\t \x01(\x0b\x32*.k8s.io.apimachinery.pkg.apis.meta.v1.Time\x12\"\n\x1a\x64\x65letionGracePeriodSeconds\x18\n \x01(\x03\x12L\n\x06labels\x18\x0b \x03(\x0b\x32<.k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta.LabelsEntry\x12V\n\x0b\x61nnotations\x18\x0c \x03(\x0b\x32\x41.k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta.AnnotationsEntry\x12M\n\x0fownerReferences\x18\r \x03(\x0b\x32\x34.k8s.io.apimachinery.pkg.apis.meta.v1.OwnerReference\x12\x12\n\nfinalizers\x18\x0e \x03(\t\x12\x13\n\x0b\x63lusterName\x18\x0f \x01(\t\x12O\n\rmanagedFields\x18\x11 \x03(\x0b\x32\x38.k8s.io.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a\x32\n\x10\x41nnotationsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"}\n\x0eOwnerReference\x12\x12\n\napiVersion\x18\x05 \x01(\t\x12\x0c\n\x04kind\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x0b\n\x03uid\x18\x04 \x01(\t\x12\x12\n\ncontroller\x18\x06 \x01(\x08\x12\x1a\n\x12\x62lockOwnerDeletion\x18\x07 \x01(\x08\"[\n\x15PartialObjectMetadata\x12\x42\n\x08metadata\x18\x01 \x01(\x0b\x32\x30.k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta\"\xa9\x01\n\x19PartialObjectMetadataList\x12@\n\x08metadata\x18\x01 \x01(\x0b\x32..k8s.io.apimachinery.pkg.apis.meta.v1.ListMeta\x12J\n\x05items\x18\x02 \x03(\x0b\x32;.k8s.io.apimachinery.pkg.apis.meta.v1.PartialObjectMetadata\"\x07\n\x05Patch\"C\n\x0cPatchOptions\x12\x0e\n\x06\x64ryRun\x18\x01 \x03(\t\x12\r\n\x05\x66orce\x18\x02 \x01(\x08\x12\x14\n\x0c\x66ieldManager\x18\x03 \x01(\t\"5\n\rPreconditions\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x17\n\x0fresourceVersion\x18\x02 \x01(\t\"\x1a\n\tRootPaths\x12\r\n\x05paths\x18\x01 \x03(\t\"F\n\x19ServerAddressByClientCIDR\x12\x12\n\nclientCIDR\x18\x01 \x01(\t\x12\x15\n\rserverAddress\x18\x02 \x01(\t\"\xcf\x01\n\x06Status\x12@\n\x08metadata\x18\x01 \x01(\x0b\x32..k8s.io.apimachinery.pkg.apis.meta.v1.ListMeta\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x0e\n\x06reason\x18\x04 \x01(\t\x12\x44\n\x07\x64\x65tails\x18\x05 \x01(\x0b\x32\x33.k8s.io.apimachinery.pkg.apis.meta.v1.StatusDetails\x12\x0c\n\x04\x63ode\x18\x06 \x01(\x05\"=\n\x0bStatusCause\x12\x0e\n\x06reason\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\r\n\x05\x66ield\x18\x03 \x01(\t\"\xa5\x01\n\rStatusDetails\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05group\x18\x02 \x01(\t\x12\x0c\n\x04kind\x18\x03 \x01(\t\x12\x0b\n\x03uid\x18\x06 \x01(\t\x12\x41\n\x06\x63\x61uses\x18\x04 \x03(\x0b\x32\x31.k8s.io.apimachinery.pkg.apis.meta.v1.StatusCause\x12\x19\n\x11retryAfterSeconds\x18\x05 \x01(\x05\"%\n\x0cTableOptions\x12\x15\n\rincludeObject\x18\x01 \x01(\t\"&\n\x04Time\x12\x0f\n\x07seconds\x18\x01 \x01(\x03\x12\r\n\x05nanos\x18\x02 \x01(\x05\"+\n\tTimestamp\x12\x0f\n\x07seconds\x18\x01 \x01(\x03\x12\r\n\x05nanos\x18\x02 \x01(\x05\",\n\x08TypeMeta\x12\x0c\n\x04kind\x18\x01 \x01(\t\x12\x12\n\napiVersion\x18\x02 \x01(\t\"5\n\rUpdateOptions\x12\x0e\n\x06\x64ryRun\x18\x01 \x03(\t\x12\x14\n\x0c\x66ieldManager\x18\x02 \x01(\t\"\x16\n\x05Verbs\x12\r\n\x05items\x18\x01 \x03(\t\"Y\n\nWatchEvent\x12\x0c\n\x04type\x18\x01 \x01(\t\x12=\n\x06object\x18\x02 \x01(\x0b\x32-.k8s.io.apimachinery.pkg.runtime.RawExtensionB\x04Z\x02v1')



_APIGROUP = DESCRIPTOR.message_types_by_name['APIGroup']
_APIGROUPLIST = DESCRIPTOR.message_types_by_name['APIGroupList']
_APIRESOURCE = DESCRIPTOR.message_types_by_name['APIResource']
_APIRESOURCELIST = DESCRIPTOR.message_types_by_name['APIResourceList']
_APIVERSIONS = DESCRIPTOR.message_types_by_name['APIVersions']
_APPLYOPTIONS = DESCRIPTOR.message_types_by_name['ApplyOptions']
_CONDITION = DESCRIPTOR.message_types_by_name['Condition']
_CREATEOPTIONS = DESCRIPTOR.message_types_by_name['CreateOptions']
_DELETEOPTIONS = DESCRIPTOR.message_types_by_name['DeleteOptions']
_DURATION = DESCRIPTOR.message_types_by_name['Duration']
_FIELDSV1 = DESCRIPTOR.message_types_by_name['FieldsV1']
_GETOPTIONS = DESCRIPTOR.message_types_by_name['GetOptions']
_GROUPKIND = DESCRIPTOR.message_types_by_name['GroupKind']
_GROUPRESOURCE = DESCRIPTOR.message_types_by_name['GroupResource']
_GROUPVERSION = DESCRIPTOR.message_types_by_name['GroupVersion']
_GROUPVERSIONFORDISCOVERY = DESCRIPTOR.message_types_by_name['GroupVersionForDiscovery']
_GROUPVERSIONKIND = DESCRIPTOR.message_types_by_name['GroupVersionKind']
_GROUPVERSIONRESOURCE = DESCRIPTOR.message_types_by_name['GroupVersionResource']
_LABELSELECTOR = DESCRIPTOR.message_types_by_name['LabelSelector']
_LABELSELECTOR_MATCHLABELSENTRY = _LABELSELECTOR.nested_types_by_name['MatchLabelsEntry']
_LABELSELECTORREQUIREMENT = DESCRIPTOR.message_types_by_name['LabelSelectorRequirement']
_LIST = DESCRIPTOR.message_types_by_name['List']
_LISTMETA = DESCRIPTOR.message_types_by_name['ListMeta']
_LISTOPTIONS = DESCRIPTOR.message_types_by_name['ListOptions']
_MANAGEDFIELDSENTRY = DESCRIPTOR.message_types_by_name['ManagedFieldsEntry']
_MICROTIME = DESCRIPTOR.message_types_by_name['MicroTime']
_OBJECTMETA = DESCRIPTOR.message_types_by_name['ObjectMeta']
_OBJECTMETA_LABELSENTRY = _OBJECTMETA.nested_types_by_name['LabelsEntry']
_OBJECTMETA_ANNOTATIONSENTRY = _OBJECTMETA.nested_types_by_name['AnnotationsEntry']
_OWNERREFERENCE = DESCRIPTOR.message_types_by_name['OwnerReference']
_PARTIALOBJECTMETADATA = DESCRIPTOR.message_types_by_name['PartialObjectMetadata']
_PARTIALOBJECTMETADATALIST = DESCRIPTOR.message_types_by_name['PartialObjectMetadataList']
_PATCH = DESCRIPTOR.message_types_by_name['Patch']
_PATCHOPTIONS = DESCRIPTOR.message_types_by_name['PatchOptions']
_PRECONDITIONS = DESCRIPTOR.message_types_by_name['Preconditions']
_ROOTPATHS = DESCRIPTOR.message_types_by_name['RootPaths']
_SERVERADDRESSBYCLIENTCIDR = DESCRIPTOR.message_types_by_name['ServerAddressByClientCIDR']
_STATUS = DESCRIPTOR.message_types_by_name['Status']
_STATUSCAUSE = DESCRIPTOR.message_types_by_name['StatusCause']
_STATUSDETAILS = DESCRIPTOR.message_types_by_name['StatusDetails']
_TABLEOPTIONS = DESCRIPTOR.message_types_by_name['TableOptions']
_TIME = DESCRIPTOR.message_types_by_name['Time']
_TIMESTAMP = DESCRIPTOR.message_types_by_name['Timestamp']
_TYPEMETA = DESCRIPTOR.message_types_by_name['TypeMeta']
_UPDATEOPTIONS = DESCRIPTOR.message_types_by_name['UpdateOptions']
_VERBS = DESCRIPTOR.message_types_by_name['Verbs']
_WATCHEVENT = DESCRIPTOR.message_types_by_name['WatchEvent']
APIGroup = _reflection.GeneratedProtocolMessageType('APIGroup', (_message.Message,), {
  'DESCRIPTOR' : _APIGROUP,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.APIGroup)
  })
_sym_db.RegisterMessage(APIGroup)

APIGroupList = _reflection.GeneratedProtocolMessageType('APIGroupList', (_message.Message,), {
  'DESCRIPTOR' : _APIGROUPLIST,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.APIGroupList)
  })
_sym_db.RegisterMessage(APIGroupList)

APIResource = _reflection.GeneratedProtocolMessageType('APIResource', (_message.Message,), {
  'DESCRIPTOR' : _APIRESOURCE,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.APIResource)
  })
_sym_db.RegisterMessage(APIResource)

APIResourceList = _reflection.GeneratedProtocolMessageType('APIResourceList', (_message.Message,), {
  'DESCRIPTOR' : _APIRESOURCELIST,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.APIResourceList)
  })
_sym_db.RegisterMessage(APIResourceList)

APIVersions = _reflection.GeneratedProtocolMessageType('APIVersions', (_message.Message,), {
  'DESCRIPTOR' : _APIVERSIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.APIVersions)
  })
_sym_db.RegisterMessage(APIVersions)

ApplyOptions = _reflection.GeneratedProtocolMessageType('ApplyOptions', (_message.Message,), {
  'DESCRIPTOR' : _APPLYOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ApplyOptions)
  })
_sym_db.RegisterMessage(ApplyOptions)

Condition = _reflection.GeneratedProtocolMessageType('Condition', (_message.Message,), {
  'DESCRIPTOR' : _CONDITION,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Condition)
  })
_sym_db.RegisterMessage(Condition)

CreateOptions = _reflection.GeneratedProtocolMessageType('CreateOptions', (_message.Message,), {
  'DESCRIPTOR' : _CREATEOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.CreateOptions)
  })
_sym_db.RegisterMessage(CreateOptions)

DeleteOptions = _reflection.GeneratedProtocolMessageType('DeleteOptions', (_message.Message,), {
  'DESCRIPTOR' : _DELETEOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.DeleteOptions)
  })
_sym_db.RegisterMessage(DeleteOptions)

Duration = _reflection.GeneratedProtocolMessageType('Duration', (_message.Message,), {
  'DESCRIPTOR' : _DURATION,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Duration)
  })
_sym_db.RegisterMessage(Duration)

FieldsV1 = _reflection.GeneratedProtocolMessageType('FieldsV1', (_message.Message,), {
  'DESCRIPTOR' : _FIELDSV1,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.FieldsV1)
  })
_sym_db.RegisterMessage(FieldsV1)

GetOptions = _reflection.GeneratedProtocolMessageType('GetOptions', (_message.Message,), {
  'DESCRIPTOR' : _GETOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GetOptions)
  })
_sym_db.RegisterMessage(GetOptions)

GroupKind = _reflection.GeneratedProtocolMessageType('GroupKind', (_message.Message,), {
  'DESCRIPTOR' : _GROUPKIND,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupKind)
  })
_sym_db.RegisterMessage(GroupKind)

GroupResource = _reflection.GeneratedProtocolMessageType('GroupResource', (_message.Message,), {
  'DESCRIPTOR' : _GROUPRESOURCE,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupResource)
  })
_sym_db.RegisterMessage(GroupResource)

GroupVersion = _reflection.GeneratedProtocolMessageType('GroupVersion', (_message.Message,), {
  'DESCRIPTOR' : _GROUPVERSION,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersion)
  })
_sym_db.RegisterMessage(GroupVersion)

GroupVersionForDiscovery = _reflection.GeneratedProtocolMessageType('GroupVersionForDiscovery', (_message.Message,), {
  'DESCRIPTOR' : _GROUPVERSIONFORDISCOVERY,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersionForDiscovery)
  })
_sym_db.RegisterMessage(GroupVersionForDiscovery)

GroupVersionKind = _reflection.GeneratedProtocolMessageType('GroupVersionKind', (_message.Message,), {
  'DESCRIPTOR' : _GROUPVERSIONKIND,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersionKind)
  })
_sym_db.RegisterMessage(GroupVersionKind)

GroupVersionResource = _reflection.GeneratedProtocolMessageType('GroupVersionResource', (_message.Message,), {
  'DESCRIPTOR' : _GROUPVERSIONRESOURCE,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.GroupVersionResource)
  })
_sym_db.RegisterMessage(GroupVersionResource)

LabelSelector = _reflection.GeneratedProtocolMessageType('LabelSelector', (_message.Message,), {

  'MatchLabelsEntry' : _reflection.GeneratedProtocolMessageType('MatchLabelsEntry', (_message.Message,), {
    'DESCRIPTOR' : _LABELSELECTOR_MATCHLABELSENTRY,
    '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
    # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.LabelSelector.MatchLabelsEntry)
    })
  ,
  'DESCRIPTOR' : _LABELSELECTOR,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.LabelSelector)
  })
_sym_db.RegisterMessage(LabelSelector)
_sym_db.RegisterMessage(LabelSelector.MatchLabelsEntry)

LabelSelectorRequirement = _reflection.GeneratedProtocolMessageType('LabelSelectorRequirement', (_message.Message,), {
  'DESCRIPTOR' : _LABELSELECTORREQUIREMENT,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.LabelSelectorRequirement)
  })
_sym_db.RegisterMessage(LabelSelectorRequirement)

List = _reflection.GeneratedProtocolMessageType('List', (_message.Message,), {
  'DESCRIPTOR' : _LIST,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.List)
  })
_sym_db.RegisterMessage(List)

ListMeta = _reflection.GeneratedProtocolMessageType('ListMeta', (_message.Message,), {
  'DESCRIPTOR' : _LISTMETA,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ListMeta)
  })
_sym_db.RegisterMessage(ListMeta)

ListOptions = _reflection.GeneratedProtocolMessageType('ListOptions', (_message.Message,), {
  'DESCRIPTOR' : _LISTOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ListOptions)
  })
_sym_db.RegisterMessage(ListOptions)

ManagedFieldsEntry = _reflection.GeneratedProtocolMessageType('ManagedFieldsEntry', (_message.Message,), {
  'DESCRIPTOR' : _MANAGEDFIELDSENTRY,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ManagedFieldsEntry)
  })
_sym_db.RegisterMessage(ManagedFieldsEntry)

MicroTime = _reflection.GeneratedProtocolMessageType('MicroTime', (_message.Message,), {
  'DESCRIPTOR' : _MICROTIME,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.MicroTime)
  })
_sym_db.RegisterMessage(MicroTime)

ObjectMeta = _reflection.GeneratedProtocolMessageType('ObjectMeta', (_message.Message,), {

  'LabelsEntry' : _reflection.GeneratedProtocolMessageType('LabelsEntry', (_message.Message,), {
    'DESCRIPTOR' : _OBJECTMETA_LABELSENTRY,
    '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
    # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta.LabelsEntry)
    })
  ,

  'AnnotationsEntry' : _reflection.GeneratedProtocolMessageType('AnnotationsEntry', (_message.Message,), {
    'DESCRIPTOR' : _OBJECTMETA_ANNOTATIONSENTRY,
    '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
    # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta.AnnotationsEntry)
    })
  ,
  'DESCRIPTOR' : _OBJECTMETA,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ObjectMeta)
  })
_sym_db.RegisterMessage(ObjectMeta)
_sym_db.RegisterMessage(ObjectMeta.LabelsEntry)
_sym_db.RegisterMessage(ObjectMeta.AnnotationsEntry)

OwnerReference = _reflection.GeneratedProtocolMessageType('OwnerReference', (_message.Message,), {
  'DESCRIPTOR' : _OWNERREFERENCE,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.OwnerReference)
  })
_sym_db.RegisterMessage(OwnerReference)

PartialObjectMetadata = _reflection.GeneratedProtocolMessageType('PartialObjectMetadata', (_message.Message,), {
  'DESCRIPTOR' : _PARTIALOBJECTMETADATA,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.PartialObjectMetadata)
  })
_sym_db.RegisterMessage(PartialObjectMetadata)

PartialObjectMetadataList = _reflection.GeneratedProtocolMessageType('PartialObjectMetadataList', (_message.Message,), {
  'DESCRIPTOR' : _PARTIALOBJECTMETADATALIST,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.PartialObjectMetadataList)
  })
_sym_db.RegisterMessage(PartialObjectMetadataList)

Patch = _reflection.GeneratedProtocolMessageType('Patch', (_message.Message,), {
  'DESCRIPTOR' : _PATCH,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Patch)
  })
_sym_db.RegisterMessage(Patch)

PatchOptions = _reflection.GeneratedProtocolMessageType('PatchOptions', (_message.Message,), {
  'DESCRIPTOR' : _PATCHOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.PatchOptions)
  })
_sym_db.RegisterMessage(PatchOptions)

Preconditions = _reflection.GeneratedProtocolMessageType('Preconditions', (_message.Message,), {
  'DESCRIPTOR' : _PRECONDITIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Preconditions)
  })
_sym_db.RegisterMessage(Preconditions)

RootPaths = _reflection.GeneratedProtocolMessageType('RootPaths', (_message.Message,), {
  'DESCRIPTOR' : _ROOTPATHS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.RootPaths)
  })
_sym_db.RegisterMessage(RootPaths)

ServerAddressByClientCIDR = _reflection.GeneratedProtocolMessageType('ServerAddressByClientCIDR', (_message.Message,), {
  'DESCRIPTOR' : _SERVERADDRESSBYCLIENTCIDR,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.ServerAddressByClientCIDR)
  })
_sym_db.RegisterMessage(ServerAddressByClientCIDR)

Status = _reflection.GeneratedProtocolMessageType('Status', (_message.Message,), {
  'DESCRIPTOR' : _STATUS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Status)
  })
_sym_db.RegisterMessage(Status)

StatusCause = _reflection.GeneratedProtocolMessageType('StatusCause', (_message.Message,), {
  'DESCRIPTOR' : _STATUSCAUSE,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.StatusCause)
  })
_sym_db.RegisterMessage(StatusCause)

StatusDetails = _reflection.GeneratedProtocolMessageType('StatusDetails', (_message.Message,), {
  'DESCRIPTOR' : _STATUSDETAILS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.StatusDetails)
  })
_sym_db.RegisterMessage(StatusDetails)

TableOptions = _reflection.GeneratedProtocolMessageType('TableOptions', (_message.Message,), {
  'DESCRIPTOR' : _TABLEOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.TableOptions)
  })
_sym_db.RegisterMessage(TableOptions)

Time = _reflection.GeneratedProtocolMessageType('Time', (_message.Message,), {
  'DESCRIPTOR' : _TIME,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Time)
  })
_sym_db.RegisterMessage(Time)

Timestamp = _reflection.GeneratedProtocolMessageType('Timestamp', (_message.Message,), {
  'DESCRIPTOR' : _TIMESTAMP,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Timestamp)
  })
_sym_db.RegisterMessage(Timestamp)

TypeMeta = _reflection.GeneratedProtocolMessageType('TypeMeta', (_message.Message,), {
  'DESCRIPTOR' : _TYPEMETA,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.TypeMeta)
  })
_sym_db.RegisterMessage(TypeMeta)

UpdateOptions = _reflection.GeneratedProtocolMessageType('UpdateOptions', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEOPTIONS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.UpdateOptions)
  })
_sym_db.RegisterMessage(UpdateOptions)

Verbs = _reflection.GeneratedProtocolMessageType('Verbs', (_message.Message,), {
  'DESCRIPTOR' : _VERBS,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.Verbs)
  })
_sym_db.RegisterMessage(Verbs)

WatchEvent = _reflection.GeneratedProtocolMessageType('WatchEvent', (_message.Message,), {
  'DESCRIPTOR' : _WATCHEVENT,
  '__module__' : 'k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2'
  # @@protoc_insertion_point(class_scope:k8s.io.apimachinery.pkg.apis.meta.v1.WatchEvent)
  })
_sym_db.RegisterMessage(WatchEvent)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\002v1'
  _LABELSELECTOR_MATCHLABELSENTRY._options = None
  _LABELSELECTOR_MATCHLABELSENTRY._serialized_options = b'8\001'
  _OBJECTMETA_LABELSENTRY._options = None
  _OBJECTMETA_LABELSENTRY._serialized_options = b'8\001'
  _OBJECTMETA_ANNOTATIONSENTRY._options = None
  _OBJECTMETA_ANNOTATIONSENTRY._serialized_options = b'8\001'
  _APIGROUP._serialized_start=200
  _APIGROUP._serialized_end=497
  _APIGROUPLIST._serialized_start=499
  _APIGROUPLIST._serialized_end=577
  _APIRESOURCE._serialized_start=580
  _APIRESOURCE._serialized_end=823
  _APIRESOURCELIST._serialized_start=825
  _APIRESOURCELIST._serialized_end=934
  _APIVERSIONS._serialized_start=937
  _APIVERSIONS._serialized_end=1069
  _APPLYOPTIONS._serialized_start=1071
  _APPLYOPTIONS._serialized_end=1138
  _CONDITION._serialized_start=1141
  _CONDITION._serialized_end=1315
  _CREATEOPTIONS._serialized_start=1317
  _CREATEOPTIONS._serialized_end=1370
  _DELETEOPTIONS._serialized_start=1373
  _DELETEOPTIONS._serialized_end=1561
  _DURATION._serialized_start=1563
  _DURATION._serialized_end=1591
  _FIELDSV1._serialized_start=1593
  _FIELDSV1._serialized_end=1616
  _GETOPTIONS._serialized_start=1618
  _GETOPTIONS._serialized_end=1655
  _GROUPKIND._serialized_start=1657
  _GROUPKIND._serialized_end=1697
  _GROUPRESOURCE._serialized_start=1699
  _GROUPRESOURCE._serialized_end=1747
  _GROUPVERSION._serialized_start=1749
  _GROUPVERSION._serialized_end=1795
  _GROUPVERSIONFORDISCOVERY._serialized_start=1797
  _GROUPVERSIONFORDISCOVERY._serialized_end=1862
  _GROUPVERSIONKIND._serialized_start=1864
  _GROUPVERSIONKIND._serialized_end=1928
  _GROUPVERSIONRESOURCE._serialized_start=1930
  _GROUPVERSIONRESOURCE._serialized_end=2002
  _LABELSELECTOR._serialized_start=2005
  _LABELSELECTOR._serialized_end=2253
  _LABELSELECTOR_MATCHLABELSENTRY._serialized_start=2203
  _LABELSELECTOR_MATCHLABELSENTRY._serialized_end=2253
  _LABELSELECTORREQUIREMENT._serialized_start=2255
  _LABELSELECTORREQUIREMENT._serialized_end=2328
  _LIST._serialized_start=2331
  _LIST._serialized_end=2465
  _LISTMETA._serialized_start=2467
  _LISTMETA._serialized_end=2566
  _LISTOPTIONS._serialized_start=2569
  _LISTOPTIONS._serialized_end=2784
  _MANAGEDFIELDSENTRY._serialized_start=2787
  _MANAGEDFIELDSENTRY._serialized_end=3028
  _MICROTIME._serialized_start=3030
  _MICROTIME._serialized_end=3073
  _OBJECTMETA._serialized_start=3076
  _OBJECTMETA._serialized_end=3863
  _OBJECTMETA_LABELSENTRY._serialized_start=3766
  _OBJECTMETA_LABELSENTRY._serialized_end=3811
  _OBJECTMETA_ANNOTATIONSENTRY._serialized_start=3813
  _OBJECTMETA_ANNOTATIONSENTRY._serialized_end=3863
  _OWNERREFERENCE._serialized_start=3865
  _OWNERREFERENCE._serialized_end=3990
  _PARTIALOBJECTMETADATA._serialized_start=3992
  _PARTIALOBJECTMETADATA._serialized_end=4083
  _PARTIALOBJECTMETADATALIST._serialized_start=4086
  _PARTIALOBJECTMETADATALIST._serialized_end=4255
  _PATCH._serialized_start=4257
  _PATCH._serialized_end=4264
  _PATCHOPTIONS._serialized_start=4266
  _PATCHOPTIONS._serialized_end=4333
  _PRECONDITIONS._serialized_start=4335
  _PRECONDITIONS._serialized_end=4388
  _ROOTPATHS._serialized_start=4390
  _ROOTPATHS._serialized_end=4416
  _SERVERADDRESSBYCLIENTCIDR._serialized_start=4418
  _SERVERADDRESSBYCLIENTCIDR._serialized_end=4488
  _STATUS._serialized_start=4491
  _STATUS._serialized_end=4698
  _STATUSCAUSE._serialized_start=4700
  _STATUSCAUSE._serialized_end=4761
  _STATUSDETAILS._serialized_start=4764
  _STATUSDETAILS._serialized_end=4929
  _TABLEOPTIONS._serialized_start=4931
  _TABLEOPTIONS._serialized_end=4968
  _TIME._serialized_start=4970
  _TIME._serialized_end=5008
  _TIMESTAMP._serialized_start=5010
  _TIMESTAMP._serialized_end=5053
  _TYPEMETA._serialized_start=5055
  _TYPEMETA._serialized_end=5099
  _UPDATEOPTIONS._serialized_start=5101
  _UPDATEOPTIONS._serialized_end=5154
  _VERBS._serialized_start=5156
  _VERBS._serialized_end=5178
  _WATCHEVENT._serialized_start=5180
  _WATCHEVENT._serialized_end=5269
# @@protoc_insertion_point(module_scope)
