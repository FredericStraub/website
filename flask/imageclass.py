from transformers import BeitFeatureExtractor, BeitForImageClassification
from PIL import Image
import requests
import os
import wave
audio ="m.wav"
image = "spectrogram.jpg"
import pylab
import numpy as np
#needed to include this other wise i had problems with pylab for some reason we have to see if i have to change smth in the environvariables where we will run the code
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
   
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.jpg')

def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate

def predict(file):
    file_name=os.path.split(file)[-1]

    if file_name[-3:] != "wav":
        image = Image.open(file)
        feature_extractor = BeitFeatureExtractor.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        model = BeitForImageClassification.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        # model predicts one of the 21,841 ImageNet-22k classes
        predicted_class_idx = logits.argmax(-1).item()
        result = model.config.id2label[predicted_class_idx].split(",")[0]
        #print("Predicted class:", result)
        return result
    else:
        graph_spectrogram(file)
        image = Image.open("spectrogram.jpg")
        feature_extractor = BeitFeatureExtractor.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        model = BeitForImageClassification.from_pretrained('microsoft/beit-base-patch16-224-pt22k-ft22k')
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        # model predicts one of the 21,841 ImageNet-22k classes
        predicted_class_idx = logits.argmax(-1).item()
        # since i saved the spectrogram file in the same dir i am deleting it here prob have do edit this depending where and how we run the code 
        # os.remove("spectrogram.jpg")
        result = model.config.id2label[predicted_class_idx].split(",")[0]
        #print("Predicted class:", result)
        return result

predict(audio)