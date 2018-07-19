from django.shortcuts import render , HttpResponse
from .models import TargetData , TreasureHuntData,SearchTargetData
from .forms import TargetForm,TreasureHuntForm,SearchTargetDataForm
import json
from rest_framework.test import RequestsClient
import base64
from django.conf import settings
import hashlib
import hmac
import urllib3
from datetime import datetime , timezone
from time import mktime
from time import strftime, gmtime
from wsgiref.handlers import format_date_time
from email.utils import formatdate
import sys
import mimetypes


# Create your views here.

# The hostname of the Cloud Recognition Web API
CLOUD_RECO_API_ENDPOINT = 'cloudreco.vuforia.com'


def compute_md5_hex(data):
    """Return the hex MD5 of the data"""
    h = hashlib.md5()
    h.update(data)
    return h.hexdigest()


def compute_hmac_base64(key, data):
    """Return the Base64 encoded HMAC-SHA1 using the provide key"""
    h = hmac.new(key, None, hashlib.sha1)
    h.update(data)
    return base64.b64encode(h.digest())


def authorization_header_for_request(access_key, secret_key, method, content, content_type, date, request_path):
    """Return the value of the Authorization header for the request parameters"""
    components_to_sign = list()
    components_to_sign.append(method)
    components_to_sign.append(str(compute_md5_hex(content)))
    components_to_sign.append(str(content_type))
    components_to_sign.append(str(date))
    components_to_sign.append(str(request_path))
    string_to_sign = "\n".join(components_to_sign)
    signature = compute_hmac_base64(secret_key, string_to_sign.encode('utf-8'))
    auth_header = "VWS %s:%s" % (access_key, signature.decode('utf-8'))
    return auth_header


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Query image')
    parser.add_argument('--access-key', required=True, type=str, help='The access key for the VuMark database')
    parser.add_argument('--secret-key', required=True, type=str, help='The secret key for the VuMark database')
    parser.add_argument('--max-num-results', required=False, type=int,
                        default=10, help='The maximum number of matched targets to be returned')
    parser.add_argument('--include-target-data', type=str, required=False,
                        default='top', choices=['top', 'none', 'all'],
                        help='Specified for which results the target metadata is included in the response')
    parser.add_argument('image', nargs=1, type=str, help='Image path')
    args = parser.parse_args()

    status, query_response = send_query(access_key=args.access_key,
                             secret_key=args.secret_key,
                             max_num_results=str(args.max_num_results),
                             include_target_data=args.include_target_data,
                             image=args.image[0])




def uploadTD(request):


    http = urllib3.PoolManager()
    target_data_form = TargetForm()
    target_data_form2 = TargetForm(request.POST)
    if request.method == 'POST':
        form = target_data_form.save(commit=False)
        #get the data from http request and add it to database
        target_name = request.POST.get("target_name")
        nameTH = request.POST.get("NameTH")
        target_text = request.POST.get("target_text")
        target_image = request.POST.get("target_image")
        target_3d_model = request.POST.get("target_3d_model")
        target_recognition_image = request.POST.get("target_recognition_image")
        form.target_name = target_name
        form.target_text = target_text
        form.target_image = target_image
        form.target_3d_model = target_3d_model
        form.target_recognition_image = target_recognition_image
        form.save()
        #make a http request to vuforia cloud for creation of a new target
        client = RequestsClient()
        http_verb='POST'
        request_path='/targets'
        content_type = 'application/json'
        date = formatdate(None, localtime=False, usegmt=True)
        print(target_name)
        data = {"name":target_name,
                "width": 1.15,
                "image": image,
                }
        encoded_data = json.dumps(data).encode('utf-8')
        x = authorization_header_for_request('be29c77995e53b7652b2f2589410c26d3fad0817', settings.API_SERVICE_SECRET_KEY.encode('utf-8'), http_verb,encoded_data,content_type,date, request_path)


        print(x)
        print(date)
        r = http.request('POST','https://vws.vuforia.com/targets',body=encoded_data,headers = {'Authorization':str(x),
                                                                                               'Date':date,
                                                                                               'Content-Type': 'application/json'})
        print(r.status)
        print(r.data)
        print(r.read)


        #requesting a json with all targets id

    return render(request, "uploadTD.html", {'target_data_form': target_data_form})



def uploadTHD(request):
    treasure_hunt_data_form = TargetForm()
    treasure_hunt_data_form2 = TargetForm(request.POST)
    if request.method == 'POST':
        #add a treasurehunts
        form = treasure_hunt_data_form.save(commit=False)
        th_name = request.POST.get("THName")
        form.THName = th_name
        form.save()
    return render(request,"uploadTHD.html",{'treasure_hunt_data_form':treasure_hunt_data_form})

def searchTargetData(request):
    target_data_form = SearchTargetDataForm()
    target_data_form2 = SearchTargetDataForm(request.POST)
    if request.method == 'POST':
        targetid = request.POST.get("targetid")
        th_name = request.POST.get("thname")
        ip = request.POST.get("ip")
        targetdata = TargetData.objects.filter(target_id = targetid).filter(thname = th_name)
        #return a json with deatils
        data = {
            'target_image': targetdata.target_image,
            'target_3d_model': targetdata.target_3d_model,
            'target_text': targetdata.target_text,
        }
    dump = json.dumps(data)
    return HttpResponse(dump, content_type='application/json')
