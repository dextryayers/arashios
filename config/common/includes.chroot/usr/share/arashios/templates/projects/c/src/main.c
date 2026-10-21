#include <stdio.h>

#include "@NAME@.h"

const char *@NAME@_version(void) {
    return "0.1.0";
}

int main(void) {
    printf("@NAME@ %s\n", @NAME@_version());
    return 0;
}
