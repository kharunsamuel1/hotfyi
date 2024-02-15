from googleapiclient.discovery import build
import pymongo

class Topic():
    def __init__(self, name):
        self.name = name
        self.youtube = build('youtube', 'v3', developerKey='AIzaSyCAs9vfsygT-ykCjjkpMBZ-GJ__lADVhC8')
        self.channels = {}
        self.views = {}

    def transformViews(self, name):
        pass

    def persistChannels(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/hfcluster")
        db = client["hfcluster"]
        collection = db["channels"]
        for channel in self.channels:
            id = self.channels[channel]
            views = self.views[id] if id in self.views else []
            document = {
                "name": channel,  # Specify the name field for identification
                "id": id,
                "topic": self.name,
                "views": views
            }

            # Use the update_one() method with upsert=True
            result = collection.update_one(
                {"name": channel},   # Filter criteria to find the document by name
                {"$set": document},  # Set the fields and values to insert or update
                upsert=True  # Set upsert option to true
            )

    def transformViews(self):
        pass


    def exploreChannels(self):
        def exploreChannel(channel_id):
            max_results = 15
            channel_response = self.youtube.channels().list(
                id=channel_id,
                part='contentDetails'
            ).execute()

            if 'items' in channel_response:
                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                # Retrieve the last 10 videos from the uploads playlist
                playlist_response = self.youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='contentDetails',
                    maxResults=max_results
                ).execute()

                video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]

                # Get video statistics (including views) for each video
                video_response = self.youtube.videos().list(
                    id=','.join(video_ids),
                    part='statistics'
                ).execute()

                video_statistics = video_response['items']

                views_data = []
                for video_stat in video_statistics:
                    views = int(video_stat['statistics']['viewCount'])
                    # Good place to grab and set date information
                    # video_id = video_stat['id']
                    views_data.append(views)
                self.views[channel_id] = views_data
                return views_data

            else:
                return None
        for id in self.channels.values():
            print(exploreChannel(id))

    def exploreChannelsDry(self):
        self.views = {'UC7O8KgJdsE_e9op3vG-p2dg': [('xdhXsO124cM', 23706), ('Jb6Xs86Ewlw', 28438), ('-Kl394MQXsQ', 56585),
                                                   ('Tn4JTY1Lo0g', 144153), ('LWsAbG3pAxQ', 101831), ('NwdwtmUT-l8', 122707),
                                                   ('Wj1U0DxMvIs', 117066), ('3vBUREkRzug', 121045), ('J0Q-dwuxK-s', 132890),
                                                   ('CjPSzAtLzO8', 96544), ('g8j3xyrO_Ds', 110051), ('zZBdVk3KFTk', 251788),
                                                   ('al2LfAlTgJw', 91096), ('QJ9PSZtJ3KM', 62942), ('-034WD-KvH8', 78507)],
                      'UCpsKoMnKZaFekA9vZNftbPw': [('vBYAx-kAKRQ', 3097), ('kkRDpm3rHRk', 8824), ('KWQXnF6IoKs', 17885),
                                                   ('RC3zg1gIBWU', 13272), ('TUR0B5sMqj8', 18205), ('1vAC9xms4i4', 12410),
                                                   ('VymNsmvpUo0', 16866), ('qJqYvirSulg', 67333), ('8p4afmqduJw', 28594),
                                                   ('Soe0pXXxvOs', 16880), ('oiUdy8k6QIY', 8812), ('iR5LtqAbAwQ', 10799),
                                                   ('_GNo0xcweng', 11439), ('knkvnmkhikc', 12269), ('-lYQsEfSph4', 5876)],
                      'UCV5_FNKj1x-EB4dGTUTltHA': [('u0j1NBVOBlk', 57158), ('uIIRs12PhGw', 15396), ('g5cmV5NgpL0', 12074),
                                                   ('is9uEJCqhVo', 163394), ('_8n9FEXCI-I', 13986), ('ghUfgfw5qaQ', 11609),
                                                   ('AtiN6fj5Y9M', 30104), ('VjvmY-0mk5s', 37393), ('n-vdHxpbThg', 48911),
                                                   ('wcd4PVf3EEI', 49940), ('GggKg2apEUQ', 24906), ('2mzy3_wE5D0', 58409),
                                                   ('CARc_GevFjg', 124000), ('Ss4XehLJIOs', 51124), ('8zgOw3fNoE4', 23442)],
                      'UCblfuW_4rakIf2h6aqANefA': [('IW7lxmqrvuA', 33543), ('EpZUFICDdpA', 103664), ('AlYfVwPfeK8', 187156),
                                                   ('3i-C0T8u5PY', 133554), ('B1OopoRdKz8', 150202), ('oyN22tqx0_Y', 143190),
                                                   ('I2ZzqdlGbn0', 253113), ('NqI6b8tDzSc', 2123091), ('NCx3Pve3Bhw', 159732),
                                                   ('qKi6vTpIDLw', 202054), ('gSOlczNZsII', 1690163), ('kLWM2f14e64', 1200110),
                                                   ('zf1h5WNErrQ', 430953), ('-HNqrdHxq34', 1007078), ('P7rnLMrqZxk', 927209)]}

    def exploreTopic2(self):
        query = self.name
        max_results = 10
        search_response = self.youtube.search().list(
            q=query,
            type='video,channel',
            part='id',
            maxResults=max_results
        ).execute()

        result_items = search_response.get('items', [])

        results = []

        for item in result_items:
            video_id = item['id']['videoId'] if 'videoId' in item['id'] else ''
            channel_id = item['id']['channelId'] if 'channelId' in item['id'] else ''

            if video_id:
                # If it's a video, get video details
                video_response = self.youtube.videos().list(
                    id=video_id,
                    part='snippet'
                ).execute()
                video_info = video_response.get('items', [])[0]['snippet']
                self.channels[video_info['channelTitle']] = video_info['channelId']
                results.append((video_info['title'], 'Video'))
            elif channel_id:
                # If it's a channel, get channel details
                channel_response = self.youtube.channels().list(
                    id=channel_id,
                    part='snippet'
                ).execute()
                channel_info = channel_response.get('items', [])[0]['snippet']
                self.channels[channel_info['title']] = channel_id
                results.append((channel_info['title'], 'Channel'))

        return results

    def exploreTopicDry(self):
        self.channels = {'Johnny FPV': 'UC7O8KgJdsE_e9op3vG-p2dg', 'Fenix FPV': 'UCpsKoMnKZaFekA9vZNftbPw',
                         'Captain Vanover': 'UCV5_FNKj1x-EB4dGTUTltHA', 'Red Bull': 'UCblfuW_4rakIf2h6aqANefA'}