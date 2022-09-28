#include "cutils.h"
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

void get_cmd_output(char *dest, int dest_size, char *cmd, char **cmd_args) {
    int piped[2];
    if(pipe(piped) == -1) {
        exit(EXIT_FAILURE);
    }

    if(fork() == 0) {
        close(piped[0]);    // close read end of child
        dup2(piped[1], 1);  // stdout to pipe
        dup2(piped[1], 2);  // stderr to pipe
        close(piped[1]);    // close write end of child: no longer needed

        execvp(cmd, cmd_args);
    }
    else {
        strcpy(dest, "");

        int c = 0; // Bytes read into buffer each time
        char buf[1024] = "";
        close(piped[1]);    // close write end of parent

        while((c = read(piped[0], buf, sizeof(buf) - 1))) {
            // Sets the byte after the last one read to '\0', terminating the string
            buf[c] = '\0';

            if(strlen(dest) + strlen(buf) >= (size_t) dest_size)
                break;

            strcat(dest, buf);
        }
        close(piped[0]);    // close read end of parent: no longer needed
    }
}

void get_separator(char **dest, int argc, char **argv) {
        for(int i = 0; i < argc; i++) {
        if(streq("--separator", argv[i])) {
            (*dest) = SEPARATOR;
        }
    }
}

int to_formatted_bytes(char *dest, double bytes) {
    char *suffixes[7] = {"B", "K", "M", "G", "T", "P", "E"};

    double approx_bytes = bytes;
    unsigned int divisions = 0;

    while(approx_bytes > 1e3 && divisions <= 7) {
        approx_bytes /= 1024;
        divisions++;
    }

    if(divisions == 0)
        sprintf(dest, "%.0lf%s", approx_bytes, suffixes[divisions]);
    else
        sprintf(dest, "%.2lf%s", approx_bytes, suffixes[divisions]);

    return 1;
}
