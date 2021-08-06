#include <pebble.h>

#include "modules/download.h"
#include "modules/dlog.h"
#include "modules/pers.h"
#include "modules/types.h"
#include "modules/util.h"
#include "windows/info_window.h"
#include <@smallstoneapps/utils/macros.h>

static void garbage_collection();
static void on_finish_record(void *data);
static void on_show_text(void *data);
static void show_summary();
static void on_download_success(Record *records, uint8_t max_records);
static void on_download_fail(char *msg);
static void init();
static void deinit();