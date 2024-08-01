# requirements:
# FX file explorer (https://wiki.termux.com/wiki/Internal_and_external_storage)
# F-Droid
# Termux
# Termux:API
# Termux:Boot
# Termux:tasker
# install termux, termux-api, termux-tasker form F-Droid, form inside Termux run `pkg install termux-api`

# Termux requirements
# run termux-setup-storage to allow access to storage folders

# required termux pakages:
# rust `pkg install rust`
# python `pkg install python`

# python requirements: numpy, pandas (link:)[https://github.com/termux/termux-packages/discussions/19126]
# when errors occurs in installing python packages usually `export MATHLIB=m` fixes the issue
# pip install ai71 openai langchain

# connect phone screen to mac
# Stay Awake: scrcpy --stay-awake
# Stay Awake + Screen Off: scrcpy -w -S

import os
from datetime import datetime
import subprocess
import time
import warnings

#  android termux functions mapping
dir_home = "/data/data/com.termux/files/home"
dir_project = "visionAId"
dir_downloads = "~/storage/downloads"
dir_pictures = "~/storage/pictures"
dir_dcim = "~/storage/dcim"
dir_music = "~/storage/music"
dir_movies = "~/storage/movies"
# dir_external_1 = "~/storage/external-1"

def take_photo(**kwargs): # camera_id = 0 or 1 (0 back camera, 1 front camera)
    camera_id = kwargs.get("camera_id", 0)
    filename = f"photo_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg"
    _path = os.path.join('~/storage/dcim/', filename)
    cmd = f"termux-camera-photo -c {camera_id} {_path}"
    subprocess.call(cmd, shell=True)

def get_location():
    cmd = "termux-location -p passive -r once"
    subprocess.call(cmd, shell=True)

def start_recording():
    cmd = "termux-microphone-record -f ~/storage/dcim/audio.mp3 -l 30"
    subprocess.call(cmd, shell=True)

def stop_recording():
    cmd = "termux-microphone-record -q"
    subprocess.call(cmd, shell=True)

def block_user_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)

def enable_user_warnings():
    warnings.filterwarnings("default", category=UserWarning)

def find_best_match(input_string, string_dict, threshold=75):
    best_match_key = None
    highest_similarity = 0

    for key, value in string_dict.items():
        block_user_warnings()
        from fuzzywuzzy import fuzz
        similarity = fuzz.ratio(str(input_string), str(value))
        if similarity > highest_similarity and similarity >= threshold:
            highest_similarity = similarity
            best_match_key = key

    # msg = f"debug: best_match_key: {str(best_match_key)}, highest_similarity: {str(highest_similarity)}"
    # os.system("termux-tts-speak {}".format(msg))
    return str(best_match_key)

commands_dict = {
        'front': "What's in front of me",
        'around': "What's around me",
        'where': "Where am I",
        'help': "Help me go _____",
        'warn': "warn me",
}

def speech_routine():
    txt = "Listening..."
    os.system("termux-tts-speak {}".format(txt))

    inp = ''
    while inp == '':
        inp = subprocess.getoutput("termux-speech-to-text")
        time.sleep(1)
        if inp == '':
            txt = "Sorry, I could not understand the audio. please try again."
            os.system("termux-tts-speak {}".format(txt))

    text_you_want_in_speech = "You said: "+str(inp)
    print(text_you_want_in_speech)
    os.system("termux-tts-speak {}".format(text_you_want_in_speech))

    match find_best_match(inp, commands_dict):
        case 'front':
            msg = 'taking front a photo'
        case 'around':
            msg = 'taking 360 photo'
        case 'where':
            msg = 'getting current location'
        case 'help':
            msg = 'setting up navigation'
        case 'warn':
            msg = 'setting up warning system'
        case _ :
            msg = 'Sorry, I could not understand the audio. please try again.'

    os.system("termux-tts-speak {}".format(msg))