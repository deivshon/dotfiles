UTILS_PATH = ../scriptingUtils/cutils

.SECONDARY: $(UTILS_PATH)/cutils.o eth/eth.o diskUsage/diskUsage.o

all: eth/eth.out diskUsage/diskUsage.out

%.out: %.o $(UTILS_PATH)/cutils.o
	gcc -o $@ $^

%.o: %.c $(UTILS_PATH)/cutils.c $(UTILS_PATH)/cutils.h
	gcc -c -o $@ $<

clean:
	rm -f */*.o */*.out $(UTILS_PATH)/*.o
