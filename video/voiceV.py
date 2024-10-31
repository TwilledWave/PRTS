#retrieve the video resource to local
import re
def read_dict(file='./cache/data_char.txt'):
    dict = {};
    with open(file, 'r') as f:
        lines = f.readlines()
    for l in lines:
        s = l.split(',')
        s[1] = s[1].replace("\n", "")
        dict[s[0]]=s[1]
    return(dict)

def download_link(link):
    import urllib
    f = urllib.request.urlopen(link)  
    myfile = f.read()
    myfile = str(myfile).replace(" ","");
    images = re.findall('(?<=image=\")[\w_#$]+',str(myfile))
    chars = re.findall('(?<=\",name=\")[\w_#$]+',str(myfile))
    download_image(images, dict_image, image = True);
    download_image(chars, dict_char);
    return("download complete");

def download_image(list, dict, prefix = "", image = False):
    for l in list:
        l = l.replace("#","-")
        if not(l in dict):
            l = l.replace("-","_")
        if "bg_"+l in dict:
            l = "bg_"+l
        if l in dict:
            link = dict[l];
            path = "./cache"+link.replace("https://media.prts.wiki/","/images/")
            from pathlib import Path
            #check whether file exist
            my_file = Path(path)
            if not(my_file.is_file()):
                print(prefix+link);
                import requests
                #while to retry when download timeout
                tmp = True;
                while tmp:
                    try:
                        img_data = requests.get(prefix+link, timeout=30).content
                        tmp = False
                    except requests.exceptions.Timeout:
                        print("Timed out")
                #create directory and save the image
                import os
                Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
                with open(path, 'wb') as handler:
                    handler.write(img_data)
                if image == True:
                    from PIL import Image
                    size = (1024, 576)
                    #resize image
                    print(path)
                    im = Image.open(path)
                    im = im.resize(size, Image.Resampling.LANCZOS)
                    im.save(path, "PNG")

def image2video(link, duration, folder_image = "./cache/"):        
    import urllib
    f = urllib.request.urlopen(link)  
    myfile = f.read()
    myfile = str(myfile).replace(" ","");
    #get the non-background images, if zero, get the background
    images = re.findall('(?<=image\(image=\")[\w_#$]+',str(myfile))
    if len(images)==0:
        images = re.findall('(?<=image=\")[\w_#$]+',str(myfile))
        for i in range(len(images)):
            images[i] = "bg_"+images[i];
    clips = [];
    if len(images)==0:
        clips = [mpy.ColorClip(color = [0,0,0], size = (1024, 576)).set_duration(duration)]
    else:
        for i in images:
            if i in dict_image:
                img = folder_image + dict_image[i].replace("https://media.prts.wiki/","/images/");
                clip = mpy.ImageClip(img, duration = duration/len(images)).resize(width=1024, height=576)
                clips.append(clip)
    return(mpy.concatenate_videoclips(clips, method="chain"))

#read the character json and output the dictionary for translation
def json2dict(file = "voice.json", lang = "zh"):
    import json, time
    dict = {}
    # Opening JSON file
    with open(file, encoding="utf-8") as f:
        char_list = json.load(f)
    for l in char_list:
        nameEN = l["nameEN"];
        nameCN = l["nameCN"];
        nameJP = l["nameJP"];
        if lang =="zh":
            dict[nameCN]=l
        if lang == "en":
            dict[nameEN]=l
        if lang == "ja":
            dict[nameJP]=l            
    return(dict);

dict_char=read_dict('data_char.txt');
dict_image=read_dict('data_image.txt');
dict_voice=json2dict("voice.json", lang = "zh")
dict_voiceEN=json2dict("voice.json", lang = "en")
dict_voiceJA=json2dict("voice.json", lang = "ja")

import moviepy.editor as mpy
from moviepy.audio.AudioClip import AudioArrayClip
from pathlib import Path

