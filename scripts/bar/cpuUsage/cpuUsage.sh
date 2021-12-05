#!/usr/bin/perl
#
# Copyright 2014 Pierre Mavro <deimos@deimos.fr>
# Copyright 2014 Vivien Didelot <vivien@didelot.org>
# Copyright 2014 Andreas Guldstrand <andreas.guldstrand@gmail.com>
#
# Licensed under the terms of the GNU GPL v3, or any later version
#

#
# Part of the original script at https://github.com/vivien/i3blocks-contrib/blob/master/cpu_usage/cpu_usage
#

# Get CPU usage
$ENV{LC_ALL}="en_US"; # if mpstat is not run under en_US locale, things may break, so make sure it is
open (MPSTAT, 'mpstat 1 1 |') or die;
while (<MPSTAT>) {
    if (/^Average.*\s+(\d+\.\d+)/) {
        $cpu_usage = 100 - $1; # 100% - %idle
        last;
    }
}
close(MPSTAT);

printf "%.2f%%\n", $cpu_usage
