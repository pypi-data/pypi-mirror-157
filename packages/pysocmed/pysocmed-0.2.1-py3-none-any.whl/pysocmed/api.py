from urllib import response
from googleapiclient.discovery import build
import pandas as pd

class YouTube():
    def __init__(self, api_key) -> None:
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def _check_param(self, return_type):
        if return_type not in ['json', 'pandas_json',  'pandas_normalize']:
            raise Exception('return_type value must be one of "json", "pandas_json", or "pandas_normalize"')
    
    def _formatter(self, response, return_type='json'):
        if return_type == 'pandas_json':
            return pd.DataFrame(response['items'])
        elif return_type == 'pandas_normalize':
            return pd.json_normalize(response['items'])
        else:
            return response
    
    def _get(self, access_type, param, max_results, limit):

        if max_results > limit:
            num_results = limit
            max_results = max_results - limit
        else:
            num_results = max_results
            max_results = 0

        request = access_type.list(
            maxResults=num_results,
            **param
        )

        response = request.execute()
        if 'nextPageToken' in response.keys():
            next_token = response['nextPageToken']
        else:
            max_results = 0

        while max_results > 0:
            if max_results > limit:
                num_results = limit
                max_results = max_results - limit
            else:
                num_results = max_results
                max_results = 0

            request = access_type.list(
                **param,
                maxResults=num_results,
                pageToken=next_token
            )
            new_response = request.execute() 
            items = new_response['items']

            if len(items) == 0:
                break
            response['items'] = response['items'] + items
            
            if 'nextPageToken' in new_response.keys():
                next_token = new_response['nextPageToken']
            else:
                break
        return response

    def get_search(
        self, keyword, max_results=50, content_type=None, 
        lat=None, long=None, radius=None,
        related_to=None, event_type=None,
        return_type='json'):

        self._check_param(return_type)
        if lat is None or long is None:
            location = None
        else:
            content_type = 'video' if content_type is None else content_type
            radius = '10mi' if radius is None else content_type
            location = f'{lat},{long}'
            event_type = 'video'

        if related_to is not None or event_type is not None:
            content_type = 'video'
        
        param = {
            'part': 'snippet',
            'q': keyword,
            'location': location,
            'locationRadius':radius,
            'relatedToVideoId': related_to,
            'eventType':event_type
        }
        
        response = self._get(
            self.youtube.search(),
            param, max_results,
            limit=50
        )

        return self._formatter(response, return_type)

    def get_comments(self, url, max_results=100, order='time', return_type='json'):

        self._check_param(return_type)
        video_id = url.split('=')[-1]
        param = {
            'part': 'snippet,replies',
            'videoId': video_id,
            'order': order
        }
        
        response = self._get(
            self.youtube.commentThreads(),
            param, max_results,
            limit=100
        )

        return self._formatter(response, return_type)
    
    def get_popular(self, region_code, max_results=50, return_type='json'):
        self._check_param(return_type)
        param = {
            'part': 'snippet,contentDetails,statistics',
            'chart': 'mostPopular',
            'regionCode': region_code
        }
        
        response = self._get(
            self.youtube.videos(),
            param, max_results,
            limit=50
        )

        return self._formatter(response, return_type)

    def get_replies(self, comment_id, max_results=100, return_type='json'):
        self._check_param(return_type)
        param = {
            'part': 'snippet',
            'parentId': comment_id
        }
        
        response = self._get(
            self.youtube.comments(),
            param, max_results,
            limit=100
        )

        return self._formatter(response, return_type)
class Twitter():
    def __init__(self) -> None:
        pass
