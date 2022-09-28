UTILS_PATH = ../scriptingUtils/cutils

CFLAGS = -O2 -Wall -Wextra

.SECONDARY: $(UTILS_PATH)/cutils.o eth/eth.o diskUsage/diskUsage.o RAMusage/RAMusage.o

all: eth/eth.out diskUsage/diskUsage.out RAMusage/RAMusage.out

%.out: %.o $(UTILS_PATH)/cutils.o
	gcc -o $@ $^

%.o: %.c $(UTILS_PATH)/cutils.c $(UTILS_PATH)/cutils.h
	gcc $(CFLAGS) -c -o $@ $<

clean:
	rm -f */*.o */*.out $(UTILS_PATH)/*.o
