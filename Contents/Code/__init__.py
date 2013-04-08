NYT_ROOT = 'http://video.nytimes.com/video'
PLAYLIST_URL = 'http://www.nytimes.com/video/svc/scoop/playlist/%s/index.html' # This is a json feed

RE_CHANNELS = Regex("'channels': (?P<channels_json>\[\{.+?\}\])\};")

####################################################################################################
def Start():

	ObjectContainer.title1 = 'New York Times'
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/thenytimes', 'New York Times')
def MainMenu():

	return Channels()

####################################################################################################
@route('/video/thenytimes/channels', i=int)
def Channels(title='', i=-1):

	oc = ObjectContainer()

	page = HTTP.Request(NYT_ROOT, cacheTime=CACHE_1DAY).content
	chanels_json = RE_CHANNELS.search(page).group('channels_json')

	if i == -1:
		channels = JSON.ObjectFromString(chanels_json)
	else:
		channels = JSON.ObjectFromString(chanels_json)[i]['subChannels']

	for i, channel in enumerate(channels):
		if 'showInLibrary' in channel and not channel['showInLibrary']:
			continue

		title = channel['displayName']

		if 'subChannels' not in channel or len(channel['subChannels']) < 1:
			oc.add(DirectoryObject(
				key = Callback(Playlist, title=title, playlist_id=channel['knewsId']),
				title = title
			))
		else:
			oc.add(DirectoryObject(
				key = Callback(Channels, title=title, i=i),
				title = title
			))

	return oc

####################################################################################################
@route('/video/thenytimes/playlist', allow_sync=True)
def Playlist(title, playlist_id):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(PLAYLIST_URL % playlist_id)

	for video in json_obj['videos']:
		oc.add(VideoClipObject(
			url = video['permalink'],
			title = video['name'],
			summary = video['longDescription'],
			duration = video['length'] if isinstance(video['length'], int) else None,
			originally_available_at = Datetime.ParseDate(video['publishedDateGMT']).date(),
			thumb = Resource.ContentsOfURLWithFallback(video['videoStillURL'])
		))

	return oc