def link2video(link:str, folder = "./cache/", folder_image = "./cache/", overwrite = False, stage = "1", lang = "zh", writeclip = True, lang_to = "en", translate = False, translate_using_llm = False):
    #download resource
    download_link(link);
    #download text
    import urllib, time
    f = urllib.request.urlopen(link)  
    html = f.readlines()
    #process
    background_image = ""; char_image = "";clips = [];
    for t in range(len(html)):
        line = html[t].decode("utf-8");
        if "image" in line:
            images = re.findall('(?<=image=\")[\w_#$]+',line)
            #if (len(images) > 0) and not('cgitem' in line):
            if (len(images) > 0):
                this_image = images[0];
                if "[Background(" in line:
                    this_image = "bg_"+this_image;
                else:
                    char_image = "";
                if this_image in dict_image:
                    background_image = folder_image + dict_image[this_image].replace("https://media.prts.wiki/","/images/");
        if "[charslot(" in line:
            line=line.replace(" ","");
            chars = re.findall('(?<=\",name=\")[\w_#$]+',line)
            if len(chars) > 0:
                chars[0] = chars[0].replace("#","-")
                if not(chars[0] in dict_char):
                    chars[0] = chars[0].replace("-","_")
                if chars[0] in dict_char:
                    char_image = folder_image + dict_char[chars[0]].replace("https://media.prts.wiki/","/images/");
                else:
                    char_image = "";
        name = ""; text = ""; voice_name = "default"
        if ("[name=" in line) and not("<" in line):
            names = re.findall('(?<=name=\")[^\"]+',line)
            texts = re.findall('(?<=\"\])[^\n]+',line)
            if len(names)>0 and len(texts)>0:
                name = names[0]; voice_name = name;                
                #remove the words in parenthesis
                text = re.sub("[\（\[].*?[\）\]]", "", texts[0])
                text = re.sub("[\(\[].*?[\)\]]", "", text)
        if ("text=" in line) and not("<" in line):            
            texts = re.findall('(?<=text=\")[^\"]+',line)
            if len(texts)>0:
                #remove the words in parenthesis
                text = re.sub("[\（\[].*?[\）\]]", "", texts[0])
                text = re.sub("[\(\[].*?[\)\]]", "", text)
        if not("[" in line) and not("<" in line) and not("}" in line):
            text = line[:-1];
            voice_name = "narrative"
        #remove unique character not recognized by TTS
        text = text.replace("—","");
        #check translation
        lang_voice = lang;
        prefix = str(t)
        path = folder+"/clip/"+stage+"/"+prefix+".mp4";
        if (translate == True) & (len(text)>0) & (not(Path(path).is_file())):
            print('TL:'+name+text)
            lang_voice = lang_to;
            #replace names in the text
            if lang_to == "en":
                text = multipleReplace(text = text, wordDict = dict_nameCN2EN)
                if name in dict_nameCN2EN:
                    name = dict_nameCN2EN[name];
                else:
                    name = ts.translate_text(name, translator="google",from_langugage=lang,to_language=lang_to)
            if lang_to == "ja":
                text = multipleReplace(text = text, wordDict = dict_nameCN2JP)
                if name in dict_nameCN2JP:
                    name = dict_nameCN2JP[name];
                else:
                    name = ts.translate_text(name, translator="google",from_langugage=lang,to_language=lang_to)
            voice_name = name
            for i in range(0,10):
                try:
                    if translate_using_llm:
                        text = translate_llm(text, lang = lang_to)
                    else:
                        text = ts.translate_text(text, translator="google",from_langugage=lang,to_language=lang_to)
                    #convert all capital words to words with the first letter capitalized.
                    text = capitalize_first_letter(text)
                except:
                    time.sleep(3);
                    continue
            text = text.replace("intersection","");
            text = text.replace("Intersection","");
            print('TLRES:'+name+text)
        #get the voice profile
        if lang_voice == "zh":
            this_dict = dict_voice;
        if lang_voice == "en":
            this_dict = dict_voiceEN;
        if lang_voice == "ja":
            this_dict = dict_voiceJA;            
        if not(name in this_dict):
            voice_name = "default"
            if ("冷漠" in name) or ("饥饿" in name):
                voice_name = "冷漠" 
            if ("残忍" in name) or ("愤" in name) or ("困倦" in name) or ("Rude" in name):
                voice_name = "残忍"
            if ("童" in name) or ("young" in name.lower()) or ("child" in name.lower()):
                voice_name = "defaultChild"                
            if ("女" in name) or ("太太" in name) or ("lady" in name.lower()) or ("girl" in name.lower()) or ("woman" in name.lower()) or ("female" in name.lower()):
                voice_name = "defaultF"
        ref = this_dict[voice_name]["voice"];
        prompt_language = this_dict[voice_name]["lang"];
        prompt_text = this_dict[voice_name]["text"];
        #generate clip if text not empty
        prefix = str(t)
        path = folder+"/clip/"+stage+"/"+prefix+".mp4";
        text = text.replace("-","")
        tmp = text.replace(".","")
        if ((len(tmp) > 3) and (not(Path(path).is_file())) or (overwrite == True)):
            print(prefix+name+str(len(text))+text);
            print(ref+prompt_language+prompt_text+background_image+char_image);
            try:
                clips.append(text2video(text, lang = lang_voice, img = background_image, char = char_image, char_name = name, overwrite = overwrite,
                            ref=ref, prompt_language=prompt_language, prompt_text=prompt_text, prefix = prefix, stage = stage, writeclip = writeclip,
                            folder = folder))
            except Exception as e:
                print(str(e))
        else: 
            if Path(path).is_file():
                clips.append(mpy.VideoFileClip(path))
    concat_clip = mpy.concatenate_videoclips(clips, method="chain")
    concat_clip.write_videofile(folder+"/"+stage+".mp4", verbose=False, logger=None);
    concat_clip.close();
    return("video run success for "+link);

