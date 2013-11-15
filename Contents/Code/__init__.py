NYT_ROOT = 'http://www.nytimes.com/video'
PLAYLIST_URL = 'http://www.nytimes.com/svc/video/api/playlist/%s'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'New York Times'
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/thenytimes', 'New York Times')
def MainMenu():

	oc = ObjectContainer()
	html = HTML.ElementFromURL(NYT_ROOT, cacheTime=CACHE_1DAY)

	for channel in html.xpath('//nav[contains(@class, "main-nav")]//li[@data-id]'):
		title = channel.xpath('./a//text()')[0]
		playlist_id = channel.xpath('./@data-id')[0]

		oc.add(DirectoryObject(
			key = Callback(Playlist, title=title, playlist_id=playlist_id),
			title = title
		))

	return oc

####################################################################################################
@route('/video/thenytimes/playlist', allow_sync=True)
def Playlist(title, playlist_id):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(PLAYLIST_URL % playlist_id)

	for video in json_obj['videos']:

		date = video['publish_url'].split('/')
		date = '%s-%s-%s' % (date[2], date[3], date[4])

		oc.add(VideoClipObject(
			url = '%s%s' % (video['domain'], video['seo_url']),
			title = video['headline'],
			summary = video['summary'],
			originally_available_at = Datetime.ParseDate(date).date(),
			thumb = Resource.ContentsOfURLWithFallback('%s/%s' % (video['domain'], video['images'][-1]['url']))
		))

	return oc
