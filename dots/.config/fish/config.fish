#!/bin/fish

set -U fish_greeting

set FISH_ALIASES_FILE "$HOME/.config/aliases/fish_aliases.fish"
if test -f "$FISH_ALIASES_FILE"
    source "$FISH_ALIASES_FILE"
else
    printf "Error: aliases file not found at $FISH_ALIASES_FILE\n" 1>&2
end
set -e FISH_ALIASES_FILE

function ssh-start
    eval (ssh-agent -c)

    for KEY in ~/.ssh/*
        if test -f "$KEY"
            set FILE_RESULT (file -b "$KEY")
            if string match -q "private key" "$FILE_RESULT"
                ssh-add "$KEY"
            end
        end
    end
end

if test "$TERM" = "foot"
    alias ssh "TERM=linux ssh"
    alias vagrant "TERM=linux vagrant"
end

function set_theme
    set -U fish_color_normal normal
    set -U fish_color_command green
    set -U fish_color_quote yellow
    set -U fish_color_redirection cyan --bold
    set -U fish_color_end green
    set -U fish_color_error brred
    set -U fish_color_param normal
    set -U fish_color_comment red
    set -U fish_color_match --background=brblue
    set -U fish_color_selection white --bold --background=brblack
    set -U fish_color_search_match bryellow --background=brblack
    set -U fish_color_history_current --bold
    set -U fish_color_operator brcyan
    set -U fish_color_escape brcyan
    set -U fish_color_cwd green
    set -U fish_color_cwd_root red
    set -U fish_color_valid_path --underline
    set -U fish_color_autosuggestion 555
    set -U fish_color_user brgreen
    set -U fish_color_host normal
    set -U fish_color_cancel --reverse
    set -U fish_pager_color_prefix normal --bold --underline
    set -U fish_pager_color_progress brwhite --background=blue
    set -U fish_pager_color_completion normal
    set -U fish_pager_color_description B3A06D --italics
    set -U fish_pager_color_selected_background --reverse
    set -U fish_pager_color_selected_prefix
    set -U fish_pager_color_background
    set -U fish_color_host_remote
    set -U fish_color_keyword
    set -U fish_pager_color_secondary_completion
    set -U fish_pager_color_selected_completion
    set -U fish_color_option
    set -U fish_pager_color_secondary_prefix
    set -U fish_pager_color_selected_description
    set -U fish_pager_color_secondary_background
    set -U fish_pager_color_secondary_description
end

set_theme

set -U fish_color_cwd_root white
set -U fish_color_cwd white
set -U fish_user $(whoami)
set -U fish_hostname $(hostname)

function fish_prompt
    set -l last_pipestatus $pipestatus
    set -lx __fish_last_status $status

    set -l status_color (set_color red)
    set -l statusb_color (set_color red)
    set -l prompt_status (__fish_print_pipestatus "" ">" "/" "$status_color" "$statusb_color" $last_pipestatus)" "

    set -f prompt_cwd (pwd)
    if [ "$prompt_cwd" = $HOME ]
        set -f prompt_cwd "~"
    else
        set -f prompt_cwd (basename (realpath .))
    end

    if test -z "$prompt_status"
        echo -n -s (set_color green) ["$fish_user@$fish_hostname " (set_color $fish_color_cwd) "$prompt_cwd" (set_color yellow) (fish_vcs_prompt) (set_color green)] (set_color green)"> "
    else
        echo -n -s (set_color green) ["$fish_user@$fish_hostname " (set_color $fish_color_cwd) "$prompt_cwd" (set_color yellow) (fish_vcs_prompt) (set_color green)] " $prompt_status"
    end
end

function fish_command_not_found
    return
end

afetch
