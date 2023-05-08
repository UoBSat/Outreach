#ifndef _COMMANDS_H
#define _COMMANDS_H

#define COMMAND_BYTE_COUNT 1
#define COMMAND_SERVER_PORT 8080

// Byte 0
#define X_POSITIVE      0b00000001
#define X_NEGATIVE      0b00000010
#define Y_POSITIVE      0b00000100
#define Y_NEGATIVE      0b00001000
#define SHUTDOWN        0b10000000
#endif
