#include "main.h"

static CurrentRecord *s_current = NULL;
static Record *s_record = NULL;

static void garbage_collection()
{
  FREE_SAFE(s_current);
  FREE_SAFE(s_record);
}

static void start_process_item(uint8_t num, uint8_t max)
{
  s_record = malloc(sizeof(Record));
  pers_read_single(num, s_record);

  DEBUG_RECORD(*s_record);

  s_current = malloc(sizeof(CurrentRecord));
  s_current->record = s_record;
  s_current->max = max;
  s_current->num = num;

  on_show_text(s_current);
}

static void on_finish_record(void *data)
{
  CurrentRecord *current = (CurrentRecord *)data;

  DEBUG_RECORD(*current->record);

  current->record->last_displayed = time(NULL);

  pers_write(*current->record, current->num);
  dlog_log(*current->record);


  uint8_t num = current->num + 1;
  uint8_t max = current->max;
  garbage_collection();

  if (num == max)
  {
    dlog_deinit();
    show_summary();
    return;
  }

  start_process_item(num, max);
}

static void on_start_process(void *data)
{
  uint8_t max = pers_read_max_records();
  if (max > 0)
  {
    dlog_init();

    start_process_item(0, max);
  }
}

static void on_show_text(void *data)
{
  CurrentRecord *current = (CurrentRecord *)data;

  DEBUG_RECORD(*current->record);

  InfoConfig c;
  c.action = on_finish_record;
  c.extra = current;

  strcpy(c.main, current->record->text);
  snprintf(c.status, sizeof(c.status), "(%d / %d)", current->num + 1, current->max);

  window_stack_pop_all(true);
  info_window_init(c);
}

static void show_summary()
{
  DEBUG("show_summary");

  InfoConfig c;

  uint8_t max_records = pers_read_max_records();

  if (max_records > 0)
  {
    strcpy(c.main, "Records found.");
  }
  else
  {
    strcpy(c.main, "No records found. Please run 'pebble_upload.py'.");
  }

  snprintf(c.status, sizeof(c.status), "%d records", max_records);
  c.action = on_start_process;

  window_stack_pop_all(true);

  info_window_init(c);
}

static void on_download_success(Record *records, uint8_t max_records)
{
  for (int i = 0; i < max_records; i++)
  {
    pers_write(records[i], i);
  }

  pers_write_max_records(max_records);

  show_summary();
}

static void on_download_fail(char msg[MAX_TEXT_LEN])
{
  info_window_set_main("Download failed. Please try 'pebble_upload.py' again or press select for demo mode");

  download_deinit();
}

static void init()
{
  //pers_sweep();
  AppLaunchReason appLaunchReason = launch_reason();

  show_summary();

  if (appLaunchReason == APP_LAUNCH_PHONE)
  {
    download_init(on_download_success, on_download_fail);
    // If app was launched by phone and close to last app is disabled, always exit to the watchface instead of to the menu
    exit_reason_set(APP_EXIT_ACTION_PERFORMED_SUCCESSFULLY);
  }
}

static void deinit()
{
  dlog_deinit();
  garbage_collection();
}

int main()
{
  init();
  app_event_loop();
  deinit();
}