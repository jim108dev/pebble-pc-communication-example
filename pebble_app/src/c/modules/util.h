#include "types.h"
#include <@smallstoneapps/utils/macros.h>
#include <pebble-packet/pebble-packet.h>

void debug_record(char prefix[], Record r);
uint8_t packet_get_uint8(DictionaryIterator *inbox_iter, int key);
void time_to_string(char buf[MAX_TEXT_LEN], time_t rawtime);