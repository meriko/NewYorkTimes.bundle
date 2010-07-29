import re, string, os
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

NYT_PREFIX      = '/video/thenytimes'
NYT_ROOT        = 'http://video.nytimes.com/video'
NYT_SEARCH      = 'http://query.nytimes.com/search/video?date_select=full&type=nyt&query=%s&x=0&y=0&n=50'

CACHE_INTERVAL = 3600 * 6

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(NYT_PREFIX, MainMenu, 'New York Times', 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'New York Times'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def UpdateCache():
  HTTP.Request(NYT_ROOT)

####################################################################################################
def MainMenu():
  dir = MediaContainer()

  dir.Append(Function(DirectoryItem(GetPlaylist, title=L("Featured")), url=NYT_ROOT, id='playlistMostViewedFeatured'))
  dir.Append(Function(DirectoryItem(GetPlaylist, title=L("Most Viewed")), url=NYT_ROOT, id='playlistMostViewed'))

  for li in XML.ElementFromURL(NYT_ROOT, True).xpath('//td[@id="leftNav"]/ul/li'):
    if li.get('class') != 'closed':
      dir.Append(Function(DirectoryItem(GetPlaylist, title=li.find('a').text), url=li.find('a').get('href')))

  dir.Append(Function(SearchDirectoryItem(Search, title=L("Search..."), prompt=L("Search for Videos"), thumb=R('search.png'))))

  return dir

####################################################################################################
def GetPlaylist(sender, url, id='playlistCurrent'):
  dir = MediaContainer(viewGroup='Details')

  playlistRx = re.compile(r"NYTD_PlaylistMgr.addPlaylist\(({ id:'" + id + ".*?\]})\);", re.MULTILINE | re.DOTALL)
  data = HTTP.Request(url)
  xml = XML.ElementFromString(data, True)
  listOfMatches = playlistRx.findall(data)
  obj = JSON.ObjectFromString(listOfMatches[0].encode('utf-8'), errors="ignore")
  
  thumb = None
  for video in obj['list']:
    if 'timg_wide' in video:
      thumb = video['timg_wide']
    else:
      thumb = xml.xpath('//li[@titleref="' + video['ref'] + '"]/a/img')[0].get('src')
    
    dir.Append(WebVideoItem(video['turi'], video['name'], video['lname'], video['desc'], None, thumb))
    
  return dir
  
####################################################################################################
def Search(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details')
  query=query.replace(' ','+')
  
  for li in XML.ElementFromURL(NYT_SEARCH % query, True).xpath("//li[@class='clearfix']"):
    thumbVideo = li.xpath('ul/li[@class="thumb video"]')
    if len(thumbVideo) > 0:
      video = thumbVideo[0]
      thumb = video.xpath('a/img')[0].get('src')
      key = video.find('a').get('href')
      summaryItem = li.xpath('ul/li[@class="summary"]')[0]
      date = summaryItem.xpath('span[@class="byline"]')[0].text
      title = ''.join(summaryItem.xpath('h3/a')[0].itertext()).strip()
      title = title.replace(' - Video Library','')
      
      summary = ''.join(li.itertext())
      summary = summary.replace('Video:','')
      summary = summary.replace(' - Video Library','')
      summary = summary.replace(title,'')
      summary = summary.replace(date,'')
      
      dir.Append(WebVideoItem(key, title, date, summary.strip(), None, thumb))
  
  return dir