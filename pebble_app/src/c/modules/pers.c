#include "pers.h"

uint8_t pers_read_max_records()
{
  uint8_t buf = 0;
  persist_read_data(MAX_RECORDS_KEY, &buf, sizeof(uint8_t));
  return buf;
}

void pers_write_max_records(uint8_t max)
{
  persist_write_data(MAX_RECORDS_KEY, &max, sizeof(uint8_t));
}

void pers_read_single(uint8_t num, Record* buf)
{
  persist_read_data(num + RECORDS_OFFSET, buf, sizeof(Record));
}

void pers_read_all(Record *buf)
{
  uint8_t max = pers_read_max_records();
  for (int i = 0; i < max; i++)
  {
    pers_read_single(i, &buf[i]);
  }
}

void pers_write(Record record, uint num)
{
  persist_write_data(num + RECORDS_OFFSET, &record, sizeof(Record));
}

void pers_sweep()
{
  for (int i = 0; i < 256; i++)
  {
    persist_delete(i);
  }
}
