#include "download.h"

static DownloadSuccessCallback s_success;
static DownloadFailCallback s_fail;
static uint8_t s_num_received = 0;
static Record *s_records = NULL;
static EventHandle s_app_message_handle = NULL;
static AppTimer *s_timeout_timer = NULL;

static uint8_t s_max_records = 0;

void close_connection()
{
  if (s_timeout_timer != NULL)
  {
    app_timer_cancel(s_timeout_timer);
    s_timeout_timer = NULL;
  }
  if (s_app_message_handle != NULL)
  {
    events_app_message_unsubscribe(s_app_message_handle);
    s_app_message_handle = NULL;
  }
}

Record parse_data(char *data)
{
  ProcessingState *state = data_processor_create(data, ';');

  Record r;
  r.id = data_processor_get_int(state);
  strcpy(r.text, data_processor_get_string(state));
  r.last_displayed = data_processor_get_int(state);

  data_processor_destroy(state);
  return r;
}

static void inbox_received_handler(DictionaryIterator *iter, void *context)
{
  DEBUG("Inbox received");

  if (packet_contains_key(iter, DOWNLOAD_KEY_MAX))
  {
    s_max_records = packet_get_uint8(iter, DOWNLOAD_KEY_MAX);
    s_records = malloc(sizeof(Record) * s_max_records);

    DEBUG("Max key received");
    return;
  }

  if (packet_contains_key(iter, DOWNLOAD_KEY_DATA))
  {
    char *data = packet_get_string(iter, DOWNLOAD_KEY_DATA);

    if (s_max_records == 0)
    {
      s_fail("Max records is 0");
      return;
    }

    Record record = parse_data(data);

    s_records[s_num_received] = record;

    s_num_received++;

    if (s_num_received == s_max_records)
    {
      close_connection();
      s_success(s_records, s_num_received);
    }

    return;
  }

  DEBUG("Unknown message received");
}

static void timeout_timer_handler(void *context)
{
  s_timeout_timer = NULL;
  close_connection();
  s_fail("Connection timeout");
}

void download_init(DownloadSuccessCallback success,DownloadFailCallback fail)
{
  s_success = success;
  s_fail = fail;
  s_app_message_handle = events_app_message_subscribe_handlers((EventAppMessageHandlers){
                                                                   .received = inbox_received_handler},
                                                               NULL);
  events_app_message_request_inbox_size(INBOX_SIZE);
  events_app_message_request_outbox_size(OUTBOX_SIZE);
  events_app_message_open();

  s_timeout_timer = app_timer_register(TIMEOUT, timeout_timer_handler, NULL);

  DEBUG("Waiting for connection");
}

void download_deinit()
{
  close_connection();
  if (s_records != NULL)
  {
    free(s_records);
    s_records = NULL;
  }
}