def text2video(text:str, stage, ref = "", prompt_language = "", prompt_text = "", overwrite = False, writeclip = True,
               img = "", char = "", char_name = "", lang:str = "zh", title = "      ", folder = "./cache/", prefix = "1"):
    #make audio
    path = Path(folder+"audio/"+stage+"/"+prefix+".wav");
    if (not(path.is_file()) or (overwrite == True)):
        if ref == "":
            o4 = text2audio(text, lang = lang, audio = folder+"audio/"+stage+"/"+prefix+".wav");
        else:
            o4 = text2audio(text, lang = lang, audio = folder+"audio/"+stage+"/"+prefix+".wav", ref=ref, prompt_language=prompt_language, prompt_text=prompt_text);
    audio = mpy.AudioFileClip(folder+"audio/"+stage+"/"+prefix+".wav")
    #make text
    text = char_name +":      "+text
    if lang == "zh":
        font = "Microsoft-YaHei-&-Microsoft-YaHei-UI"
    elif (lang == "jp") or (lang == "ja"):
        font = "wqy-microhei.ttc"
    else:
        font = "Microsoft-YaHei-&-Microsoft-YaHei-UI"
    txt_clip  = mpy.TextClip(text, fontsize = 15, color = "white", font = font)
    title_clip  = mpy.TextClip(title, fontsize = 20, color = "white", font = font)
    txt_clip = txt_clip.margin(bottom=100, opacity=0).set_pos('bottom').set_duration(audio.duration)
    title_clip = title_clip.set_pos('center').set_duration(audio.duration)
    #make video
    if img != "":
        clip = mpy.ImageClip(img, duration = audio.duration).resize(width=1024, height=576)
    else:
        clip = mpy.ColorClip(color = [0,0,0], size = (1024, 576)).set_duration(audio.duration)
    if char!="":
        char_clip = mpy.ImageClip(char, duration = audio.duration).resize(0.7).set_pos(("left","top"))
        clip = mpy.CompositeVideoClip([clip, char_clip])
    #clip = clip.set_duration(audio.duration)
    clip.audio = audio
    clip  = mpy.CompositeVideoClip([clip, txt_clip, title_clip])
    clip.fps = 12
    fade_in = 0.05
    clip.audio_fadein(fade_in).audio_fadeout(fade_in)
    if writeclip == True:
        clip.write_videofile(folder+"/clip/"+stage+"/"+prefix+".mp4", verbose=False, logger=None);
    return(clip, txt_clip, title_clip)



