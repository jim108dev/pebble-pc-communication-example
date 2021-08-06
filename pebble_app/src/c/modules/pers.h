#pragma once // Prevent errors from being included multiple times

#include <pebble.h> // Pebble SDK symbols
#include <@smallstoneapps/utils/macros.h>
#include "types.h"
#define RECORDS_OFFSET 10
#define MAX_RECORDS_KEY 0
#define UPLOADED_DATE_KEY 1
#define LAST_TESTED_KEY 2

uint8_t pers_read_max_records();

void pers_write_max_records(uint8_t max);

void pers_read_single(uint8_t num, Record* buf);

void pers_read_all(Record *buf);

void pers_write(Record record, uint num);

void pers_sweep();