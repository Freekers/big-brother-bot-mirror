#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2011 Courgette
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import re
import unittest2 as unittest
from mock import Mock, DEFAULT, patch, call
from mockito import when, verify
import b3
from b3.clients import Client, Clients
from b3.fake import FakeClient
from b3.parsers.bf4 import Bf4Parser, MAP_NAME_BY_ID, GAME_MODES_BY_MAP_ID, GAME_MODES_NAMES
from b3.config import XmlConfigParser, CfgConfigParser
from b3.parsers.frostbite2.protocol import CommandFailedError
from b3.parsers.frostbite2.util import MapListBlock
from b3.plugins.admin import AdminPlugin
from tests import logging_disabled


sleep_patcher = None
def setUpModule():
    sleep_patcher = patch("time.sleep")
    sleep_patcher.start()


# make sure to unpatch core B3 stuf
original_getByMagic = Clients.getByMagic
original_message = Client.message
original_disconnect = Clients.disconnect
def tearDownModule():
    Clients.getByMagic = original_getByMagic
    Client.message = original_message
    Clients.disconnect = original_disconnect
    if hasattr(Client, "messagequeueworker"):
        del Client.messagequeueworker
    if sleep_patcher:
        sleep_patcher.stop()


class BF4TestCase(unittest.TestCase):
    """
    Test case that is suitable for testing BF3 parser specific features
    """

    @classmethod
    def setUpClass(cls):
        from b3.parsers.frostbite2.abstractParser import AbstractParser
        from b3.fake import FakeConsole
        AbstractParser.__bases__ = (FakeConsole,)
        # Now parser inheritance hierarchy is :
        # BF4Parser -> AbstractParser -> FakeConsole -> Parser

    def tearDown(self):
        if hasattr(self, "parser"):
            del self.parser.clients
            self.parser.working = False



