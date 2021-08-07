#include "dlog.h"
#include "types.h"
#include "util.h"

static DataLoggingSessionRef s_session_ref = NULL;

void dlog_init()
{
  if (!s_session_ref)
  {
    s_session_ref = data_logging_create(LOG_TAG, DATA_LOGGING_BYTE_ARRAY, sizeof(DLogRecord), true);
  }
}

void dlog_log(Record r)
{
  DLogRecord output = {
    .id = r.id,
    .last_displayed = r.last_displayed
  };

  DataLoggingResult result = data_logging_log(s_session_ref, &output, 1);
  DEBUG("Send: %d", sizeof(DLogRecord));

  // Was the value successfully stored? If it failed, print the reason
  if (result != DATA_LOGGING_SUCCESS)
  {
    DEBUG("Error logging data: %d", (int)result);
  }
}

void dlog_deinit()
{
  if (s_session_ref)
  {
    data_logging_finish(s_session_ref);
    s_session_ref = NULL;
    DEBUG("Data logging completed");
  }
}
