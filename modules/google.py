#-*- coding: utf-8 -*-
import urllib
import requests
import json
import time
import traceback
import random
from bs4 import BeautifulSoup
from core.ext.text import strtr
from core.ext.unicode import u
from core.ext.temp import generate_temp_name
from modules import module, dispatch, Result, ResultType

SEARCH_PIC_URL = "https://www.google.com/search?q={0}&tbm=isch&tbs=isz:m"
@module.route(ur'^([가-힣a-zA-Z0-9\s]+)\s{0,}?사진\s{0,}?(구해|가져|찾아|검색|내놔)', re=True, prefix=False)
def search_photo(message, session, pic_name, pic_command):
    resp_type = None
    resp_content = None
    try:
        url = SEARCH_PIC_URL.format(u(pic_name))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
        }
        request = requests.get(url, timeout=5, headers=headers, verify=False)

        if request and request.status_code == 200:
            data = BeautifulSoup(request.text)
            results = data.select('#rg a')

            if len(results) is 0:
                resp_type = ResultType.TEXT
                resp_content = u'검색결과가 없습니다.'
            else:
                href = urllib.unquote(random.choice(results)['href']) \
                    .replace('http://www.google.com/imgres?', '')
                split = href.split('&img')
                link = urllib.unquote(split[0].replace('imgurl=', ''))
                tmp = generate_temp_name()

                headers['Referer'] = request.url
                r = requests.get(link, stream=True, headers=headers, timeout=10)
                if r.status_code == 200:
                    with open(tmp, 'wb') as f:
                        for chunk in r.iter_content():
                            f.write(chunk)
                    resp_type = ResultType.IMAGE
                    resp_content = tmp
                else:
                    resp_type = ResultType.TEXT
                    resp_content = u'{0} 사진을 가져오지 못했습니다. 대신 링크라도 드릴게요: {1}'.format(pic_name, link)
        else:
            resp_type = ResultType.TEXT
            resp_content = u'{0} 사진 가져오는데 너무 오래걸려서 중지시켰어요. 명령을 다시 내려주세요.'.format(pic_name)
    except Exception, e:
        resp_type = ResultType.TEXT
        resp_content = u"{0}사진을 가져오지 못했습니다\r\n가져오는데 너무 오래걸려 취소됐을 수도 있습니다.".format(pic_name)

    return Result(type=resp_type, content=resp_content)

SEARCH_YOUTUBE_URL = "http://gdata.youtube.com/feeds/api/videos?q={0}&max-results=3&alt=jsonc&v=2"
YOUTUBE_REPLACE_PATTERN = {
    u'단위인정': u'段位認定',
    u'개전': u'皆伝',
}
@module.route(ur'^([가-힣a-zA-Z0-9\s]+)\s{0,}?(동영상|영상|유튜브)', re=True, prefix=False)
def search_youtube(message, session, name, search_command):
    resp_type = None
    resp_content = None
    name = name.strip()
    name = strtr(name, YOUTUBE_REPLACE_PATTERN)
    try:
        url = SEARCH_YOUTUBE_URL.format(u(name))
        request = requests.get(url, timeout=5, verify=False)

        if request and request.status_code == 200:
            data = json.loads(request.text)['data']

            if data['totalItems'] is 0:
                resp_type = ResultType.TEXT
                resp_content = u'검색결과가 없습니다.'
            else:
                resp_type = ResultType.TEXT
                resp_content = u''
                items = data['items']

                for item in items:
                    player = item['player']['mobile'] if 'mobile' in item['player'] else item['player']['default']
                    rating = str(item['rating']) if 'rating' in item else '0'
                    resp_content += u"{0}\r\n".format(item['title'])
                    resp_content += u"조회: {0}, 별점: {1}\r\n".format(str(item['viewCount']), rating)
                    resp_content += u"{0}\r\n".format(player)
        else:
            resp_type = ResultType.TEXT
            resp_content = u'{0} 영상을 찾지 못했습니다.'.format(name)
    except Exception, e:
        traceback.print_exc()
        resp_type = ResultType.TEXT
        resp_content = u"{0} 영상을 찾지 못했습니다.\r\n가져오는데 너무 오래 걸려 취소됐을 수도 있습니다.".format(name)

    return Result(type=resp_type, content=resp_content)

