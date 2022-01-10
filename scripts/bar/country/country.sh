#!/bin/sh

seconds=$1
updateFreq=$((seconds * 6))

updateCountry() 
{
    country=$(curl https://am.i.mullvad.net/country -s)
    counter=0
    printf "%s\n%s\n" "$country" "$counter" > /tmp/countryData
    printf "%s\n" "$country"
}

if [ -f /tmp/countryData ]; then
    data=/tmp/countryData
    lastResult=""
    counter=""
    { read -r lastResult; read -r counter; } < "$data"
    if [ "$counter" -ge "$updateFreq" ]; then
        updateCountry
    else
        counter=$((counter + 1))
        printf "%s\n%s\n" "$lastResult" "$counter" > /tmp/countryData
        printf "%s\n" "$lastResult"
    fi
else
    updateCountry
fi
