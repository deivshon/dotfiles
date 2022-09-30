UTILS_PATH = ../scriptingUtils/cutils

CFLAGS = -O2 -Wall -Wextra

ifeq ($(dbg), true)
.SECONDARY: $(UTILS_PATH)/cutils.o eth/eth.o diskUsage/diskUsage.o RAMusage/RAMusage.o cpuUsage/cpuUsage.o mullvadCheck/mullvadCheck.o battery/battery.o
endif

all: eth/eth.out diskUsage/diskUsage.out RAMusage/RAMusage.out cpuUsage/cpuUsage.out mullvadCheck/mullvadCheck.out battery/battery.out

%.out: %.o $(UTILS_PATH)/cutils.o
	gcc $(CFLAGS) -o $@ $^

%.o: %.c $(UTILS_PATH)/cutils.c $(UTILS_PATH)/cutils.h
	gcc $(CFLAGS) -c -o $@ $<

clean:
	rm -f */*.o */*.out $(UTILS_PATH)/*.o
