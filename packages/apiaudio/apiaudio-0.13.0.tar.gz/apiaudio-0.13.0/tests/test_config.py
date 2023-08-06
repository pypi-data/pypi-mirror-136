import apiaudio
import pprint
import pytest
import os 

apiaudio.api_key = os.environ["AFLR_API_KEY"]
apiaudio.api_base="https://staging-v1.api.audio"
'''
def test_english_voices():
    print("List test:\nAll voices:")
    print(len(apiaudio.Voice.list().get("voices")))
    print("\nFiltered voices:")
    assert len(apiaudio.Voice.list(language="english").get("voices")) == 16

def test_spanish_voices():
    assert len(apiaudio.Voice.list(language="spanish").get("voices")) == 7

def test_list_parameters():
    assert len(apiaudio.Voice.list_parameters()) > 0 
'''
def test_sound_design():
    sounds = apiaudio.Sound.list()
    print(sounds)

def test_create_scripts():
    create_script= apiaudio.Script.create(scriptId="test", scriptText="<<sectionName::question>> Hey! Do you know we support multiple voices from different providers in the same script? I am a polly voice from Amazon. <<sectionName::answer>> I am Azure voice from Microsoft. I think Azure voices sound awesome.")
    get_script = apiaudio.Script.retrieve(scriptId="test")
    apiaudio.Speech.create(scriptId="test", voice="brandon")

def test_create_mastering():
    create_script= apiaudio.Script.create(scriptText="<<sectionName::question>> Hey! Do you know we support multiple voices from different providers in the same script? I am a polly voice from Amazon. <<sectionName::answer>> I am Azure voice from Microsoft. I think Azure voices sound awesome.")
    scriptId = create_script.get("scriptId")
    apiaudio.Speech.create(scriptId=scriptId, voice="brandon")
    mastering = apiaudio.Mastering.create(scriptId=scriptId)
    create_mastering = {'Message': 'Mastering request was successful'}
    assert len(mastering) > 0
    assert mastering == create_mastering

def test_birdcache():
    birdcache = apiaudio.Birdcache.create(
        type="mastering",
        voice="linda",
        text="This is {{username|me}} creating synchronous text to speech",
        audience={"username": ["salih", "sam", "timo"]},
        soundTemplate="openup",
    )
    assert len(birdcache) > 0
    assert birdcache[1]["text"] == "This is salih creating synchronous text to speech"

def test_warnings(capfd):
    mastering = apiaudio.Mastering.create(
        scriptId="test",
        forceLength=30000
    )
    out, err = capfd.readouterr()
    assert out == "Hello World!"

