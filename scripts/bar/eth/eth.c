#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <stdlib.h>
#include "../../scriptingUtils/cutils/cutils.h"

int operstate_up(char *path) {
    char operstate_path[MAX_PATH_LENGTH];
    sprintf(operstate_path, "%s/%s", path, "operstate");

    FILE *fs = fopen(operstate_path, "r");
    if(fs == NULL) return 0;

    char content[16];
    fgets(content, 16, fs);

    fclose(fs);

    strip(content);

    return streq("up", content);
}

int main(int argc, char **argv) {
    char *sep = "";
    int isUp = 0;
    
    get_separator(&sep, argc, argv);

    struct dirent *d;
    DIR *interfaces;
    if((interfaces = opendir(NET_INTERFACES_PATH)) == NULL) {
        exit(EXIT_FAILURE);
    }

    while((d = readdir(interfaces)) != NULL) {
        if(starts_with(d->d_name, "eth") || starts_with(d->d_name, "enp")) {
            char current_interface_path[MAX_PATH_LENGTH];
            sprintf(current_interface_path, "%s/%s", NET_INTERFACES_PATH, d->d_name);
            isUp = operstate_up(current_interface_path);
            break;
        }
    }

    if(!isUp) exit(EXIT_SUCCESS);
    
    char res[16] = "ETH: UP";
    strcat(res, sep);
    printf("%s\n", res);
}
