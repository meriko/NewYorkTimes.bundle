
TITLE           = 'New York Times'
ART             = 'art-default.jpg'
ICON            = 'icon-default.jpg'

NYT_PREFIX      = '/video/thenytimes'
NYT_ROOT        = 'http://video.nytimes.com/video'
NYT_SEARCH      = 'http://query.nytimes.com/search/video?date_select=full&type=nyt&query=%s&x=0&y=0&n=50'

CACHE_INTERVAL = 3600 * 6

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(NYT_PREFIX, MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup("Details", viewMode = "InfoList", mediaType = "items")

  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'Details'
  ObjectContainer.art = R(ART)

  DirectoryObject.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  InputDirectoryObject.art = R(ART)
  InputDirectoryObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)

  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenu():
  oc = ObjectContainer()

  oc.add(DirectoryObject(key = Callback(GetPlaylist, title = L("Featured"), url = NYT_ROOT, id = 'playlistMostViewedFeatured'), title = L("Featured")))
  oc.add(DirectoryObject(key = Callback(GetPlaylist, title = L("Most Viewed"), url = NYT_ROOT, id = 'playlistMostViewed'), title = L("Most Viewed")))

  page = HTML.ElementFromURL(NYT_ROOT)
  for li in page.xpath('//td[@id="leftNav"]/ul/li'):
    if li.get('class') != 'closed':
      title = li.find('a').text
      url = li.find('a').get('href')
      oc.add(DirectoryObject(key = Callback(GetPlaylist, title = title, url = url), title = title))

  oc.add(InputDirectoryObject(key = Callback(Search), title = L("Search..."), prompt=L("Search for Videos")))

  return oc

####################################################################################################
def GetPlaylist(title, url, id='playlistCurrent'):
  oc = ObjectContainer(title2 = title)

  data = HTTP.Request(url).content
  xml = HTML.ElementFromString(data)

  playlist_regex = Regex(r"NYTD_PlaylistMgr.addPlaylist\(({ id:'" + id + ".*?\]})\);", Regex.MULTILINE | Regex.DOTALL)
  matches = playlist_regex.findall(data)
  obj = JSON.ObjectFromString(matches[0].encode('utf-8'))
  
  thumb = None
  for video in obj['list']:
    if 'timg_wide' in video:
      thumb = video['timg_wide']
    else:
      thumb = xml.xpath('//li[@titleref="' + video['ref'] + '"]/a/img')[0].get('src')
    
    oc.add(VideoClipObject(
      url = video['turi'],
      title = video['name'],
      summary = video['desc'],
      thumb = thumb))
    
  return oc
  
####################################################################################################
def Search(query = 'the', page = 1):
  oc = ObjectContainer(title2 = query)

  query = query.replace(' ','+')
  
  page = HTML.ElementFromURL(NYT_SEARCH % query)
  for li in page.xpath("//li[@class='clearfix']"):
    thumbVideo = li.xpath('ul/li[@class="thumb video"]')
    if len(thumbVideo) > 0:
      video = thumbVideo[0]
      thumb = video.xpath('a/img')[0].get('src')
      video_url = video.find('a').get('href')
      summaryItem = li.xpath('ul/li[@class="summary"]')[0]
      date_text = summaryItem.xpath('span[@class="byline"]')[0].text
      date = Datetime.ParseDate(date_text)
      title = ''.join(summaryItem.xpath('h3/a')[0].itertext()).strip()
      title = title.replace(' - Video Library','')
      
      summary = ''.join(li.itertext())
      summary = summary.replace('Video:','')
      summary = summary.replace(' - Video Library','')
      summary = summary.replace(title,'')
      summary = summary.replace(date_text,'')
      
    oc.add(VideoClipObject(
      url = video_url,
      title = title,
      summary = summary.strip(),
      thumb = thumb))
  
  return oc