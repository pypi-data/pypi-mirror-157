# module imports
import requests
import os
import base64
import urllib3
import json

# imports for modules used in the package
from .resources import regions
from .resources import queues 

from .auth import Auth

# exceptions
from .exceptions import ResponseError, HandshakeError, LockfileError, PhaseError

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Client:

    def __init__(self, region="na", auth=None):
        '''
        NOTE: when using manual auth, local endpoints will not be available
        auth format:
        {
            "username":"usernamehere",
            "password":"passwordhere"
        }
        '''
        if auth is None:
            self.lockfile_path = os.path.join(
                os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')

        self.puuid = ""
        self.en_token= ""
        self.authorization= ""
        self.local_authorization = ""
        self.local_port = ""
        self.player_name = ""
        self.player_tag = ""
        self.lockfile = {}
        self.headers = {}
        self.local_headers = {}
        self.region = region
        self.shard = ""
        self.auth = None
        self.client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

        if auth is not None:
            self.auth = Auth(auth)

        if region in regions:
            self.region = region
        else:
            raise ValueError(f"Invalid region, valid regions are: {regions}")

        if region == "latam" or region == "br" or region == "pbe":
            self.shard = "na"
        else:
            self.shard = region

    def activate(self) -> None:
        '''Activate the client and get authorization'''
        try:
            if self.auth is None:
                self.lockfile = self.__get_lockfile()
                self.puuid, self.headers, self.local_headers = self.__get_headers()
                self.authorization = self.headers["Authorization"]
                self.en_token = self.headers["X-Riot-Entitlements-JWT"]
                self.local_authorization = self.local_headers["Authorization"]
                self.local_port = self.lockfile["port"]
            else:
                self.puuid, self.authorization, self.en_token, _ = self.auth.authenticate()
        except:
            raise HandshakeError("Unable to activate; is VALORANT running?")

    # --------------------------------------------------------------------------------------------------

    # PVP endpoints
    def fetch_content(self) -> dict:
        '''
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        '''
        url=f"https://shared.{self.shard}.a.pvp.net/content-service/v3/content"
        headers= {
            "X-Riot-ClientVersion": self.__get_current_version(),
            "X-Riot-ClientPlatform": self.client_platform
        }
        data = requests.get(url=url, headers=headers).json()
        return data
    
    def fetch_account_xp(self) -> dict:
        '''
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        '''
        url=f"https://pd.{self.shard}.a.pvp.net/account-xp/v1/players/{self.puuid}"
        headers= {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def fetch_player_loadout(self) -> dict:
        '''
        playerLoadoutUpdate
        Get the player's current loadout
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/personalization/v2/players/{self.puuid}/playerloadout"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def put_player_loadout(self, loadout:dict) -> dict:
        '''
        playerLoadoutUpdate
        Use the values from client.fetch_player_loadout() excluding properties like subject and version. Loadout changes take effect when starting a new game
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/personalization/v2/players/{self.puuid}/playerloadout"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.put(url=url, headers=headers, json=loadout).json()
        return data

    def fetch_mmr(self, puuid:str=None) -> dict:
        '''
        MMR_FetchPlayer
        Get the match making rating for a player
        '''
        puuid = self.__check_puuid(puuid)
        url=f"https://pd.{self.shard}.a.pvp.net/mmr/v1/players/{puuid}"
        headers= {
            'X-Riot-Entitlements-JWT': self.en_token,
            'Authorization': self.authorization,
            'X-Riot-ClientVersion': self.__get_current_version(),
            'X-Riot-ClientPlatform': self.client_platform
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_match_history(self, start_index:int=0, end_index:int=15, queue_id:str="null", puuid:str=None) -> dict:
        '''
        MatchHistory_FetchMatchHistory
        Get recent matches for a player
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null, competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        '''
        puuid = self.__check_puuid(puuid)
        self.__check_queue_type(queue_id)
        url = f"https://pd.{self.shard}.a.pvp.net/match-history/v1/history/{puuid}?startIndex={start_index}&endIndex={end_index}" + (f"&queue={queue_id}" if queue_id != "null" else "")
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version(),
            "X-Riot-ClientPlatform": self.client_platform
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_match_details(self, match_id:str) -> dict:
        '''
        Get the full info for a previous match
        Includes everything that the in-game match details screen shows including damage and kill positions, same as the official API w/ a production key
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/match-details/v1/matches/{match_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version(),
            "X-Riot-ClientPlatform": self.client_platform
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_competitive_updates(self, start_index:int=0, end_index:int=15, queue_id:str="competitive", puuid:str=None) -> dict:
        '''
        MMR_FetchCompetitiveUpdates
        Get recent games and how they changed ranking
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null, competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        '''
        puuid = self.__check_puuid(puuid)
        self.__check_queue_type(queue_id)
        url = f"https://pd.{self.shard}.a.pvp.net/mmr/v1/players/{puuid}/competitiveupdates?startIndex={start_index}&endIndex={end_index}" + (f"&queue={queue_id}" if queue_id != "null" else "")
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientPlatform": self.client_platform
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_leaderboard(self, season:str, start_index:int=0, size:int=25, region:str="na") -> dict:
        '''
        MMR_FetchLeaderboard
        Get the competitive leaderboard for a given season
        The query parameter query can be added to search for a username.
        '''
        if season == "": season = self.__get_live_season()
        url = f"https://pd.{region}.a.pvp.net/mmr/v1/leaderboards/affinity/na/queue/competitive/season/{season}?startIndex={start_index}&size={size}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_player_restrictions(self) -> dict:
        '''
        Restrictions_FetchPlayerRestrictionsV2
        Checks for any gameplay penalties on the account
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/restrictions/v3/penalties"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_user_from_id(self, puuid:str = None) -> dict:
        '''
        Get username and tagline from puuid.
        '''
        puuid = self.__check_puuid(puuid)
        url = f"https://pd.{self.shard}.a.pvp.net/name-service/v2/players"
        headers = {
            "Authorization": self.authorization,
            "X-Riot-Entitlements-JWT": self.en_token,
            "X-Riot-ClientPlatform": self.client_platform,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.put(url=url, headers=headers, json=[puuid])

        return data.json()

    def fetch_item_progression_definitions(self) -> dict:
        '''
        ItemProgressionDefinitionsV2_Fetch
        Get details for item upgrades
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contract-definitions/v3/item-upgrades"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def fetch_config(self) -> dict:
        '''
        Config_FetchConfig
        Get various internal game configuration settings set by Riot
        '''
        url = f"https://shared.{self.shard}.a.pvp.net/v1/config/{self.shard}"
        data = requests.get(url=url).json()
        return data

    # store endpoints
    def store_fetch_offers(self) -> dict:
        '''
        Store_GetOffers
        Get prices for all store items
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/store/v1/offers/"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def store_fetch_storefront(self) -> dict:
        '''
        Store_GetStorefrontV2
        Get the currently available items in the store
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/store/v2/storefront/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def store_fetch_wallet(self) -> dict:
        '''
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7        
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/store/v1/wallet/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def store_fetch_order(self, order_id:str) -> dict:
        '''
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/store/v1/order/{order_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def store_fetch_entitlements(self, item_type:str="e7c63390-eda7-46e0-bb7a-a6abdacd2433") -> dict:
        '''
        Store_GetEntitlements
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in client.fetch_content() to know what items are owned

        NOTE: uuid to item type
        "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "skin_level",
        "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "skin_chroma",
        "01bb38e1-da47-4e6a-9b3d-945fe4655707": "agent",
        "f85cb6f7-33e5-4dc8-b609-ec7212301948": "contract_definition",
        "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "buddy",
        "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475": "spray",
        "3f296c07-64c3-494c-923b-fe692a4fa1bd": "player_card",
        "de7caa6b-adf7-4588-bbd1-143831e786c6": "player_title",
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/store/v1/entitlements/{self.puuid}/{item_type}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data


    # party endpoints
    def party_fetch_player(self) -> dict:
        '''
        Party_FetchPlayer
        Get the Party ID that a given player belongs to                
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/players/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def party_remove_player(self, puuid:str=None) -> None:
        '''
        Party_RemovePlayer
        Removes a player from the current party      
        '''
        puuid = self.__check_puuid(puuid)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/players/{puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.delete(url=url, headers=headers).json()
        return data

    def fetch_party(self) -> dict:
        '''
        Party_FetchParty
        Get details about a given party id    
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def party_set_member_ready(self, ready:bool) -> dict:
        '''
        Party_SetMemberReady
        Sets whether a party member is ready for queueing or not      
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/members/{self.puuid}/setReady"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers, json={"ready": ready}).json()
        return data 

    def party_refresh_competitive_tier(self) -> dict:
        '''
        Party_RefreshCompetitiveTier
        Refreshes the competitive tier for a player    
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/members/{self.puuid}/refreshCompetitiveTier"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers).json()
        return data

    def party_refresh_player_identity(self) -> dict:
        '''
        Party_RefreshPlayerIdentity
        Refreshes the identity for a player   
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/members/{self.puuid}/refreshPlayerIdentity"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers).json()
        return data

    def party_refresh_pings(self) -> dict:
        '''
        Party_RefreshPings
        Refreshes the pings for a player      
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/members/{self.puuid}/refreshPings"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers).json()
        return data

    def party_change_queue(self, queue_id:str) -> dict:
        '''
        Party_ChangeQueue
        Sets the matchmaking queue for the party 
        '''
        self.__check_queue_type(queue_id)
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/queue"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers, json={"queueID": queue_id}).json()
        return data 

    def party_start_custom_game(self) -> dict:
        '''
        Party_StartCustomGame
        Starts a custom game     
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/startcustomgame"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers).json()
        return data 

    def party_enter_matchmaking_queue(self) -> dict:
        '''
        Party_EnterMatchmakingQueue
        Enters the matchmaking queue
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/matchmaking/join"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers).json()
        return data 

    def party_leave_matchmaking_queue(self) -> dict:
        '''
        Party_LeaveMatchmakingQueue
        Leaves the matchmaking queue   
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/matchmaking/leave"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers).json()
        return data 

    def set_party_accessibility(self, open:bool) -> dict:
        '''
        Party_SetAccessibility
        Changes the party accessibility to be open or closed  
        '''
        state = "OPEN" if open else "CLOSED"
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/accessibility"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers, json={"accessibility":state}).json()
        return data

    def party_set_custom_game_settings(self, settings: dict) -> dict:
        '''
        Party_SetCustomGameSettings
        Changes the settings for a custom game

        settings:
        {
            "Map": "/Game/Maps/Triad/Triad", # map url
            "Mode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C", # url to gamemode
            "UseBots": true, # this isn't used anymore :(
            "GamePod": "aresriot.aws-rclusterprod-use1-1.na-gp-ashburn-awsedge-1", # server
            "GameRules": {
		            "AllowGameModifiers": "true/false",
		            "PlayOutAllRounds": "true/false",
		            "SkipMatchHistory": "true/false",
		            "TournamentMode": "true/false",
		            "IsOvertimeWinByTwo": "true/false"
	        }
        }
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/customgamesettings"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers, json=settings).json()
        return data
        
    def party_invite_by_display_name(self, name:str, tag:str) -> dict:
        '''
        Party_InviteToPartyByDisplayName
        Invites a player to the party with their display name

        omit the "#" in tag
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/invites/name/{name}/tag/{tag}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers).json()
        return data

    def party_request_to_join(self, party_id:str, other_puuid:str) -> dict:
        '''
        Party_RequestToJoinParty
        Requests to join a party
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/request"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers, json={"Subjects": other_puuid}).json()
        return data

    def party_decline_request(self, request_id:str) -> dict:
        '''
        Party_DeclineRequest
        Declines a party request

        {request id}: The ID of the party request. Can be found from the Requests array on the Party_FetchParty endpoint.
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/request/{request_id}/decline"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers).json()
        return data

    def party_join(self, party_id:str) -> dict:
        '''
        Party_PlayerJoin
        Join a party
        '''
        data = self.post(endpoint=f"/parties/v1/players/{self.puuid}/joinparty/{party_id}",endpoint_type="glz")
        return data 

    def party_leave(self, party_id:str) -> dict:
        '''
        Party_PlayerLeave
        Leave a party
        '''
        data = self.post(endpoint=f"/parties/v1/players/{self.puuid}/leaveparty/{party_id}",endpoint_type="glz")
        return data

    def party_fetch_custom_game_configs(self) -> dict:
        '''
        Party_FetchCustomGameConfigs
        Get information about the available gamemodes
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/customgameconfigs"
        headers = {
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def party_fetch_muc_token(self) -> dict:
        '''
        Party_FetchMUCToken
        Get a token for party chat
        '''
        party_id = self.__get_current_party_id()
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/muctoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def party_fetch_voice_token(self) -> dict:
        '''
        Party_FetchVoiceToken
        Get a token for party voice
        '''
        party_id = self.__get_current_party_id() 
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/parties/v1/parties/{party_id}/voicetoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 


    # live game endpoints
    def coregame_fetch_player(self) -> dict:
        '''
        CoreGame_FetchPlayer
        Get the game ID for an ongoing game the player is in        
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/players/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()

    def coregame_fetch_match(self, match_id:str=None) -> dict:
        '''
        CoreGame_FetchMatch
        Get information about an ongoing game      
        '''
        match_id = self.__coregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()

    def coregame_fetch_match_loadouts(self, match_id:str=None) -> dict:
        '''
        CoreGame_FetchMatchLoadouts
        Get player skins and sprays for an ongoing game     
        '''
        match_id = self.__coregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}/loadouts"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()
       
    def coregame_fetch_team_chat_muc_token(self,match_id:str=None) -> dict:
        '''
        CoreGame_FetchTeamChatMUCToken
        Get a token for team chat    
        '''
        match_id = self.__coregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}/teamchatmuctoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()

    def coregame_fetch_allchat_muc_token(self, match_id:str=None) -> dict:
        '''
        CoreGame_FetchAllChatMUCToken
        Get a token for all chat      
        '''
        match_id = self.__coregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}/allchatmuctoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()

    def coregame_disassociate_player(self,match_id:str=None) -> dict:
        '''
        CoreGame_DisassociatePlayer
        Leave an in-progress game    
        '''
        match_id = self.__coregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/core-game/v1/players/{self.puuid}/disassociate/{match_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a core-game")
        else:
            return data.json()

    
    # pregame endpoints
    def pregame_fetch_player(self) -> dict:
        '''
        Pregame_GetPlayer
        Get the ID of a game in the pre-game stage       
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/players/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json()

    def pregame_fetch_match(self, match_id:str=None) -> dict:
        '''
        Pregame_GetMatch
        Get info for a game in the pre-game stage       
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.tatus_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json()

    def pregame_fetch_match_loadouts(self, match_id:str=None) -> dict:
        '''
        Pregame_GetMatchLoadouts
        Get player skins and sprays for a game in the pre-game stage      
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/loadouts"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json()

    def pregame_fetch_chat_token(self,match_id:str=None) -> dict:
        '''
        Pregame_FetchChatToken
        Get a chat token     
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/chattoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json() 

    def pregame_fetch_voice_token(self,match_id:str=None) -> dict:
        '''
        Pregame_FetchVoiceToken
        Get a voice token      
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/voicetoken"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json() 

    def pregame_select_character(self, agent_id:str, match_id:str=None) -> dict:
        '''
        Pregame_SelectCharacter
        Select an agent

        don't use this for instalocking :)
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/select/{agent_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json() 

    def pregame_lock_character(self, agent_id:str, match_id:str=None) -> dict:
        '''
        Pregame_LockCharacter
        Lock in an agent

        don't use this for instalocking :)       
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/lock/{agent_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json() 

    def pregame_quit_match(self, match_id:str=None) -> dict:
        '''
        Pregame_QuitMatch
        Quit a match in the pre-game stage     
        '''
        match_id = self.__pregame_check_match_id(match_id)
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/pregame/v1/matches/{match_id}/quit"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.post(url=url, headers=headers)
        if data.status_code == 404:
            raise PhaseError("You are not in a pre-game")
        else:
            return data.json() 

    
    # contracts endpoints
    def contracts_fetch_definitions(self) -> dict:
        '''
        ContractDefinitions_Fetch
        Get names and descriptions for contracts        
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contract-definitions/v3/item-upgrades"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json
        return data 

    def contracts_fetch(self) -> dict:
        '''
        Contracts_Fetch
        Get a list of contracts and completion status including match history       
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contracts/v1/contracts/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.get(url=url, headers=headers).json
        return data 

    def contracts_activate(self, contract_id:str) -> dict:
        '''
        Contracts_Activate
        Activate a particular contract      

        {contract id}: The ID of the contract to activate. Can be found from the ContractDefinitions_Fetch endpoint.
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contracts/v1/contracts/{self.puuid}/special/{contract_id}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization,
            "X-Riot-ClientVersion": self.__get_current_version()
        }
        data = requests.post(url=url, headers=headers)
        return data 

    def contracts_fetch_active_story(self):
        '''
        ContractDefinitions_FetchActiveStory
        Get the battlepass contracts      
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contract-definitions/v2/definitions/story"
        headers =  {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def itemprogress_fetch_definitions(self) -> dict:
        '''
        ItemProgressDefinitionsV2_Fetch
        Fetch definitions for skin upgrade progressions
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contract-definitions/v3/item-upgrades"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def contracts_unlock_item_progress(self, progression_id:str) -> dict:
        '''
        Contracts_UnlockItemProgressV2
        Unlock an item progression
        '''
        url = f"https://pd.{self.shard}.a.pvp.net/contracts/v2/item-upgrades/{progression_id}/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    
    # session endpoints
    def session_fetch(self) -> dict:
        '''
        Session_Get
        Get information about the current game session     
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/session/v1/sessions/{self.puuid}"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 

    def session_reconnect(self) -> dict:
        '''
        Session_ReConnect
        '''
        url = f"https://glz-{self.shard}-1.{self.shard}.a.pvp.net/session/v1/sessions/{self.puuid}/reconnect"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data 


    # local riotclient endpoints
    def fetch_presence(self, puuid:str=None) -> dict:
        '''
        PRESENCE_RNet_GET
        NOTE: Only works on self or active user's friends
        '''
        puuid = self.__check_puuid(puuid)
        url = f"https://127.0.0.1:{self.local_port}/chat/v4/presences"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        try:
            for presence in data['presences']:
                if presence['puuid'] == puuid:
                    return json.loads(base64.b64decode(presence['private']))
        except:
            return None

    def fetch_all_friend_presences(self) -> dict:
        '''
        PRESENCE_RNet_GET_ALL
        Get a list of online friends and their activity
        private is a base64-encoded JSON string that contains useful information such as party and in-progress game score.
        '''
        url = f"https://127.0.0.1:{self.local_port}/chat/v4/presences"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def riotclient_session_fetch_sessions(self) -> dict:
        '''
        RiotClientSession_FetchSessions
        Gets info about the running Valorant process including start arguments
        '''
        url = f"https://127.0.0.1:{self.local_port}/product-session/v1/external-sessions"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def rnet_fetch_active_alias(self) -> dict:
        '''
        PlayerAlias_RNet_GetActiveAlias
        Gets the player username and tagline
        '''
        url = f"https://127.0.0.1:{self.local_port}/player-account/aliases/v1/active"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def rso_rnet_fetch_entitlements_token(self) -> dict:
        '''
        RSO_RNet_GetEntitlementsToken
        Gets both the token and entitlement for API usage
        accessToken is used as the token and token is used as the entitlement.
        PBE access can be checked through here
        '''
        url = f"https://127.0.0.1:{self.local_port}/player-account/aliases/v1/active"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def rnet_fetch_chat_session(self) -> dict:
        '''
        TEXT_CHAT_RNet_FetchSession
        Get the current session including player name and PUUID
        '''
        url = f"https://127.0.0.1:{self.local_port}/chat/v1/session"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def rnet_fetch_all_friends(self) -> dict:
        '''
        CHATFRIENDS_RNet_GET_ALL
        Get a list of friends     
        '''
        url = f"https://127.0.0.1:{self.local_port}/chat/v4/friends"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data

    def rnet_fetch_settings(self) -> dict:
        '''
        RiotKV_RNet_GetSettings
        Get client settings
        '''
        url = f"https://127.0.0.1:{self.local_port}/player-preferences/v1/data-json/Ares.PlayerSettings"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data
        
    def rnet_fetch_friend_requests(self) -> dict:
        '''
        FRIENDS_RNet_FetchFriendRequests
        Get pending friend requests       
        '''
        url = f"https://127.0.0.1:{self.local_port}/chat/v4/friendrequests"
        headers = {
            "X-Riot-Entitlements-JWT": self.en_token,
            "Authorization": self.authorization
        }
        data = requests.get(url=url, headers=headers).json()
        return data


    #Third-Party||Valorant API
    def fetch_version(self) -> dict:
        '''
        Returns data of the current manifest & version the API is running on
        '''
        data = requests.get(f'https://valorant-api.com/v1/version')
        return data.json()["data"]

    def fetch_weapons(self) -> dict:
        '''
        Returns data and assets of all weapons
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons")
        return data.json()["data"]

    def fetch_weapon_skins(self) -> dict:
        '''
        Returns data and assets of all weapon skins
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skins")
        return data.json()["data"]

    def fetch_weapon_skin_chromas(self) -> dict:
        '''
        Returns data and assets of all weapon skin chromas
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skinchromas")
        return data.json()["data"]

    def fetch_weapon_skin_levels(self) -> dict:
        '''
        Returns data and assets of all weapon skin levels
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels")
        return data.json()["data"]

    def fetch_weapon_by_uuid(self, weaponUuid) -> dict:
        '''
        Returns data and assets of the requeted weapon
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/{weaponUuid}")
        return data.json()["data"]

    def fetch_weapon_skin_by_uuid(self, weaponSkinUuid) -> dict:
        '''
        Returns data and assets of the requeted weapon skin
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skins/{weaponSkinUuid}")
        return data.json()["data"]

    def fetch_weapon_skin_chroma_by_uuid(self, weaponSkinChromaUuid) -> dict:
        '''
        Returns data and assets of the requeted weapon skin chroma
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skinchromas/{weaponSkinChromaUuid}")
        return data.json()["data"]

    def fetch_weapon_skin_level_by_uuid(self, weaponSkinLevelUuid) -> dict:
        '''
        Returns data and assets of the requeted weapon skin level
        '''
        data = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{weaponSkinLevelUuid}")
        return data.json()["data"]

    def fetch_themes(self) -> dict:
        '''
        Returns data and assets of all themes
        '''
        data = requests.get(f"https://valorant-api.com/v1/themes")
        return data.json()["data"]

    def fetch_themes_by_uuid(self, themeUuid) -> dict:
        '''
        Returns data and assets of the requested theme
        '''
        data = requests.get(f"https://valorant-api.com/v1/themes/{themeUuid}")
        return data.json()["data"]
    
    def fetch_sprays(self) -> dict:
        '''
        Returns data and assets of all sprays
        '''
        data = requests.get(f"https://valorant-api.com/v1/sprays")
        return data.json()["data"]

    def fetch_spray_levels(self) -> dict:
        '''
        Returns data and assets of all spray levels
        '''
        data = requests.get(f"https://valorant-api.com/v1/sprays/levels")
        return data.json()["data"]

    def fetch_spray_by_uuid(self, sprayUuid) -> dict:
        '''
        Returns data and assets of the requested spray
        '''
        data = requests.get(f"https://valorant-api.com/v1/sprays/{sprayUuid}")
        return data.json()["data"]

    def fetch_spray_level_by_uuid(self, sprayLevelUuid) -> dict:
        '''
        Returns data and assets of the requested spray level
        '''
        data = requests.get(f"https://valorant-api.com/v1/sprays/levels/{sprayLevelUuid}")
        return data.json()["data"]

    def fetch_seasons(self) -> dict:
        '''
        Returns data of all seasons
        '''
        data = requests.get(f"https://valorant-api.com/v1/seasons")
        return data.json()["data"]

    def fetch_competitive_seasons(self) -> dict:
        '''
        Returns data of all competitive seasons
        '''
        data = requests.get(f"https://valorant-api.com/v1/seasons/competitive")
        return data.json()["data"]
    
    def fetch_season_by_uuid(self, seasonUuid) -> dict:
        '''
        Returns data of the requested season
        '''
        data = requests.get(f"https://valorant-api.com/v1/seasons/{seasonUuid}")
        return data.json()["data"]

    def fetch_competitive_season_by_uuid(self, competitiveSeasonUuid) -> dict:
        '''
        Returns data of the requested competitive season
        '''
        data = requests.get(f"https://valorant-api.com/v1/seasons/competitive/{competitiveSeasonUuid}")
        return data.json()["data"]

    def fetch_player_titles(self) -> dict:
        '''
        Returns data of all player title
        '''
        data = requests.get(f"https://valorant-api.com/v1/playertitles")
        return data.json()["data"]

    def fetch_player_title_by_uuid(self, playertitleUuid) -> dict:
        '''
        Returns data of the requested player title
        '''
        data = requests.get(f"https://valorant-api.com/v1/playertitles/{playertitleUuid}")
        return data.json()["data"]

    def fetch_player_cards(self) -> dict:
        '''
        Returns data and assets of all player cards
        '''
        data = requests.get(f"https://valorant-api.com/v1/playercards")
        return data.json()["data"]

    def fetch_player_card_by_uuid(self, playercardUuid) -> dict:
        '''
        Returns data and assets of the requested player card
        '''
        data = requests.get(f"https://valorant-api.com/v1/playercards/{playercardUuid}")
        return data.json()["data"]

    def fetch_maps(self) -> dict:
        '''
        Returns data and assets of all maps
        '''
        data = requests.get(f"https://valorant-api.com/v1/maps")
        return data.json()["data"]

    def fetch_map_by_uuid(self, mapUuid) -> dict:
        '''
        Returns data and assets of the requested map
        '''
        data = requests.get(f"https://valorant-api.com/v1/maps/{mapUuid}")
        return data.json()["data"]

    def fetch_level_borders(self) -> dict:
        '''
        Returns data and assets of all level borders
        '''
        data = requests.get(f"https://valorant-api.com/v1/levelborders")
        return data.json()["data"]

    def fetch_level_border_by_uuid(self, levelborderUuid) -> dict:
        '''
        Returns data and assets of the requested level border
        '''
        data = requests.get(f"https://valorant-api.com/v1/levelborders/{levelborderUuid}")
        return data.json()["data"]

    def fetch_gear(self) -> dict:
        '''
        Returns data and assets of all gear
        '''
        data = requests.get(f"https://valorant-api.com/v1/gear")
        return data.json()["data"]

    def fetch_gear_by_uuid(self, gearUuid) -> dict:
        '''
        Returns data and assets of the requested gear
        '''
        data = requests.get(f"https://valorant-api.com/v1/gear/{gearUuid}")
        return data.json()["data"]

    def fetch_gamemodes(self) -> dict:
        '''
        Returns data and assets of all gamemodes
        '''
        data = requests.get(f"https://valorant-api.com/v1/gamemodes")
        return data.json()["data"]

    def fetch_gamemode_equippables(self) -> dict:
        '''
        Returns data and assets of the requested player card
        '''
        data = requests.get(f"https://valorant-api.com/v1/gamemodes/equippables")
        return data.json()["data"]

    def fetch_gamemode_by_uuid(self, gamemodeUuid) -> dict:
        '''
        Returns data and assets of the requested gamemode
        '''
        data = requests.get(f"https://valorant-api.com/v1/gamemodes/{gamemodeUuid}")
        return data.json()["data"]

    def fetch_gamemode_equippable_by_uuid(self, gamemodeequippableUuid) -> dict:
        '''
        Returns data and assets of the requested gamemode equippable
        '''
        data = requests.get(f"https://valorant-api.com/v1/gamemodes/equippables/{gamemodeequippableUuid}")
        return data.json()["data"]

    def fetch_events(self) -> dict:
        '''
        Returns data and assets of all events
        '''
        data = requests.get(f"https://valorant-api.com/v1/events")
        return data.json()["data"]

    def fetch_event_by_uuid(self, eventUuid) -> dict:
        '''
        Returns data and assets the requested event
        '''
        data = requests.get(f"https://valorant-api.com/v1/events/{eventUuid}")
        return data.json()["data"]

    def fetch_currencies(self) -> dict:
        '''
        Returns data and assets of all in-game currencies
        '''
        data = requests.get(f"https://valorant-api.com/v1/currencies")
        return data.json()["data"]

    def fetch_currency_by_uuid(self, currencyUuid) -> dict:
        '''
        Returns data and assets the requested in-game currency
        '''
        data = requests.get(f"https://valorant-api.com/v1/currencies/{currencyUuid}")
        return data.json()["data"]

    def fetch_contracts(self) -> dict:
        '''
        Returns data and assets of all contracts
        '''
        data = requests.get(f"https://valorant-api.com/v1/contracts")
        return data.json()["data"]

    def fetch_contract_by_uuid(self, contractUuid) -> dict:
        '''
        Returns data and assets the requested contract
        '''
        data = requests.get(f"https://valorant-api.com/v1/contracts/{contractUuid}")
        return data.json()["data"]

    def fetch_content_tier(self) -> dict:
        '''
        Returns data and assets of all content tiers
        '''
        data = requests.get(f"https://valorant-api.com/v1/contenttiers")
        return data.json()["data"]

    def fetch_content_tier_by_uuid(self, contenttierUuid) -> dict:
        '''
        Returns data and assets the requested content tier
        '''
        data = requests.get(f"https://valorant-api.com/v1/contenttiers/{contenttierUuid}")
        return data.json()["data"]

    def fetch_competitive_tiers(self) -> dict:
        '''
        Returns data and assets of all competitive tiers
        '''
        data = requests.get(f"https://valorant-api.com/v1/competitivetiers")
        return data.json()["data"]

    def fetch_competitive_tier_by_uuid(self, competitivetierUuid) -> dict:
        '''
        Returns data and assets the requested competitive tier table
        '''
        data = requests.get(f"https://valorant-api.com/v1/competitivetiers/{competitivetierUuid}")
        return data.json()["data"]

    def fetch_ceremonies(self) -> dict:
        '''
        Returns data and assets of all ceremonies
        '''
        data = requests.get(f"https://valorant-api.com/v1/ceremonies")
        return data.json()["data"]

    def fetch_ceremony_by_uuid(self, ceremoniesUuid) -> dict:
        '''
        Returns data and assets of the requested ceremony
        '''
        data = requests.get(f"https://valorant-api.com/v1/ceremonies/{ceremoniesUuid}")
        return data.json()["data"]

    def fetch_bundles(self) -> dict:
        '''
        Returns data and assets of all bundles
        '''
        data = requests.get(f"https://valorant-api.com/v1/bundles")
        return data.json()["data"]

    def fetch_bundle_by_uuid(self, bundleUuid) -> dict:
        '''
        Returns data and assets of the requested bundle
        '''
        data = requests.get(f"https://valorant-api.com/v1/bundles/{bundleUuid}")
        return data.json()["data"]

    def fetch_buddies(self) -> dict:
        '''
        Returns data and assets of all weapon buddies
        '''
        data = requests.get(f"https://valorant-api.com/v1/buddies")
        return data.json()["data"]

    def fetch_buddy_level(self) -> dict:
        '''
        Returns data and assets of all weapon buddy levels
        '''
        data = requests.get(f"https://valorant-api.com/v1/buddies/levels")
        return data.json()["data"]

    def fetch_buddy_by_uuid(self, buddyUuid) -> dict:
        '''
        Returns data and assets of the requested weapon buddy
        '''
        data = requests.get(f"https://valorant-api.com/v1/buddies/{buddyUuid}")
        return data.json()["data"]

    def fetch_buddy_level_by_uuid(self, buddyLevelUuid) -> dict:
        '''
        Returns data and assets of the requested weapon buddy level
        '''
        data = requests.get(f"https://valorant-api.com/v1/buddies/levels/{buddyLevelUuid}")
        return data.json()["data"]

    def fetch_agents(self) -> dict:
        '''
        Returns data and assets of all agents and their abilities
        Info: Yes, there are 2 Sovas. Use the isPlayableCharacter=true filter to make sure you don't have a "duplicate" Sova.
        '''
        data = requests.get(f"https://valorant-api.com/v1/agents")
        return data.json()["data"]

    def fetch_agent_by_uuid(self, agentUuid) -> dict:
        '''
        Returns data and assets of the requested agent
        '''
        data = requests.get(f"https://valorant-api.com/v1/agents/{agentUuid}")
        return data.json()["data"]

    # local utility functions
    def __get_live_season(self) -> str:
        '''Get the UUID of the live competitive season'''
        return self.fetch_mmr()["LatestCompetitiveUpdate"]["SeasonID"]

    def __check_puuid(self, puuid) -> str:
        '''If puuid passed into method is None make it current user's puuid'''
        return self.puuid if puuid is None else puuid

    def __check_party_id(self, party_id) -> str:
        '''If party ID passed into method is None make it user's current party'''
        return self.__get_current_party_id() if party_id is None else party_id

    def __get_current_party_id(self) -> str:
        '''Get the user's current party ID'''
        party = self.party_fetch_player()
        return party["CurrentPartyID"]

    def __coregame_check_match_id(self, match_id) -> str:
        '''Check if a match id was passed into the method'''
        return self.coregame_fetch_player()["MatchID"] if match_id is None else match_id

    def __pregame_check_match_id(self, match_id) -> str:
        return self.pregame_fetch_player()["MatchID"] if match_id is None else match_id


    def __check_queue_type(self, queue_id) -> None:
        '''Check if queue id is valid'''
        if queue_id not in queues:
            raise ValueError("Invalid queue type")

    def __get_headers(self) -> dict:
        '''Get authorization headers to make requests'''
        try:
            if self.auth is None:
                return self.__get_auth_headers()
            puuid, headers, _ = self.auth.authenticate()
            headers['X-Riot-ClientPlatform'] = self.client_platform,
            headers['X-Riot-ClientVersion'] = self.__get_current_version()
            return puuid, headers, None

        except Exception as e:
            print(e)
            raise HandshakeError('Unable to get headers; is VALORANT running?')

    def __get_auth_headers(self): # headers for pd/glz endpoints
        local_headers = {
            'Authorization': (
                'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
            )
        }
        response = requests.get("https://127.0.0.1:{port}/entitlements/v1/token".format(
            port=self.lockfile['port']),
            headers=local_headers,
            verify=False
        )
        entitlements = response.json()
        puuid = entitlements['subject']
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token'],
            'X-Riot-ClientPlatform': self.client_platform,
            'X-Riot-ClientVersion': self.__get_current_version()
        }
        return puuid, headers, local_headers

    def __get_current_version(self) -> str:
        data = requests.get('https://valorant-api.com/v1/version')
        data = data.json()['data']['riotClientVersion']
        return data

    def __get_lockfile(self) -> dict:
        try:
            with open(self.lockfile_path) as lockfile:
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                return dict(zip(keys, data))
        except:
            raise LockfileError("Lockfile not found")