class Test_getServerInfo(unittest.TestCase):

    def test_decodeServerinfo_R2(self):
        self.maxDiff = None
        self.assertDictEqual({
            'serverName': 'BigBrotherBot #2',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'ConquestLarge0',
            'level': 'MP_012',
            'roundsPlayed': '0',
            'roundsTotal': '2',
            'numTeams': '0',
            'team1score': None,
            'team2score': None,
            'team3score': None,
            'team4score': None,
            'targetScore': '0',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '5148',
            'roundTime': '455',
            'gameIpAndPort': '1.2.3.4:5445',
            'punkBusterVersion': '1.5',
            'joinQueueEnabled': 'false',
            'region': 'EU',
            'closestPingSite': '45',
            'country': 'FR',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME'
        }, Bf4Parser.decodeServerinfo(('BigBrotherBot #2', '0', '16', 'ConquestLarge0', 'MP_012', '0', '2', '0', '0', '', 'true', 'true', 'false', '5148', '455', '1.2.3.4:5445', '1.5', 'false', 'EU', '45', 'FR', '0', 'IN_GAME')))

        self.assertDictEqual({
            'serverName': 'BigBrotherBot #2',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'ConquestLarge0',
            'level': 'MP_012',
            'roundsPlayed': '0',
            'roundsTotal': '2',
            'numTeams': '1',
            'team1score': '47',
            'team2score': None,
            'team3score': None,
            'team4score': None,
            'targetScore': '0',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '5148',
            'roundTime': '455',
            'gameIpAndPort': '1.2.3.4:5445',
            'punkBusterVersion': '1.5',
            'joinQueueEnabled': 'false',
            'region': 'EU',
            'closestPingSite': '45',
            'country': 'FR',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME'
        }, Bf4Parser.decodeServerinfo(('BigBrotherBot #2', '0', '16', 'ConquestLarge0', 'MP_012', '0', '2', '1', '47', '0', '', 'true', 'true', 'false', '5148', '455', '1.2.3.4:5445', '1.5', 'false', 'EU', '45', 'FR', '0', 'IN_GAME')))

        self.assertDictEqual({
            'serverName': 'BigBrotherBot #2',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'ConquestLarge0',
            'level': 'MP_012',
            'roundsPlayed': '0',
            'roundsTotal': '2',
            'numTeams': '2',
            'team1score': '300',
            'team2score': '300',
            'team3score': None,
            'team4score': None,
            'targetScore': '0',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '5148',
            'roundTime': '455',
            'gameIpAndPort': '1.2.3.4:5445',
            'punkBusterVersion': '1.5',
            'joinQueueEnabled': 'false',
            'region': 'EU',
            'closestPingSite': '45',
            'country': 'FR',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME'
        }, Bf4Parser.decodeServerinfo(('BigBrotherBot #2', '0', '16', 'ConquestLarge0', 'MP_012', '0', '2', '2', '300', '300', '0', '', 'true', 'true', 'false', '5148', '455', '1.2.3.4:5445', '1.5', 'false', 'EU', '45', 'FR', '0', 'IN_GAME')))

        self.assertDictEqual({
            'serverName': 'BigBrotherBot #2',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'ConquestLarge0',
            'level': 'MP_012',
            'roundsPlayed': '1',
            'roundsTotal': '2',
            'numTeams': '3',
            'team1score': '300',
            'team2score': '215',
            'team3score': '25',
            'team4score': None,
            'targetScore': '0',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '5148',
            'roundTime': '455',
            'gameIpAndPort': '1.2.3.4:5445',
            'punkBusterVersion': '1.5',
            'joinQueueEnabled': 'false',
            'region': 'EU',
            'closestPingSite': '45',
            'country': 'FR',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME',
        }, Bf4Parser.decodeServerinfo(('BigBrotherBot #2', '0', '16', 'ConquestLarge0', 'MP_012', '1', '2', '3', '300', '215', '25', '0', '', 'true', 'true', 'false', '5148', '455', '1.2.3.4:5445', '1.5', 'false', 'EU', '45', 'FR', '0', 'IN_GAME')))

        self.assertDictEqual({
            'serverName': 'BigBrotherBot #2',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'ConquestLarge0',
            'level': 'MP_012',
            'roundsPlayed': '1',
            'roundsTotal': '2',
            'numTeams': '4',
            'team1score': '300',
            'team2score': '215',
            'team3score': '25',
            'team4score': '84',
            'targetScore': '0',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '5148',
            'roundTime': '455',
            'gameIpAndPort': '1.2.3.4:5445',
            'punkBusterVersion': '1.5',
            'joinQueueEnabled': 'false',
            'region': 'EU',
            'closestPingSite': '45',
            'country': 'FR',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME',
        }, Bf4Parser.decodeServerinfo(('BigBrotherBot #2', '0', '16', 'ConquestLarge0', 'MP_012', '1', '2', '4', '300', '215', '25', '84', '0', '', 'true', 'true', 'false', '5148', '455', '1.2.3.4:5445', '1.5', 'false', 'EU', '45', 'FR', '0', 'IN_GAME')))

    def test_getServerInfo_R2(self):

        bf4_response = ['i3D.net - BigBrotherBot #3 (FR)', '0', '16', 'SquadDeathMatch0', 'MP_013',
                        '0', '1','4', '0', '0', '0', '0', '50', '', 'true', 'true', 'false', '92480',
                        '4832', '4.5.6.7:542', '', '', 'EU', 'ams', 'DE', '0', 'IN_GAME']
        parser = Mock(spec=Bf4Parser)
        parser.write = lambda x: bf4_response

        data = Bf4Parser.getServerInfo(parser)
        self.assertEqual(bf4_response, data)
        self.assertEqual(parser.game.sv_hostname, 'i3D.net - BigBrotherBot #3 (FR)')
        self.assertEqual(parser.game.sv_maxclients, 16)
        self.assertEqual(parser.game.gameType, 'SquadDeathMatch0')
        self.assertEqual(parser._publicIp, '4.5.6.7')
        self.assertEqual(parser._gamePort, '542')
        self.assertEqual({
            'serverName': 'i3D.net - BigBrotherBot #3 (FR)',
            'numPlayers': '0',
            'maxPlayers': '16',
            'gamemode': 'SquadDeathMatch0',
            'level': 'MP_013',
            'roundsPlayed': '0',
            'roundsTotal': '1',
            'numTeams': '4',
            'team1score': '0',
            'team2score': '0',
            'team3score': '0',
            'team4score': '0',
            'targetScore': '50',
            'onlineState': '',
            'isRanked': 'true',
            'hasPunkbuster': 'true',
            'hasPassword': 'false',
            'serverUptime': '92480',
            'roundTime': '4832',
            'gameIpAndPort': '4.5.6.7:542',
            'punkBusterVersion': '',
            'joinQueueEnabled': '',
            'region': 'EU',
            'closestPingSite': 'ams',
            'country': 'DE',
            'blazePlayerCount': '0',
            'blazeGameState': 'IN_GAME'
        }, parser.game.serverinfo)



