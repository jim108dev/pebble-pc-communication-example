#pragma once // Prevent errors from being included multiple times

#include "types.h"
#include <pebble-packet/pebble-packet.h>

uint8_t packet_get_uint8(DictionaryIterator *inbox_iter, int key);
void time_to_string(char buf[MAX_TEXT_LEN], time_t rawtime);
void record_to_string(char buf[MAX_TEXT_LEN], Record r);

//Replaced __FILE__ by __FUNCTION__ because it is more helpful.
#define DEBUG(...) app_log(APP_LOG_LEVEL_DEBUG, __FUNCTION__, __LINE__, __VA_ARGS__)

#define DEBUG_RECORD(record) char debug_buf[MAX_TEXT_LEN]; record_to_string(debug_buf, record); DEBUG(debug_buf);

#define FREE_SAFE(ptr) if (NULL != ptr) { free(ptr); ptr = NULL; }