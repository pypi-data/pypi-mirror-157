from googleapiclient.discovery import build


class YouTube():
    def __init__(self, api_key) -> None:
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_search(
        self, keyword, max_results=None, content_type=None, 
        lat=None, long=None, radius=None,
        related_to=None, event_type=None,
        fields='snippet'):

        if lat is None or long is None:
            location = None
        else:
            content_type = 'video' if content_type is None else content_type
            radius = '10mi' if radius is None else content_type
            location = f'{lat},{long}'


        request = self.youtube.search().list(
            part=fields, maxResults=max_results, q=keyword, type=content_type,
            location=location, locationRadius=radius,
            relatedToVideoId=related_to, eventType=event_type
            )

        return request.execute()


class Twitter():
    def __init__(self) -> None:
        pass

