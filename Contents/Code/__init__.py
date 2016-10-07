####################################################################################################
#                                                                                                  #
#                                   Chaturbate Plex Channel                                        #
#                                                                                                  #
####################################################################################################
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs

# set global variables
PREFIX = '/video/chaturbate'
TITLE = 'Chaturbate'
BASE_URL = 'https://chaturbate.com'
ICON = 'icon-default.png'
ART = 'art-default.jpg'

CAT_LIST = ['Free Cams', 'Free Cams by Age', 'Free Cams by Region', 'Free Cams by Status']

MAIN_LIST = [
    ('Featured', ''), ('Female', '/female'), ('Male', '/male'),
    ('Couple', '/couple'), ('Transsexual', '/transsexual')
    ]

AGE_LIST = [
    ('Teen Cams (18+)', '/teen-cams'), ('18 to 21 Cams', '/18to21-cams'),
    ('20 to 30 Cams', '/20to30-cams'), ('30 to 50 Cams', '/30to50-cams'),
    ('Mature Cams (50+)', '/mature-cams')
    ]

REGION_LIST = [
    ('North American Cams', '/north-american-cams'), ('Other Region Cams', '/other-region-cams'),
    ('Euro Russian Cams', '/euro-russian-cams'), ('Philippines Cams', '/philippines-cams'),
    ('Asian Cams', '/asian-cams'), ('South American Cams', '/south-american-cams')
    ]

STATUS_LIST = [
    ('Exhibitionist Cams', '/exhibitionist-cams'), ('HD Cams', '/hd-cams')
    ]

CAT_DICT = {'Age': {'list': AGE_LIST}}
CAT_DICT.update({'Region': {'list': REGION_LIST}})
CAT_DICT.update({'Status': {'list': STATUS_LIST}})

GENDER_DICT = {'f': 'female', 'm': 'male', 'c': 'couple', 's': 'transsexual'}

####################################################################################################

def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    HTTP.CacheTime = 0

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    """
    Setup Main menu
    Free Cams', Free Cams by Age', Free Cams by Region, Free Cams by Status
    """

    oc = ObjectContainer(title2=TITLE, art=R(ART), no_cache=True)

    Updater(PREFIX + '/updater', oc)

    for t in CAT_LIST:
        oc.add(DirectoryObject(key=Callback(SubList, title=t), title=t))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R('icon-search.png'))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', summary='Search Chaturbate',
            prompt='Search for...', thumb=R('icon-search.png')
            ))

    return oc

####################################################################################################
@route(PREFIX + '/catlist')
def SubList(title):
    """
    Setup Sub list
    Main, Age, Region, Status
    """

    oc = ObjectContainer(title2=title)

    if title == 'Free Cams':
        cat_list_t = [(n, c+'-cams') for (n, c) in MAIN_LIST]
        for (n, c) in cat_list_t:
            name =  '%s | %s' %(title, n)
            if n == 'Featured':
                oc.add(DirectoryObject(
                    key=Callback(DirectoryList, title=name, url=BASE_URL, page=1), title=n
                    ))
            else:
                oc.add(DirectoryObject(
                    key=Callback(DirectoryList, title=name, url=BASE_URL + c, page=1), title=n
                    ))
    else:
        cat_list_t = CAT_DICT[title.split('by')[-1].strip()]['list']
        for (n, c) in cat_list_t:
            name = '%s | %s' %(title, n)
            oc.add(DirectoryObject(
                key=Callback(CatList, title=name, url=BASE_URL + c), title=n
                ))

    return oc

####################################################################################################
@route(PREFIX + '/subcatlist')
def CatList(title, url):
    """
    Setup Category List
    Featured, Female, Male, Couple, Transsexual
    """

    oc = ObjectContainer(title2=title)

    for (n, c) in MAIN_LIST:
        name = '%s | %s' %(title, n)
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title=name, url=url + c, page=1), title=n
            ))

    return oc

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(title, url, page):
    """List Currently active cams"""

    html = HTML.ElementFromURL(url)

    # parse html for 'next' and 'last' page number
    next_pg_node = html.xpath('//li/a[@class="next endless_page_link"]')
    #last_pg_node = html.xpath('//link[@rel="next"]')
    if next_pg_node:
        last_page = int(html.xpath('//li/a[@class="endless_page_link"]/text()')[-1])
        Log.Debug('* last page = %i' %last_page)
        main_title = '%s | Page %i of %i' %(title, page, last_page)
    elif page == 1:
        main_title = title
    else:
        main_title = '%s | Page %i | Last Page' %(title, page)

    oc = ObjectContainer(title2=main_title, no_cache=True)
    time_stamp = int(Datetime.TimestampFromDatetime(Datetime.Now()))

    # parse url for each video and pull out relevant data
    for node in html.xpath('//ul[@class="list"]/li'):
        cam_url = BASE_URL + node.xpath('./a')[0].get('href')
        cover = node.xpath('./a/img')[0].get('src') + '?_=%i' %time_stamp
        name = node.xpath('.//div[@class="title"]/a/text()')[0].strip()
        age = node.xpath('.//div[@class="title"]/span/text()')[0].strip()
        gender_href = node.xpath('.//div[@class="title"]/span')[0].get('class')
        summary = node.xpath('.//ul[@class="subject"]/li/text()')
        if summary:
            if len(summary[0]) > 0:
                summary = Regex(r'[^a-zA-Z0-9 \n]').sub('', summary[0]).strip()
            else: summary = None
        else:
            summary == None

        tags = node.xpath('.//ul[@class="sub-info"]/li/text()')
        tags = [s.strip() for s in tags]

        gender = GENDER_DICT[gender_href.split('age gender')[-1]]

        try:
            year = int(Datetime.ParseDate(str(Datetime.Now())).year) - int(age)
        except:
            year = None
            Log.Debug('* cannot parse year')

        oc.add(VideoClipObject(
            title=name,
            summary=summary,
            thumb=cover,
            tagline=u"Age {} | {}".format(age, ' | '.join(tags)),
            year=year,
            url=cam_url
            ))

    if next_pg_node:
        next_pg_url = BASE_URL + next_pg_node[0].get('href')
        next_pg_num = int(next_pg_url.split('=')[1])
        Log.Debug('*' * 80)
        Log.Debug('* next url   = %s' %next_pg_url)
        Log.Debug('* next pg #  = %s' %next_pg_num)
        Log.Debug('*' * 80)
        oc.add(NextPageObject(
            key=Callback(DirectoryList, title=title, url=next_pg_url, page=next_pg_num),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc

    return MessageContainer(header='Warning', message='Page Empty')

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Search for Exact user"""

    query = query.strip()
    url = '%s/?keywords=%s' %(BASE_URL, query)
    title = 'Search for ' + query

    return DirectoryList(title, url, 1)

