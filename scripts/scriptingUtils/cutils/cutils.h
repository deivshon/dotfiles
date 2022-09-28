#include <string.h>

#ifndef CUTILS
#define CUTILS

#define MAX_PATH_LENGTH 4096
#define NET_INTERFACES_PATH "/sys/class/net"

#define strip(str) str[strcspn(str, "\n")] = '\0';
#define streq(str1, str2) !strcmp(str1, str2)
#define starts_with(str, prefix) !strncmp(str, prefix, strlen(prefix))

#endif