class Test_bf3_events(BF4TestCase):

    def setUp(self):
        self.conf = XmlConfigParser()
        self.conf.loadFromString("""
                <configuration>
                </configuration>
            """)
        self.parser = Bf4Parser(self.conf)
        self.parser.startup()
        # mock parser queueEvent method so we can make assertions on it later on
        self.parser.queueEvent = Mock(name="queueEvent method")
        self.joe = Mock(name="Joe", spec=Client)

    def test_cmd_rotateMap_generates_EVT_GAME_ROUND_END(self):
        # prepare fake BF3 server responses
        def fake_write(data):
            if data ==  ('mapList.getMapIndices', ):
                return [0, 1]
            else:
                return []
        self.parser.write = Mock(side_effect=fake_write)
        self.parser.getFullMapRotationList = Mock(return_value=MapListBlock(['4', '3', 'MP_007', 'RushLarge0', '4', 'MP_011', 'RushLarge0', '4', 'MP_012',
                                                                             'SquadRush0', '4', 'MP_013', 'SquadRush0', '4']))
        self.parser.rotateMap()
        self.assertEqual(1, self.parser.queueEvent.call_count)
        self.assertEqual(self.parser.getEventID("EVT_GAME_ROUND_END"), self.parser.queueEvent.call_args[0][0].type)
        self.assertIsNone(self.parser.queueEvent.call_args[0][0].data)


    def test_player_onChat_event_all(self):
        self.parser.getClient = Mock(return_value=self.joe)

        self.parser.routeFrostbitePacket(['player.onChat', 'Cucurbitaceae', 'test all', 'all'])
        self.assertEqual(1, self.parser.queueEvent.call_count)

        event = self.parser.queueEvent.call_args[0][0]
        self.assertEqual("Say", self.parser.getEventName(event.type))
        self.assertEquals('test all', event.data)
        self.assertEqual(self.joe, event.client)


    def test_player_onChat_event_team(self):
        self.parser.getClient = Mock(return_value=self.joe)

        self.parser.routeFrostbitePacket(['player.onChat', 'Cucurbitaceae', 'test team', 'team', '1'])
        self.assertEqual(1, self.parser.queueEvent.call_count)

        event = self.parser.queueEvent.call_args[0][0]
        self.assertEqual("Team Say", self.parser.getEventName(event.type))
        self.assertEquals('test team', event.data)
        self.assertEqual(self.joe, event.client)


    def test_player_onChat_event_squad(self):
        self.parser.getClient = Mock(return_value=self.joe)

        self.parser.routeFrostbitePacket(['player.onChat', 'Cucurbitaceae', 'test squad', 'squad', '1', '1'])
        self.assertEqual(1, self.parser.queueEvent.call_count)

        event = self.parser.queueEvent.call_args[0][0]
        self.assertEqual("Squad Say", self.parser.getEventName(event.type))
        self.assertEquals('test squad', event.data)
        self.assertEqual(self.joe, event.client)

    def test_player_onChat_event_squad_comrose(self):
        self.parser.getClient = Mock(return_value=self.joe)

        self.parser.routeFrostbitePacket(['player.onChat', 'Cucurbitaceae', 'ID_CHAT_REQUEST_RIDE', 'squad', '1', '1'])
        self.assertEqual(1, self.parser.queueEvent.call_count)

        event = self.parser.queueEvent.call_args[0][0]
        self.assertEqual("Client Comrose", self.parser.getEventName(event.type))
        self.assertEquals('ID_CHAT_REQUEST_RIDE', event.data)
        self.assertEqual(self.joe, event.client)

    def test_player_onChat_event_team_comrose(self):
        self.parser.getClient = Mock(return_value=self.joe)

        self.parser.routeFrostbitePacket(['player.onChat', 'Cucurbitaceae', 'ID_CHAT_THANKS', 'team', '1', ])
        self.assertEqual(1, self.parser.queueEvent.call_count)

        event = self.parser.queueEvent.call_args[0][0]
        self.assertEqual("Client Comrose", self.parser.getEventName(event.type))
        self.assertEquals('ID_CHAT_THANKS', event.data)
        self.assertEqual(self.joe, event.client)

