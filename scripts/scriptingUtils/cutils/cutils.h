#include <string.h>

#ifndef CUTILS
#define CUTILS

#define MAX_PATH_LENGTH 4096
#define NET_INTERFACES_PATH "/sys/class/net"

#define SEPARATOR "|"

#define strip(str) str[strcspn(str, "\n")] = '\0';
#define streq(str1, str2) !strcmp(str1, str2)
#define starts_with(str, prefix) !strncmp(str, prefix, strlen(prefix))

void get_separator(char **dest, int argc, char **argv);
void get_cmd_output(char *dest, int dest_size, char *cmd, char **cmd_args);
int to_formatted_bytes(char *dest, double bytes);

#endif
