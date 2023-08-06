#!/bin/bash
#
# Example of invoking fio with arguments and collecting output files
#
# In addition to the variables defined in the fio-module, then this script also requires the
# definition of FIO_FILENAME, with an absolute path to a device or file to read from
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

# Define these in the environment or testplan
: "${FIO_FILENAME?Must be set and non-empty}"
: "${FIO_OUTPUT_FILE:=/tmp/fio_example.output}"

# Remove the output-file if it already exists
if cij.cmd "[[ -f ${FIO_OUTPUT_FILE} ]] && rm ${FIO_OUTPUT_FILE} || true"; then
  cij.err "Failed removing ${FIO_OUTPUT_FILE}"
  test.fail
fi

# Setup arguments for fio
FIO_ARGS="${FIO_ARGS} --filename=${FIO_FILENAME}"
FIO_ARGS="${FIO_ARGS} --name=${CIJ_TEST_NAME}"
FIO_ARGS="${FIO_ARGS} --size=256M"
FIO_ARGS="${FIO_ARGS} --iodepth=8"
FIO_ARGS="${FIO_ARGS} --bs=64k"
FIO_ARGS="${FIO_ARGS} --numjobs=4"
FIO_ARGS="${FIO_ARGS} --ioengine=io_uring"
FIO_ARGS="${FIO_ARGS} --direct=1"
FIO_ARGS="${FIO_ARGS} --runtime=50"
FIO_ARGS="${FIO_ARGS} --rw=randread"
FIO_ARGS="${FIO_ARGS} --output-format=json"
FIO_ARGS="${FIO_ARGS} --output=${FIO_OUTPUT_FILE}"

# Run fio
if fio.run; then
  cij.err "Check the logs, to see what went wrong"
  test.fail
fi

# Fetch the fio output file to local storage such that we can extract data from it using
# cij_extractor
cij.pull "${FIO_OUTPUT_FILE}" "${CIJ_TEST_AUX_ROOT}/fio-output-$(basename $FIO_OUTPUT_FILE)"

test.pass