class Test_punkbuster_events(BF4TestCase):

    def setUp(self):
        self.conf = XmlConfigParser()
        self.conf.loadFromString("""
                <configuration>
                </configuration>
            """)
        self.parser = Bf4Parser(self.conf)
        self.parser.startup()

    def pb(self, msg):
        return self.parser.OnPunkbusterMessage(action=None, data=[msg])

    def assert_pb_misc_evt(self, msg):
        assert str(self.pb(msg)).startswith('Event<EVT_PUNKBUSTER_MISC>')

    def test_PB_SV_BanList(self):
        self.assert_pb_misc_evt('PunkBuster Server: 1   b59ffffffffffffffffffffffffffc7d {13/15} "Cucurbitaceae" "87.45.14.2:3659" retest" ""')
        self.assert_pb_misc_evt('PunkBuster Server: 1   b59ffffffffffffffffffffffffffc7d {0/1440} "Cucurbitaceae" "87.45.14.2:3659" mlkjsqfd" ""')

        self.assertEquals(
            '''Event<EVT_PUNKBUSTER_UNKNOWN>(['PunkBuster Server: 1   (UnBanned) b59ffffffffffffffffffffffffffc7d {15/15} "Cucurbitaceae" "87.45.14.2:3659" retest" ""'], None, None)''',
            str(self.pb('PunkBuster Server: 1   (UnBanned) b59ffffffffffffffffffffffffffc7d {15/15} "Cucurbitaceae" "87.45.14.2:3659" retest" ""')))

        self.assert_pb_misc_evt('PunkBuster Server: Guid=b59ffffffffffffffffffffffffffc7d" Not Found in the Ban List')
        self.assert_pb_misc_evt('PunkBuster Server: End of Ban List (1 of 1 displayed)')

    def test_PB_UCON_message(self):
        result = self.pb('PunkBuster Server: PB UCON "ggc_85.214.107.154"@85.214.107.154:14516 [admin.say "GGC-Stream.com - Welcome Cucurbitaceae with the GUID 31077c7d to our server." all]\n')
        self.assertEqual('Event<EVT_PUNKBUSTER_UCON>({\'ip\': \'85.214.107.154\', \'cmd\': \'admin.say "GGC-Stream.com - Welcome Cucurbitaceae with the GUID 31077c7d to our server." all\', \'from\': \'ggc_85.214.107.154\', \'port\': \'14516\'}, None, None)', str(result))

    def test_PB_Screenshot_received_message(self):
        result = self.pb('PunkBuster Server: Screenshot C:\\games\\bf3\\173_199_73_213_25200\\862147\\bf3\\pb\\svss\\pb000709.png successfully received (MD5=4576546546546546546546546543E1E1) from 19 Jaffar [da876546546546546546546546547673(-) 111.22.33.111:3659]\n')
        self.assertEqual(r"Event<EVT_PUNKBUSTER_SCREENSHOT_RECEIVED>({'slot': '19', 'name': 'Jaffar', 'ip': '111.22.33.111', 'pbid': 'da876546546546546546546546547673', 'imgpath': 'C:\\games\\bf3\\173_199_73_213_25200\\862147\\bf3\\pb\\svss\\pb000709.png', 'port': '3659', 'md5': '4576546546546546546546546543E1E1'}, None, None)", str(result))

    def test_PB_SV_PList(self):
        self.assert_pb_misc_evt("PunkBuster Server: Player List: [Slot #] [GUID] [Address] [Status] [Power] [Auth Rate] [Recent SS] [O/S] [Name]")
        self.assert_pb_misc_evt('PunkBuster Server: End of Player List (0 Players)')

    def test_PB_Ver(self):
        self.assertIsNone(self.pb('PunkBuster Server: PunkBuster Server for BF3 (v1.839 | A1386 C2.279) Enabled\n'))

    def test_PB_SV_BanGuid(self):
        self.assert_pb_misc_evt('PunkBuster Server: Ban Added to Ban List')
        self.assert_pb_misc_evt('PunkBuster Server: Ban Failed')

    def test_PB_SV_UnBanGuid(self):
        self.assert_pb_misc_evt('PunkBuster Server: Guid b59f190e5ef725e06531387231077c7d has been Unbanned')

    def test_PB_SV_UpdBanFile(self):
        self.assert_pb_misc_evt("PunkBuster Server: 0 Ban Records Updated in d:\\localuser\\g119142\\pb\\pbbans.dat")

    def test_misc(self):
        self.assertEqual("Event<EVT_PUNKBUSTER_LOST_PLAYER>({'slot': '1', 'ip': 'x.x.x.x', 'port': '3659', 'name': 'joe', 'pbuid': '0837c128293d42aaaaaaaaaaaaaaaaa'}, None, None)",
            str(self.pb("PunkBuster Server: Lost Connection (slot #1) x.x.x.x:3659 0837c128293d42aaaaaaaaaaaaaaaaa(-) joe")))

        self.assert_pb_misc_evt("PunkBuster Server: Invalid Player Specified: None")
        self.assert_pb_misc_evt("PunkBuster Server: Matched: Cucurbitaceae (slot #1)")
        self.assert_pb_misc_evt("PunkBuster Server: Received Master Security Information")
        self.assert_pb_misc_evt("PunkBuster Server: Auto Screenshot 000714 Requested from 25 Goldbat")


