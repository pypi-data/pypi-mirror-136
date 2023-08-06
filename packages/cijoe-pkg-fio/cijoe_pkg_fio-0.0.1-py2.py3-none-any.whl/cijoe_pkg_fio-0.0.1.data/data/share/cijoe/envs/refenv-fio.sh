#!/usr/bin/env bash

# CIJOE: SSH_* environment variables; setup to SSH into qemu-guest running on localhost
: "${SSH_HOST:=localhost}"; export SSH_HOST
: "${SSH_PORT:=$QEMU_GUEST_SSH_FWD_PORT}"; export SSH_PORT
: "${SSH_USER:=root}"; export SSH_USER
: "${SSH_NO_CHECKS:=1}"; export SSH_NO_CHECKS

#
# fio environment variables
#
# The following variables are used to control the workload run by fio.
# All variables are prefixed by `FIO_` and then contains the name of
# the fio option where possible. Some places the name has been expanded
# to make it more clear what it means.
# Information about each option can be found here:
# https://fio.readthedocs.io/en/latest/fio_doc.html#job-file-parameters
#
# The following is the exact mapping between env names and fio options:
#
# -filename=${FIO_FILENAME}
# --size=${FIO_SIZE}
# --direct=${FIO_IODIRECT}
# --ioengine=${FIO_IOENG_NAME}
# --name=${FIO_TEST_NAME}
# --rw=${FIO_RW}
# --bs=${FIO_BS}
# --iodepth=${FIO_IODEPTH}
# --numjobs=${FIO_NUMJOBS}
# --status-interval=${FIO_STATUS_INTERVAL}
# --output-format=${FIO_OUTPUT_FORMAT}
# --output=${FIO_OUTPUT_FILE}
# --runtime=${FIO_RUNTIME}"

: "${FIO_FILENAME?Must be set and non-empty}"
: "${FIO_BIN:=fio}"
: "${FIO_SIZE:=256M}"
: "${FIO_IODEPTH:=8}"
: "${FIO_BS:=64k}"
: "${FIO_NUMJOBS:=4}"
: "${FIO_IOENGINE:=io_uring}"
: "${FIO_RW:=write}"
: "${FIO_IODIRECT:=1}"
: "${FIO_TEST_NAME:=${CIJ_TEST_NAME}}"
: "${FIO_STATUS_INTERVAL:=20}"
: "${FIO_USE_OFFSET_INCREMENT:=0}"
: "${FIO_OFFSET_INCREMENT:=25%}"
: "${FIO_USE_WRITE_RATE:=0}"
: "${FIO_WRITE_RATE:=250m}"
: "${FIO_OUTPUT_FILE:=/tmp/fio_example.output}"
: "${FIO_OUTPUT_FORMAT:=json}"
: "${FIO_RUNTIME:=50}"

