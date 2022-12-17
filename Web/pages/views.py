from calendar import month_name
from unicodedata import name
from django.shortcuts import render
from matplotlib.style import context
import pyrebase
# Create your views here.
config = {
"apiKey": "AIzaSyAkl_ehqDiG5fSHW-XzMPp8ocoYmLMgDOQ",
"authDomain": "pbl5-camera-327b0.firebaseapp.com",
"databaseURL": "https://pbl5-camera-327b0-default-rtdb.asia-southeast1.firebasedatabase.app/",
"projectId": "pbl5-camera-327b0",
"storageBucket": "pbl5-camera-327b0.appspot.com",
"serviceAccount": "pbl5-camera-327b0-firebase-adminsdk-m00dj-7a33340ba9.json"
}

firebase_storage = pyrebase.initialize_app(config)
storage = firebase_storage.storage()
auth = firebase_storage.auth()
#lay user
email="tranthithanhnga913@gmail.com"
password = "01202313908@Nga"
user = auth.sign_in_with_email_and_password(email,password)

monthnames = dict()
#-------------------------------------------------------------------------------
# Uploading And Downloading Images

# storage.child("Guitar.JPG").put("Guitar.JPG")
# storage.child("PlayingGuitar.JPG").download("PlayingGuitar.JPG")

def get_all_img(request):
    monthnames.clear()
    all_files = storage.list_files()
    for file in all_files:
        str_name = file.name.split("_")[2]
        str_month = file.name.split("_")[0].split("-")[1]
        if monthnames.get("Month "+str_month+" "+str_name+" :") is None:
            monthnames["Month "+str_month+" "+str_name+" :"] = 1
        else:
            monthnames["Month "+str_month+" "+str_name+" :"] = monthnames.get("Month "+str_month+" "+str_name+" :") + 1
    context = {
        'monthnames': monthnames.keys
    }
    print(monthnames.values())
    return render(request, 'statistic.html', context)

def get_all_url_img(request):
    url = []
    all_files = storage.list_files()
    for file in all_files:
        url.append(storage.child(file.name).get_url(user['idToken']))
    url.reverse()
    context = {
        'urls': url
    }
    return render(request, 'home.html',context)
def detail(request,key): 
    detail_sta = []
    key_sta = key
    leght = monthnames.get(key)
    sta_name = key_sta.split(" ")[2]
    sta_month = key_sta.split(" ")[1]
    all_files = storage.list_files()
    for file in all_files:
        x = sta_month in file.name
        y = sta_name in file.name
        if (x == True) and (y == True):
            detail_sta.append(file.name)
    context = {
        'detail_stas': detail_sta,
        'leght' : leght
    }      
    return render(request, 'detail.html', context)

def detail_img(request, name_img):
    nameimg = name_img
    all_files = storage.list_files()
    for file in all_files:
        if (file.name == nameimg):
            str_name = file.name.split("_")[2]
            str_month = file.name.split("_")[0].split("-")[1]
            key_detail_img = "Month "+str_month+" "+str_name+" :"
            url_detail_img = storage.child(file.name).get_url(user['idToken'])
    context = {
        'url_detail_img' : url_detail_img,
        'key_detail_img' : key_detail_img,
        'name_img' : nameimg
    }
    return render(request, 'detail_img.html', context)