import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import requests

addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])


# TODO: move this into a svc class
def get_feed_ids():
    req = requests.get('https://murmuring-brook-54768.herokuapp.com/feedids')
    if req.status_code == 200:
        print "BBFEEDIDENT: BB feed id data returned from web"
        return req.json()
    print "BBFEEDIDENT: Returning static BB feed id data"
    return [{
        'title': 'BBCan1', 
        'aid': '6388794', 
        'eid': '8525962'
    },
    {
        'title': 'BBCan2', 
        'aid': '16559084', 
        'eid': '8525982'
    },
    {
        'title': 'BBCan3', 
        'aid': '16559088', 
        'eid': '8525991'
    },
    {
        'title': 'BBCan4', 
        'aid': '16559095', 
        'eid': '8525992'
    }]


def create_feed_list():
    listing = []
    ids = get_feed_ids()

    for ident in ids:
        aid = ident['aid']
        eid = ident['eid']
        fdata = get_feed_data(aid, eid)
        if fdata is None:
            continue
        item = xbmcgui.ListItem(label='[B]Live Feed[/B] ('+ fdata['title'] +')', thumbnailImage=fdata['thumb'])
        url = '{0}?action=play&a={1}&e={2}'.format(addon_url, aid, eid)
        is_folder = False
        listing.append((url, item, is_folder))

    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(addon_handle)


def playFeed(aid, eid):
    fdata = get_feed_data(aid, eid)
    item = xbmcgui.ListItem(label='Live Feed ('+ fdata['title'] +')')
    stream = fdata['m3u8']
    xbmc.Player().play(stream, item)
    #TODO: attach event to update listing on stop/go back/other action that goes up a level??
    # Or maybe just add an option to manually refresh the thumbnails.


def get_feed_data(aid, eid):
    req = requests.get('http://livestream.com/api/accounts/'+ aid +'/events/'+ eid +'/viewing_info')
    data = req.json()
    if data['streamInfo'] is None:
        return None
    return {
        'title': data['streamInfo']['stream_title'],
        'thumb': data['streamInfo']['thumbnail_url'], 
        'm3u8': data['streamInfo']['m3u8_url'],
        'rtsp': data['streamInfo']['rtsp_url']
    }


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    print "BBFEEDROUTE: params were: " + paramstring
    if params:
        action = params['action']
        if action == 'listing':
            create_feed_list()
        elif action == 'play':
            playFeed(params['a'], params['e'])
    else:
        create_feed_list()


if __name__ == '__main__':
    router(sys.argv[2][1:])
