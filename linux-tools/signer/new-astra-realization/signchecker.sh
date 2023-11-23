#!/bin/bash

trap "rm -rf $tmp; exit" INT

BSIGN="bsign"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'


FILE_STACK=$()

function is_elf_unsigned() {
    "$BSIGN" -E -w "$1" | grep "good hash found" > /dev/null
    return $?
}

function process_dir() {
    find -P "$1" -mindepth 1 -maxdepth 1 -print0 | while IFS= read -r -d $'\0' file; do
        process "$file" "$2"
    done
}

function process_tar() {
    tmp="$(mktemp -d)"
    stack_push "$1" "$2"

    # TODO: remove "2> /dev/null", fix tar detection instead
    tar xf "$1" -C "$tmp" 2> /dev/null
    process_dir "$tmp" "$tmp"

    rm -rf "$tmp"
    stack_pop
}

function process_jar() {
    tmp="$(mktemp -d)"
    stack_push "$1" "$2"

    jarfile=`realpath "$1"`
    pushd "$tmp" &>/dev/null
    jar xf "$jarfile" &>/dev/null
    JAR_EXIT_CODE=$?
    popd &>/dev/null
    if [[ $JAR_EXIT_CODE -eq 0 ]]; then
        process_dir "$tmp" "$tmp"
    else
        print_stack 1
    fi

    rm -rf "$tmp"
    stack_pop
}

function process_deb() {
    tmp="$(mktemp -d)"
    stack_push "$1" "$2"

    dpkg -x "$1" "$tmp"
    process_dir "$tmp" "$tmp"

    rm -rf "$tmp"
    stack_pop
}

# whl packages are actually zip
function process_zip() {
    tmp="$(mktemp -d)"
    stack_push "$1" "$2"

    unzip -q "$1" -d "$tmp"
    process_dir "$tmp" "$tmp"

    rm -rf "$tmp"
    stack_pop
}

function process() {
    filetype=`file -b --mime-type "$1" | cut -d/ -f2-`
    filename=`basename -- "$1"`
    extension="${filename##*.}"

    # Sometimes we have jar files which are actually are shell scripts with appended binary data (e.g. Zipkin), so we can detect jar file only by extension
    if [[ ! -d "$1" && "$extension" = "jar" ]]; then
        process_jar "$1" "$2"
    else
        case "$filetype" in
            "directory")
                process_dir "$1" "$2"
                ;;
            "gzip" | "x-tar" | "x-bzip" | "x-bzip2")
                process_tar "$1" "$2"
                ;;
            "vnd.debian.binary-package")
                process_deb "$1" "$2"
                ;;
            "zip")
                process_zip "$1" "$2"
                ;;
            "x-pie-executable" | "x-executable" | "x-sharedlib")
                is_elf_unsigned "$1"
                is_unsigned="$?"

                stack_push "$1" "$2"
                print_stack "$is_unsigned"
                stack_pop
                ;;
            *) # Find non-ELF .so files as default option
              if [[ "$extension" = "so" ]]; then
                stack_push "$1" "$2"
                is_unsigned="99"
                print_stack "$is_unsigned"
                stack_pop
              fi
            ;;
        esac

    fi
}


function print_stack() {
    echo -n "${FILE_STACK[1]}"
    for entry in "${FILE_STACK[@]:2}"; do
        echo -ne " $YELLOW->$RESET $entry"
    done
    

    if [ "$1" == 0 ]; then
        echo -e ":$GREEN Signed$RESET"
    elif [ "$1" == 99 ]; then
        echo -e ":$YELLOW Not ELF$RESET"
    else
        echo -e ":$RED Not signed$RESET"
    fi
}

function stack_push() {
    FILE_STACK+=("${1#$2}")
}

function stack_pop() {
    unset FILE_STACK[-1]
}

process "$1" ""
