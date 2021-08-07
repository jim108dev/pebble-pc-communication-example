#pragma once // Prevent errors from being included multiple times

#include <pebble.h>
#include "types.h"
#include "util.h"

//private
#define LOG_TAG 1
typedef struct DLogRecord
{
    uint8_t id;                //  1 bytes
    time_t last_displayed;    //   4 bytes
} DLogRecord;  


//public
void dlog_init();

void dlog_log(Record record);

void dlog_deinit();


