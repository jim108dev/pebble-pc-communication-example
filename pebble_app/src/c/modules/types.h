#pragma once // Prevent errors from being included multiple times

#include <pebble.h> // Pebble SDK symbols

#define MAX_TEXT_LEN 100

typedef struct Record
{
    uint8_t id;               //  1 bytes
    char text[MAX_TEXT_LEN];  // 100 bytes
    time_t last_displayed;    //   4 bytes
} Record;                     // 105 bytes

typedef void (*DownloadSuccessCallback)(Record records[], uint8_t max_records);
typedef void (*DownloadFailCallback)(char message[MAX_TEXT_LEN]);

typedef struct CurrentRecord
{
    uint8_t num;
    uint8_t max;
    Record *record;

} CurrentRecord;