class Test_bf3_sends_no_guid(BF4TestCase):
    """
    See bug https://github.com/courgette/big-brother-bot/issues/69
    """
    def setUp(self):
        BF4TestCase.setUp(self)
        self.conf = XmlConfigParser()
        self.conf.loadFromString("<configuration/>")
        self.parser = Bf4Parser(self.conf)
        self.parser.startup()

        self.authorizeClients_patcher = patch.object(self.parser.clients, "authorizeClients")
        self.authorizeClients_patcher.start()

        self.write_patcher = patch.object(self.parser, "write")
        self.write_mock = self.write_patcher.start()

        self.event_raw_data = 'PunkBuster Server: 14 300000aaaaaabbbbbbccccc111223300(-) 11.122.103.24:3659 OK   1 3.0 0 (W) "Snoopy"'
        self.regex_for_OnPBPlistItem = [x for (x, y) in self.parser._punkbusterMessageFormats if y == 'OnPBPlistItem'][0]


    def tearDown(self):
        BF4TestCase.tearDown(self)
        self.authorizeClients_patcher.stop()
        self.write_mock = self.write_patcher.stop()


    def test_auth_client_without_guid_but_with_known_pbid(self):
        # GIVEN

        # known superadmin named Snoopy
        superadmin = Client(console=self.parser, name='Snoopy', guid='EA_AAAAAAAABBBBBBBBBBBBBB00000000000012222', pbid='300000aaaaaabbbbbbccccc111223300', group_bits=128, connections=21)
        superadmin.save()

        # bf3 server failing to provide guid
        def write(data):
            if data == ('admin.listPlayers', 'player', 'Snoopy'):
                return ['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', '1', 'Snoopy', '', '2', '8', '0', '0', '0']
            else:
                return DEFAULT
        self.write_mock.side_effect = write

        # WHEN
        self.assertFalse('Snoopy' in self.parser.clients)
        self.parser.OnPBPlayerGuid(match=re.match(self.regex_for_OnPBPlistItem, self.event_raw_data), data=self.event_raw_data)

        # THEN
        # B3 should have authed Snoopy
        self.assertTrue('Snoopy' in self.parser.clients)
        snoopy = self.parser.clients['Snoopy']
        self.assertTrue(snoopy.authed)
        for attb in ('name', 'pbid', 'guid', 'groupBits'):
            self.assertEqual(getattr(superadmin, attb), getattr(snoopy, attb))



    def test_does_not_auth_client_without_guid_and_unknown_pbid(self):
        # GIVEN
        # bf3 server failing to provide guid
        def write(data):
            if data == ('admin.listPlayers', 'player', 'Snoopy'):
                return ['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', '1', 'Snoopy', '', '2', '8', '0', '0', '0']
            else:
                return DEFAULT
        self.write_mock.side_effect = write

        # WHEN
        self.assertFalse('Snoopy' in self.parser.clients)
        self.parser.OnPBPlayerGuid(match=re.match(self.regex_for_OnPBPlistItem, self.event_raw_data), data=self.event_raw_data)

        # THEN
        # B3 should have authed Snoopy
        self.assertTrue('Snoopy' in self.parser.clients)
        snoopy = self.parser.clients['Snoopy']
        self.assertFalse(snoopy.authed)