def text2audio(text:str, lang:str = "zh", audio = "./cache/audio/1.wav", 
               ref = "sample/Liskarm.wav",
               prompt_language = "en",
               prompt_text = "Take all missions seriously: that's the guiding rule for us security professionals."):
    #tts via api
    import requests
    HOST = 'localhost:9880'
    URI = f'http://{HOST}'
    response = requests.post(
        URI,
        json={
        "refer_wav_path": ref,
        "prompt_text": prompt_text,
        "prompt_language": prompt_language,
        "text": text,
        "text_language": lang
        },
    )
    with open(audio, "wb") as f:
        f.write(response.content)
    return()

def text2audio2(text:str, lang:str = "zh", audio = "./cache/audio/1.wav", 
               ref = "sample/Liskarm.wav",
               prompt_language = "en",
               prompt_text = "Take all missions seriously: that's the guiding rule for us security professionals."):
    #tts via api
    import requests
    HOST = 'localhost:9880'
    URI = f'http://{HOST}'
    cut = "cut5";
    response = requests.post(
        URI,
        json={
        "text_split_method": cut,               
        "ref_audio_path": ref,
        "prompt_text": prompt_text,
        "prompt_lang": prompt_language,
        "text": text,
        "text_lang": lang
        },
    )
    with open(audio, "wb") as f:
        f.write(response.content)
    return()

#translate the prts from cn 
#read the character json and output the dictionary for translation
def json2dict(file = "chars.json", lang_to = "en"):
    import json, time
    dict = {}
    # Opening JSON file
    with open(file, encoding="utf-8") as f:
        char_list = json.load(f)
    for l in char_list:
        nameEN = l["nameEN"];
        nameCN = l["nameCN"];
        nameJP = l["nameJP"];
        #don't replace name with only 1 character
        if lang_to == "en":
            if (nameCN != None) & (nameEN != None):
                if len(nameCN)>1:
                    dict[nameCN]=nameEN
        if lang_to == "ja":                    
            if (nameCN != None) & (nameJP != None):
                if len(nameCN)>1:
                    dict[nameCN]=nameJP
    dict["narrative"] = "narrative";
    return(dict);

#replace every instance in the source by dict
def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text

# Function to convert all capital words to words with the first letter capitalized.
def capitalize_first_letter(text):
    text = text.replace("'s","")
    text = text.replace("'","")
    words = text.split()
    processed_words = []
    for word in words:
        if word.isupper():
            word = word.capitalize()
        processed_words.append(word)
    return ' '.join(processed_words)

#redefine the translate function using llm
def translate_llm(text, lang = "en"):
    if lang == "en":
        lang = "English"
    prompt = "translate the following text to " + lang +" , output translation results only \n "+ text +" \n Translation: ";
    text = llm._call(prompt = prompt)
    truncated_text = text.split('\n', 1)[0]
    return truncated_text

from typing import Any, List, Mapping, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests

class CustomLLM2(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if isinstance(stop, list):
            stop = stop + ["\n###","\nObservation:","\n问题","\nQuestion:"]
        HOST = 'localhost:5000'
        URI = f'http://{HOST}/v1/chat/completions'

        response = requests.post(
            URI,
            json={
                "messages": [
                {
                    "role": "user",
                    "content": prompt
                  }
                ],
                "mode": "instruct",
                "instruction_template": "Alpaca",
            },
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
  
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {}

import translators as ts
llm = CustomLLM2(temperature=0.5)
dict_nameCN2EN=json2dict('../db/chars.json', lang_to = "en");
dict_nameCN2JP=json2dict('../db/chars.json', lang_to = "ja");
