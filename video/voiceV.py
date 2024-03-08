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
    download_image(images, dict_image);
    download_image(chars, dict_char);
    return("download complete");

def download_image(list, dict, prefix = "https://prts.wiki"):
    for l in list:
        if "bg_"+l in dict:
            l = "bg_"+l
        if l in dict:
            link = dict[l];
            path = "./cache"+link
            from pathlib import Path
            #check whether file exist
            my_file = Path(path)
            if not(my_file.is_file()):
                print(prefix+link);
                import requests
                img_data = requests.get(prefix+link).content
                #create directory and save the image
                import os
                Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
                with open(path, 'wb') as handler:
                    handler.write(img_data)            

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

def link2video(link:str, folder = "./cache/", folder_image = "./cache/", overwrite = False, stage = "1", lang = "zh", writeclip = True, lang_to = "en", translate = False):
    #download resource
    download_link(link);
    #download text
    import urllib
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
                    background_image = folder_image + dict_image[this_image];
        if "[charslot(" in line:
            line=line.replace(" ","");
            chars = re.findall('(?<=\",name=\")[\w_#$]+',line)
            if len(chars) > 0:
                if chars[0] in dict_char:
                    char_image = folder_image + dict_char[chars[0]];
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
        if (translate == True) & (len(text)>0):
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
            text = ts.translate_text(text, translator="google",from_langugage=lang,to_language=lang_to)
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
            if ("残忍" in name) or ("愤" in name) or ("困倦" in name):
                voice_name = "残忍"                 
            if ("女" in name) or ("太太" in name) or ("lady" in name) or ("girl" in name) or ("woman" in name) or ("female" in name):
                voice_name = "defaultF"
        ref = this_dict[voice_name]["voice"];
        prompt_language = this_dict[voice_name]["lang"];
        prompt_text = this_dict[voice_name]["text"];
        #generate clip if text not empty
        prefix = str(t)
        path = folder+"/clip/"+stage+"/"+prefix+".mp4";
        tmp = text.replace(".","")
        if (len(tmp) > 3) and (not(Path(path).is_file()) or (overwrite == True)):
            print(name+str(len(text))+text+ref+prompt_language+prompt_text+background_image+char_image);
            clips.append(text2video(text, lang = lang_voice, img = background_image, char = char_image, char_name = name, overwrite = overwrite,
                       ref=ref, prompt_language=prompt_language, prompt_text=prompt_text, prefix = prefix, stage = stage, writeclip = writeclip, folder = folder))
        else: 
            if Path(path).is_file():
                clips.append(mpy.VideoFileClip(path))
    concat_clip = mpy.concatenate_videoclips(clips, method="chain")
    concat_clip.write_videofile(folder+"/"+stage+".mp4", verbose=False, logger=None);
    concat_clip.close();
    return("video run success for "+link);

def text2video(text:str, ref, prompt_language, prompt_text, stage, overwrite, writeclip = True,
               img = "", char = "", char_name = "", lang:str = "zh", title = "      ", folder = "./cache/", prefix = "1"):
    #make audio
    path = Path(folder+"audio/"+stage+"/"+prefix+".wav");
    if (not(path.is_file()) or (overwrite == True)):
        o4 = text2audio(text, lang = lang, audio = folder+"audio/"+stage+"/"+prefix+".wav", ref=ref, prompt_language=prompt_language, prompt_text=prompt_text);
    audio = mpy.AudioFileClip(folder+"audio/"+stage+"/"+prefix+".wav")
    #make text
    text = char_name +":      "+text
    if lang == "zh":
        txt_clip  = mpy.TextClip(text, fontsize = 15, color = "white", font = "Microsoft-YaHei-&-Microsoft-YaHei-UI")
    elif (lang == "jp") or (lang == "ja"):
        txt_clip  = mpy.TextClip(text, fontsize = 15, color = "white", font = "wqy-microhei.ttc")
    else:
        txt_clip  = mpy.TextClip(text, fontsize = 15, color = "white")
    txt_clip = txt_clip.margin(bottom=100, opacity=0).set_pos('bottom').set_duration(audio.duration)
    title_clip  = mpy.TextClip(title, fontsize = 40, color = "black")
    title_clip = title_clip.set_pos('top').set_duration(audio.duration)
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
    return(clip)

def text2audio(text:str, lang:str = "zh", audio = "./cache/audio/1.wav", 
               ref = "sample/nearl.wav",
               prompt_language = "en",
               prompt_text = "I'm gladdened to be by your side once again, Doctor... Yes, may the light be with you as always."):
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
    dict["明日方舟"] = "Arknights";
    dict["narrative"] = "narrative";
    return(dict);

#replace every instance in the source by dict
def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text

import translators as ts
dict_nameCN2EN=json2dict('../db/chars.json', lang_to = "en");
dict_nameCN2JP=json2dict('../db/chars.json', lang_to = "ja");