class Test_bf3_maps(BF4TestCase):

    def setUp(self):
        BF4TestCase.setUp(self)
        self.conf = XmlConfigParser()
        self.conf.loadFromString("""
                <configuration>
                </configuration>
            """)
        self.parser = Bf4Parser(self.conf)


    def test_each_map_has_at_least_one_gamemode(self):
        for map_id in MAP_NAME_BY_ID:
            self.assertIn(map_id, GAME_MODES_BY_MAP_ID)
            self.assertGreater(len(GAME_MODES_BY_MAP_ID[map_id]), 0)


    def test_each_gamemode_is_valid(self):
        game_modes_found = set()
        map(game_modes_found.update, GAME_MODES_BY_MAP_ID.values())
        self.assertSetEqual(set(GAME_MODES_NAMES.keys()), game_modes_found)
        for game_mode in game_modes_found:
            self.assertIn(game_mode, GAME_MODES_NAMES)


    def test_getEasyName(self):
        self.assertEqual('Zavod 311', self.parser.getEasyName('MP_Abandoned'))
        self.assertEqual('Lancang Dam', self.parser.getEasyName('MP_Damage'))
        self.assertEqual('Flood Zone', self.parser.getEasyName('MP_Flooded'))
        self.assertEqual('Golmud Railway', self.parser.getEasyName('MP_Journey'))
        self.assertEqual('Paracel Storm', self.parser.getEasyName('MP_Naval'))
        self.assertEqual('Operation Locker', self.parser.getEasyName('MP_Prison'))
        self.assertEqual('Hainan Resort', self.parser.getEasyName('MP_Resort'))
        self.assertEqual('Siege of Shanghai', self.parser.getEasyName('MP_Siege'))
        self.assertEqual('Rogue Transmission', self.parser.getEasyName('MP_TheDish'))
        self.assertEqual('Dawnbreaker', self.parser.getEasyName('MP_Tremors'))
        self.assertEqual('f00', self.parser.getEasyName('f00'))


    def test_getHardName(self):
        self.assertEqual('MP_Abandoned', self.parser.getHardName('Zavod 311'))
        self.assertEqual('MP_Damage', self.parser.getHardName('Lancang Dam'))
        self.assertEqual('MP_Flooded', self.parser.getHardName('Flood Zone'))
        self.assertEqual('MP_Journey', self.parser.getHardName('Golmud Railway'))
        self.assertEqual('MP_Naval', self.parser.getHardName('Paracel Storm'))
        self.assertEqual('MP_Prison', self.parser.getHardName('Operation Locker'))
        self.assertEqual('MP_Resort', self.parser.getHardName('Hainan Resort'))
        self.assertEqual('MP_Siege', self.parser.getHardName('Siege of Shanghai'))
        self.assertEqual('MP_TheDish', self.parser.getHardName('Rogue Transmission'))
        self.assertEqual('MP_Tremors', self.parser.getHardName('Dawnbreaker'))
        self.assertEqual('f00', self.parser.getHardName('f00'))


    def test_getMapsSoundingLike(self):
        self.assertEqual(['dragon pass', 'lancang dam', 'operation locker', ], self.parser.getMapsSoundingLike(''), '')
        self.assertEqual('MP_Abandoned', self.parser.getMapsSoundingLike('Zavod 311'), 'Zavod 311')
        self.assertEqual('MP_Tremors', self.parser.getMapsSoundingLike('dawn'))
        #self.assertEqual(['operation metro', 'operation firestorm', 'operation 925'], self.parser.getMapsSoundingLike('operation'))

        self.assertEqual('MP_Abandoned', self.parser.getMapsSoundingLike('zavod'))
        self.assertEqual('MP_Abandoned', self.parser.getMapsSoundingLike('311'))
        self.assertEqual('MP_Abandoned', self.parser.getMapsSoundingLike('Zavod 311'))
        self.assertEqual('MP_Damage', self.parser.getMapsSoundingLike('lancang'))
        self.assertEqual('MP_Damage', self.parser.getMapsSoundingLike('dam'))
        self.assertEqual('MP_Damage', self.parser.getMapsSoundingLike('Lancang Dam'))
        self.assertEqual('MP_Flooded', self.parser.getMapsSoundingLike('flood'))
        self.assertEqual('MP_Flooded', self.parser.getMapsSoundingLike('zone'))
        self.assertEqual('MP_Flooded', self.parser.getMapsSoundingLike('Flood Zone'))
        self.assertEqual('MP_Journey', self.parser.getMapsSoundingLike('golmud'))
        self.assertEqual('MP_Journey', self.parser.getMapsSoundingLike('railway'))
        self.assertEqual('MP_Journey', self.parser.getMapsSoundingLike('Golmud Railway'))
        self.assertEqual('MP_Naval', self.parser.getMapsSoundingLike('paracel'))
        self.assertEqual('MP_Naval', self.parser.getMapsSoundingLike('storm'))
        self.assertEqual('MP_Naval', self.parser.getMapsSoundingLike('Paracel Storm'))
        self.assertEqual('MP_Prison', self.parser.getMapsSoundingLike('operation'))
        self.assertEqual('MP_Prison', self.parser.getMapsSoundingLike('locker'))
        self.assertEqual('MP_Prison', self.parser.getMapsSoundingLike('Operation Locker'))
        self.assertEqual('MP_Resort', self.parser.getMapsSoundingLike('hainan'))
        self.assertEqual('MP_Resort', self.parser.getMapsSoundingLike('resort'))
        self.assertEqual('MP_Resort', self.parser.getMapsSoundingLike('Hainan Resort'))
        self.assertEqual('MP_Siege', self.parser.getMapsSoundingLike('siege'))
        self.assertEqual('MP_Siege', self.parser.getMapsSoundingLike('shanghai'))
        self.assertEqual('MP_Siege', self.parser.getMapsSoundingLike('Siege of Shanghai'))
        self.assertEqual('MP_TheDish', self.parser.getMapsSoundingLike('rogue'))
        self.assertEqual('MP_TheDish', self.parser.getMapsSoundingLike('trans'))
        self.assertEqual('MP_TheDish', self.parser.getMapsSoundingLike('Rogue Transmission'))
        self.assertEqual('MP_Tremors', self.parser.getMapsSoundingLike('Dawnbreaker'))
        self.assertEqual('XP1_001', self.parser.getMapsSoundingLike('silk'))
        self.assertEqual('XP1_002', self.parser.getMapsSoundingLike('altai'))
        self.assertEqual('XP1_003', self.parser.getMapsSoundingLike('guilin'))
        self.assertEqual('XP1_004', self.parser.getMapsSoundingLike('dragon'))

    def test_getGamemodeSoundingLike(self):
        self.assertEqual('ConquestSmall0', self.parser.getGamemodeSoundingLike('MP_Siege', 'ConquestSmall0'), 'ConquestSmall0')
        self.assertEqual('ConquestSmall0', self.parser.getGamemodeSoundingLike('MP_Siege', 'Conquest'), 'Conquest')
        self.assertListEqual(['Team Deathmatch', 'Squad Deathmatch'], self.parser.getGamemodeSoundingLike('MP_Siege', 'Deathmatch'), 'Deathmatch')
        self.assertListEqual(['Rush', 'Defuse', 'Conquest'], self.parser.getGamemodeSoundingLike('MP_Siege', 'foo'))
        self.assertEqual('TeamDeathMatch0', self.parser.getGamemodeSoundingLike('MP_Siege', 'tdm'), 'tdm')
        self.assertEqual('TeamDeathMatch0', self.parser.getGamemodeSoundingLike('MP_Siege', 'teamdeathmatch'), 'teamdeathmatch')
        self.assertEqual('TeamDeathMatch0', self.parser.getGamemodeSoundingLike('MP_Siege', 'team death match'), 'team death match')
        self.assertEqual('ConquestLarge0', self.parser.getGamemodeSoundingLike('MP_Siege', 'CQ64'), 'CQ64')
        self.assertEqual('Domination0', self.parser.getGamemodeSoundingLike('MP_Siege', 'domination'), 'domination')
        self.assertEqual('Domination0', self.parser.getGamemodeSoundingLike('MP_Siege', 'dom'), 'dom')
        self.assertEqual('Obliteration', self.parser.getGamemodeSoundingLike('MP_Siege', 'obliteration'), 'obliteration')
        self.assertEqual('Obliteration', self.parser.getGamemodeSoundingLike('MP_Siege', 'obl'), 'obl')
        self.assertEqual('Elimination0', self.parser.getGamemodeSoundingLike('MP_Siege', 'defuse'), 'defuse')
        self.assertEqual('Elimination0', self.parser.getGamemodeSoundingLike('MP_Siege', 'def'), 'def')
        self.assertEqual('SquadDeathMatch0', self.parser.getGamemodeSoundingLike('MP_Siege', 'sqdm'), 'sqdm')


