#include "util.h"

void record_to_string(char buf[MAX_TEXT_LEN], Record r)
{
    char time_buf[MAX_TEXT_LEN];
    time_to_string(time_buf, r.last_displayed);
    snprintf(buf, MAX_TEXT_LEN, "Record (%d;'%s';%s)", r.id, r.text, time_buf);
}

void time_to_string(char buf[MAX_TEXT_LEN], time_t rawtime)
{
   struct tm *info;

   time( &rawtime );

   info = localtime( &rawtime );

   strftime(buf,MAX_TEXT_LEN,"%x - %I:%M%p", info);
}

uint8_t packet_get_uint8(DictionaryIterator *inbox_iter, int key)
{
    if (!packet_contains_key(inbox_iter, key))
    {
        return 0;
    }
    return dict_find(inbox_iter, key)->value->uint8;
}