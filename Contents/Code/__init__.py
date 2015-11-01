####################################################################################################
#                                                                                                  #
#                               Chaturbate Plex Channel -- v0.01                                   #
#                                                                                                  #
####################################################################################################
# set global variables
PREFIX = '/video/chaturbate'
TITLE = 'Chaturbate'
BASE_URL = 'https://chaturbate.com'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    #ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = 0
    #HTTP.Headers['User-Agent'] = Test.USER_AGENT

####################################################################################################
# Create the main menu

@handler(PREFIX, TITLE, ICON)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)

    oc.add(DirectoryObject(key=Callback(DirectoryList, url=BASE_URL, page=int(1)), title='Featured'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, url=BASE_URL + '/female-cams', page=int(1)), title='Female'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, url=BASE_URL + '/male-cams', page=int(1)), title='Male'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, url=BASE_URL + '/couple-cams', page=int(1)), title='Couple'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, url=BASE_URL + '/transsexual-cams', page=int(1)), title='Transsexual'))

    return oc

####################################################################################################
# list cams

@route(PREFIX + '/directorylist')
def DirectoryList(url, page=int):
    url_cat = url.rsplit('/', 1)[-1]
    if url_cat == 'chaturbate.com':
        url_cat == BASE_URL

    url_page = url + '/?page=%i' %int(page)

    if 'female-cam' in url_cat:
        title2 = 'Female'
    elif 'male-cam' in url_cat:
        title2 = 'Male'
    elif 'couple-cam' in url_cat:
        title2 = 'Couple'
    elif 'transsexual-cam' in url_cat:
        title2 = 'Transsexual'
    else:
        title2 = 'Featured'

    html = HTML.ElementFromURL(url_page)

    # parse html for 'next' and 'last' page number
    next_pg_node = html.xpath('//li[a[text()="next"]]')
    if next_pg_node:
        last_page = int(next_pg_node[0].xpath('./preceding-sibling::li/a[@class="endless_page_link"]/text()')[-1])
        Log(last_page)
        main_title = '%s | Page %i of %i' %(title2, int(page), last_page)
    else:
        main_title = '%s | Page %i | Last Page' %(title2, int(page))

    oc = ObjectContainer(title2=main_title, no_cache=True)

    # parse url for each video and pull out relevant data
    for node in html.xpath('//ul[@class="list"]/li'):
        cam_url = BASE_URL + node.xpath('./a')[0].get('href')
        cover = node.xpath('./a/img')[0].get('src')
        name = node.xpath('.//div[@class="title"]/a/text()')[0].strip()
        age = node.xpath('.//div[@class="title"]/span/text()')[0].strip()
        gender_href = node.xpath('.//div[@class="title"]/span')[0].get('class')
        gender_node = gender_href.split('age gender')[-1]
        summary = node.xpath('.//ul[@class="subject"]/li/text()')
        if summary:
            if len(summary[0]) > 0:
                summary = Regex('[^a-zA-Z0-9 \n]').sub('', summary[0]).strip()
            else: summary = None
        else:
            summary == None

        tag1 = node.xpath('.//ul[@class="sub-info"]/li/text()')[0].strip()
        tag2 = node.xpath('.//ul[@class="sub-info"]/li/text()')[1].strip()

        if gender_node == 'f':
            gender = 'female'
        elif gender_node == 'm':
            gender = 'male'
        elif gender_node == 'c':
            gender = 'couple'
        else:
            gender = 'transsexual'

        oc.add(
            VideoClipObject(
                title=name,
                summary=summary,
                thumb=cover,
                tagline='Age %s | %s | %s' %(age, tag2, tag1),
                url=cam_url
                )
            )

    if next_pg_node:
        next_pg_num = int(html.xpath('//li/a[text()="next"]')[0].get('href').split('=')[1])
        oc.add(NextPageObject(
            key=Callback(DirectoryList, url=url, page=next_pg_num),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer(header='Warning', message='Page Empty')