class Test_getPlayerPings(BF4TestCase):

    def setUp(self):
        BF4TestCase.setUp(self)
        self.conf = XmlConfigParser()
        self.conf.loadFromString("""
                <configuration>
                </configuration>
            """)
        self.parser = Bf4Parser(self.conf)
        self.p1 = FakeClient(self.parser, name="Player1")
        self.p2 = FakeClient(self.parser, name="Player2")

    def test_no_player(self):
        # WHEN
        actual_result = self.parser.getPlayerPings()
        # THEN
        self.assertDictEqual({}, actual_result)

    def test_one_player(self):
        # GIVEN
        self.p1.connects("Player1")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '1', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings()
        # THEN
        self.assertDictEqual({self.p1.cid: 140}, actual_result)

    def test_two_player(self):
        # GIVEN
        self.p1.connects("Player1")
        self.p2.connects("Player2")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '2', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140',
             'Player2', 'EA_XXY', '1', '1', '0', '0', '0', '1', '450']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings()
        # THEN
        self.assertDictEqual({self.p1.cid: 140, self.p2.cid: 450}, actual_result)

    def test_two_player_filter_client_ids(self):
        # GIVEN
        self.p1.connects("Player1")
        self.p2.connects("Player2")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '2', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140',
             'Player2', 'EA_XXY', '1', '1', '0', '0', '0', '1', '450']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings(filter_client_ids=[self.p1.cid])
        # THEN
        self.assertDictEqual({self.p1.cid: 140}, actual_result)

    def test_bad_data_filter_client_ids(self):
        # GIVEN
        self.p1.connects("Player1")
        self.p2.connects("Player2")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '1', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140',
             'Player2', 'EA_XYZ', '1', '1', '0', '0', '0', '1', 'f00']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings(filter_client_ids=[self.p1.cid, self.p2.cid])
        # THEN
        self.assertDictEqual({self.p1.cid: 140}, actual_result)

    def test_bad_data(self):
        # GIVEN
        self.p1.connects("Player1")
        self.p2.connects("Player2")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '1', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140',
             'Player2', 'EA_XYZ', '1', '1', '0', '0', '0', '1', 'f00']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings()
        # THEN
        self.assertDictEqual({self.p1.cid: 140}, actual_result)

    def test_exception(self):
        # GIVEN
        self.p1.connects("Player1")
        self.p2.connects("Player2")
        when(self.parser).write(('admin.listPlayers', 'all')).thenReturn(
            ['9', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', 'rank', 'ping',
             '1', 'Player1', 'EA_XXX', '1', '1', '0', '0', '0', '1', '140',
             'Player2', 'EA_XYZ', '1', '1', '0', '0', '0', '1', 'f00']
        )
        # WHEN
        actual_result = self.parser.getPlayerPings(filter_client_ids=[self.p1.cid, self.p2.cid])
        # THEN
        self.assertDictEqual({self.p1.cid: 140}, actual_result)


