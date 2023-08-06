#!/usr/bin/env bash

set -ex
PROTOC_VERSION="$(protoc --version)"
if [[ "$PROTOC_VERSION" != 'libprotoc 3.6.0' && "$PROTOC_VERSION" != 'libprotoc 3.6.1' ]]; then
	echo "Required libprotoc versions to be 3.6.0 or 3.6.1 (preferred)."
	echo "We found: $PROTOC_VERSION"
	exit 1
fi
PROTOS="databricks_registry_webhooks/protos"
protoc -I="$PROTOS" \
    --python_out="$PROTOS" \
    "$PROTOS"/databricks.proto \
    "$PROTOS"/webhooks.proto \
    "$PROTOS"/scalapb/scalapb.proto

OLD_SCALAPB="from scalapb import scalapb_pb2 as scalapb_dot_scalapb__pb2"
NEW_SCALAPB="from .scalapb import scalapb_pb2 as scalapb_dot_scalapb__pb2"
sed -i'.old' -e "s/$OLD_SCALAPB/$NEW_SCALAPB/g" "$PROTOS/databricks_pb2.py" "$PROTOS/webhooks_pb2.py"

OLD_DATABRICKS="import databricks_pb2 as databricks__pb2"
NEW_DATABRICKS="from . import databricks_pb2 as databricks__pb2"
sed -i'.old' -e "s/$OLD_DATABRICKS/$NEW_DATABRICKS/g" "$PROTOS/webhooks_pb2.py"

rm "$PROTOS/databricks_pb2.py.old"
rm "$PROTOS/webhooks_pb2.py.old"
