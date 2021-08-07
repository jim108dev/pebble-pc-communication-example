#pragma once

#include <pebble.h>
#include "../modules/types.h"
#include "../modules/util.h"

typedef void(DoneCallback)(void *data);

typedef struct InfoConfig
{
    char main[MAX_TEXT_LEN];
    char status[MAX_TEXT_LEN];
    DoneCallback *action;
    void *extra;

} InfoConfig;

void info_window_init(InfoConfig config);
void info_window_set_status(char text[]);
void info_window_set_main(char text[]);