class Test_patch_b3_Client_isAlive(BF4TestCase):
    def setUp(self):
        BF4TestCase.setUp(self)
        self.conf = XmlConfigParser()
        self.conf.loadFromString("""
                <configuration>
                </configuration>
            """)
        self.parser = Bf4Parser(self.conf)
        self.foobar = self.parser.clients.newClient(cid='Foobar', name='Foobar', guid="FoobarGuid")

    def test_unknown(self):
        # GIVEN
        when(self.parser).write(('player.isAlive', 'Foobar')).thenReturn()
        # THEN
        self.assertEqual(b3.STATE_UNKNOWN, self.foobar.state)

    def test_alive(self):
        # GIVEN
        when(self.parser).write(('player.isAlive', 'Foobar')).thenReturn(['true'])
        # THEN
        self.assertEqual(b3.STATE_ALIVE, self.foobar.state)

    def test_dead(self):
        # GIVEN
        when(self.parser).write(('player.isAlive', 'Foobar')).thenReturn(['false'])
        # THEN
        self.assertEqual(b3.STATE_DEAD, self.foobar.state)

    def test_exception_InvalidPlayerName(self):
        when(self.parser).write(('player.isAlive', 'Foobar')).thenRaise(CommandFailedError(['InvalidPlayerName']))
        self.assertEqual(b3.STATE_UNKNOWN, self.foobar.state)


class Test_patch_b3_admin_plugin(BF4TestCase):
    def setUp(self):
        BF4TestCase.setUp(self)
        with logging_disabled():
            self.conf = XmlConfigParser()
            self.conf.loadFromString("""
                    <configuration>
                    </configuration>
                """)
            self.parser = Bf4Parser(self.conf)
            adminPlugin_conf = CfgConfigParser()
            adminPlugin_conf.loadFromString(r"""
[commands]
map: 20
""")
            adminPlugin = AdminPlugin(self.parser, adminPlugin_conf)
            adminPlugin.onLoadConfig()
            adminPlugin.onStartup()
            when(self.parser).getPlugin('admin').thenReturn(adminPlugin)
            self.parser.patch_b3_admin_plugin()
            self.joe = FakeClient(self.parser, name="Joe", guid="joeguid", groupBits=128)
            self.joe.connects(cid="joe")
            self.parser.game.gameType = "Domination0"
            self.parser.game.serverinfo = {'roundsTotal': 2}

    def test_map_known_on_correct_gamemode(self):
        # GIVEN
        self.parser.game.gameType = "Elimination0"
        # WHEN
        with patch.object(self.parser, 'changeMap') as changeMap_mock:
            self.joe.says("!map siege")
        # THEN
        self.assertListEqual([call('MP_Siege', gamemode_id='Elimination0', number_of_rounds=2)], changeMap_mock.mock_calls)
        self.assertListEqual([], self.joe.message_history)

    def test_map_InvalidGameModeOnMap(self):
        # BF4 cupport currently all game modes on every map
        # we take for this test a BF3 game mode that is not implement in Bf4

        # WHEN
        #when(self.parser).changeMap('MP_Siege', gamemode_id="CaptureTheFlag0", number_of_rounds=2).thenRaise(
        #    CommandFailedError(["InvalidGameModeOnMap"]))
        #self.joe.says("!map siege")
        # THEN
        #self.assertListEqual(
        #    ['Siege of Shanghai cannot be played with gamemode CaptureTheFlag0',
        #     'supported gamemodes are : Squad Deathmatch, Domination, Team Deathmatch, Rush, Obliteration, Conquest, Defuse, Conquest64'
        #    ], self.joe.message_history)
        pass

    def test_map_InvalidRoundsPerMap(self):
        # WHEN
        when(self.parser).changeMap('MP_Siege', gamemode_id="Domination0", number_of_rounds=2).thenRaise(
            CommandFailedError(["InvalidRoundsPerMap"]))
        self.joe.says("!map siege")
        # THEN
        self.assertListEqual(['number of rounds must be 1 or greater'], self.joe.message_history)

    def test_map_Full(self):
        # WHEN
        when(self.parser).changeMap('MP_Siege', gamemode_id="Domination0", number_of_rounds=2).thenRaise(
            CommandFailedError(["Full"]))
        self.joe.says("!map siege")
        # THEN
        self.assertListEqual(['Map list maximum size has been reached'], self.joe.message_history)

    def test_map_unknown(self):
        # WHEN
        with patch.object(self.parser, 'changeMap') as changeMap_mock:
            self.joe.says("!map xxxxxxxxf00xxxxxxxxx")
        # THEN
        self.assertListEqual([], changeMap_mock.mock_calls)
        self.assertListEqual(['do you mean : siege of shanghai, flood zone, rogue transmission ?'], self.joe.message_history)
