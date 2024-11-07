import re
import json
# import eyed3
import shlex
import base64
import logging
import requests
import subprocess
from random import *
from eyed3 import id3, load
from datetime import datetime, timedelta
import defusedxml.ElementTree as ET

import math

logging.basicConfig(level=logging.INFO)


class Radiko():
    def __init__(self, args):
        self.args = args
        self.version = args.version
        self.station_id = args.station
        self.areafree = args.areaFree
        self.timefree = args.timeFree
        self.startTime = args.startTime
        self.endTime = args.endTime
        self.save = args.save
        
        self.auth_key = self.get_Full_Key()
        # self.user_id = 'dummy_user'
        self.user_id = self.get_User_ID()
        self.app, self.device, self.connection = self.get_platform_info()
        self.save_extension = 'mp3'
    
    
    def load_json(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return data
    
    
    def get_Date(self):
        if self.startTime != None:
            dateTime_format = '%Y%m%d%H%M%S'
            dateTime = datetime.strptime(self.startTime, dateTime_format)
            
            date_format = '%Y%m%d'
            time_format = '%H:%M:%S'
            date = datetime.strftime(dateTime, date_format)
            time = datetime.strftime(dateTime, time_format)
            
            start_date = f'{date}000000'
            end_date = f'{date}050000'
            start_date = datetime.strptime(start_date, dateTime_format)
            end_date = datetime.strptime(end_date, dateTime_format)
            
            if start_date <= dateTime <= end_date:
                dateTime = dateTime + timedelta(days=-1)
                date = datetime.strftime(dateTime, date_format)
                # time = datetime.strftime(dateTime, time_format)
        else:
            date = ''
    
        return date
    
    def get_Program_title(self):
        date = self.get_Date()
        url = f'https://radiko.jp/v3/program/station/date/{date}/{self.station_id}.xml'
        
        response: requests.Response = requests.get(url)
        response_element = ET.fromstring(response.text)
        
        for stations in response_element.findall('stations'):
            for station in stations.findall('station'):
                station_name = station.findtext('name')
                for progs in station.findall('progs'):
                    program_date = progs.findtext('date')
                    for prog in progs.findall('prog'):
                        if (self.startTime == prog.attrib["ft"]) and (self.endTime == prog.attrib["to"]):
                            program_title = prog.findtext('title')
                            program_logo = prog.findtext('img')
                            program_pfm = prog.findtext('pfm')
                            # for tag in prog.findall('tag'):
                            #     item = tag.find('item')
                            #     program_pfm = item.findtext('name')
                        else:
                            pass
        
        program_information = {
            'station_id' : self.station_id,
            'station_name' : station_name,
            'program_date' : program_date,
            'program_title' : program_title,
            'program_performer' : program_pfm,
            'program_logo_url' : program_logo,
        }
        
        return program_information
        
    
    
    def get_User_ID(self):
        hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        user_id = ''
        for i in range(32):
            user_id += hex[math.floor(random() * len(hex)) >> 0]
            
        return user_id
    
    
    def get_platform_info(self):
        app = 'aSmartPhone7o'
        device = 'Python.Radiko'
        connection = 'wifi'
        
        return app, device, connection
    
    
    def get_Available_Stations(self) -> list:
        url = 'https://radiko.jp/v3/station/region/full.xml'
        
        available_stations = []
        response: requests.Response = requests.get(url)
        response_element = ET.fromstring(response.text)
        
        for stations in response_element:
            for station in stations:
                info = {}
                
                for tag in station:
                    info[tag.tag] = tag.text
                    
                available_stations.append(info)
                
        return available_stations


    def get_Station(self) -> dict:
        available_stations = self.get_Available_Stations()

        try:
            for station in available_stations:
                if station['id'] == self.station_id:
                    area_id = station['area_id']
                    station_logo_url = station['banner']
        except:
            area_id = ''
            station_logo_url = ''
            
        return area_id, station_logo_url


    def is_Available_Station_ID(self) -> bool:
        available_station_ids = []
        available_stations = self.get_Available_Stations()
        
        for station in available_stations:
            available_station_ids.append(station['id'])
            
        check_station_id = self.station_id in available_station_ids
        
        return check_station_id
    
    
    def get_GPS(self, area_id) -> str:
        file_path = f'./data/json/area.json'
        COORDINATES_LIST = self.load_json(file_path)
        
        latitude = COORDINATES_LIST[area_id]['latitude']
        longitude = COORDINATES_LIST[area_id]['longitude']
        
        latitude = latitude + random() / 40.0 * (1 if (random() > 0.5) else -1)
        longitude = longitude + random() / 40.0 * (1 if (random() > 0.5) else -1)
        
        digits = 6
        latitude = round(latitude, digits)
        longitude = round(longitude, digits)
        
        latitude = str(latitude)
        longitude = str(longitude)
        
        coordinate = f'{latitude},{longitude},gps'
        
        return coordinate
    
    
    def get_Full_Key(self) -> str:
        file_path = f'./data/auth/auth_key.bin'
        
        with open(file_path, 'rb') as f:
            auth_key = f.read()
        auth_key = base64.b64encode(auth_key)
        
        return auth_key
    
    
    def access_Auth1(self, area_id):
        pattern = r'JP|^[1-47]$'
        if re.match(pattern, area_id) is None:
            raise TypeError('Invalid Area ID')
        
        url = 'https://radiko.jp/v2/api/auth1'
        
        headers={
            'X-Radiko-App' : self.app,
            'X-Radiko-App-Version' : self.version,
            'X-Radiko-Device' : self.device,
            'X-Radiko-User' : self.user_id
        }
        
        auth1: requests.Response = requests.get(url=url, headers=headers)
        auth1.raise_for_status()
        
        return auth1
        
    
    def access_Partial_Key(self, auth1):
        auth_key = base64.b64decode(self.auth_key)
        
        auth_token = auth1.headers.get('X-Radiko-AuthToken')
        key_offset = int(auth1.headers.get('X-Radiko-KeyOffset'))
        key_length = int(auth1.headers.get('X-Radiko-KeyLength'))
        
        partial_key = auth_key[key_offset : key_offset + key_length]
        partial_key = base64.b64encode(partial_key)
        
        return auth_token, partial_key
    
    
    def access_Auth2(self, auth_token, coordinate, partial_key):
        url = 'https://radiko.jp/v2/api/auth2'
        
        headers = {
            'X-Radiko-App' : self.app,
            'X-Radiko-App-Version' : self.version,
            'X-Radiko-AuthToken' : auth_token,
            'X-Radiko-Connection' : self.connection,
            'X-Radiko-Device' : self.device,
            'X-Radiko-Location' : coordinate,
            'X-Radiko-PartialKey' : partial_key,
            'X-Radiko-User' : self.user_id
        }
        
        auth2: requests.Response = requests.get(url=url, headers=headers)
        auth2.raise_for_status()
        
        return auth2

    
    def access_Authentication(self) -> str:
        if not self.is_Available_Station_ID():
            return ''
        
        area_id, station_logo_url = self.get_Station()
        auth1 = self.access_Auth1(area_id=area_id)
        auth_token, partial_key = self.access_Partial_Key(auth1=auth1)
        coordinate = self.get_GPS(area_id=area_id)
        auth2 = self.access_Auth2(auth_token=auth_token, coordinate=coordinate, partial_key=partial_key)
        
        # program_information = self.get_Program_Info(area_id=area_id, station_id=self.station_id)
        
        # logging.info(f'area_id: {area_id}')
        # logging.info(f'auth_token: {auth_token}')
        # logging.info(f'partial_key: {partial_key}')
        # logging.info(f'coordinate: {coordinate}')
        
        return auth_token
    
    
    def get_Stream_URL(self) -> str:
        url = f'https://radiko.jp/v3/station/stream/{self.app}/{self.station_id}.xml'
        
        base_url = []
        if not self.is_Available_Station_ID():
            return base_url
        
        response: requests.Response = requests.get(url)
        response_element = ET.fromstring(response.text)

        for url in response_element:
            url_timefree = bool(int(url.attrib['timefree']))
            url_areafree = bool(int(url.attrib['areafree']))
            
            if (url_areafree == self.areafree) and (url_timefree == self.timefree):
                base_url.append(url[0].text)
                
        if (self.areafree == False) and (self.timefree == False):
            url = base_url[2]
        elif (self.areafree == False) and (self.timefree == True):
            url = base_url[1]
            
        url = base_url[-1]
            
        return url
    
    
    def get_Chunk_m3u8_URL(self, url, auth_token) -> str:
        headers = {
            'X-Radiko-AuthToken' : auth_token,
        }
        
        response: requests.Response = requests.get(url=url, headers=headers)
        body = response.text
        
        pattern = r'^https?://.+m3u8'
        lines = re.findall(pattern, body, flags=(re.MULTILINE))
        response.raise_for_status()
        
        return lines[0]
    
    
    def get_ACC_URL(self, chunk_url, auth_token) -> str:
        url = chunk_url
        
        headers = {
            'X-Radiko-AuthToken' : auth_token,
        }
        
        response: requests.Response = requests.get(url=url, headers=headers)
        body = response.text
        
        return body
    

    def get_Stream_Info(self) -> dict:
        stream_info = {}
        if not self.is_Available_Station_ID():
            return stream_info
        
        auth_token = self.access_Authentication()
        stream_url = self.get_Stream_URL()
        
        stream_info['token'] = auth_token
        if (self.startTime == None) and (self.endTime == None):
            stream_info['url'] = f'{stream_url}?station_id={self.station_id}&l=15'
        else:
            stream_info['url'] = f'{stream_url}?station_id={self.station_id}&l=15&ft={self.startTime}&to={self.endTime}'
            
        return stream_info
        

    def get_Chunk_m3u8_Info(self) -> dict:
        stream_info = {}
        if not self.is_Available_Station_ID():
            return stream_info
        
        auth_token = self.access_Authentication()
        stream_url = self.get_Stream_URL()
        
        stream_info['token'] = auth_token
        if (self.startTime == None) and (self.endTime == None):
            stream_info['url'] = f'{stream_url}?station_id={self.station_id}&l=15'
        else:
            stream_info['url'] = f'{stream_url}?station_id={self.station_id}&l=15&ft={self.startTime}&to={self.endTime}'
            
        url = stream_info['url']
        chunk_url = self.get_Chunk_m3u8_URL(url=url, auth_token=auth_token)
        stream_info['url'] = chunk_url
        
        return stream_info
    
    
    def get_Program_Info(self, area_id) -> dict:
        url = f'https://radiko.jp/v3/program/now/{area_id}.xml'
        
        response: requests.Response = requests.get(url=url)
        response_element = ET.fromstring(response.text)
        
        for stations in response_element.findall('stations'):
            for station in stations.findall('station'):
                if station.attrib['id'] == self.station_id:
                    station_name = station.findtext('name')
                    for progs in station.findall('progs'):
                        program_date = progs.findtext('date')
                        prog = progs.find('prog')
                        program_title = prog.findtext('title')
                        program_info = prog.findtext('info')
                        program_pfm = prog.findtext('pfm')
                        program_logo = prog.findtext('img')
                else:
                    pass
        
        program_information = {
            'station_id' : self.station_id,
            'station_name' : station_name,
            'program_date' : program_date,
            'program_title' : program_title,
            'program_info' : program_info,
            'program_performer' : program_pfm,
            'program_logo_url' : program_logo,
        }
        
        return program_information
    
    
    def get_Program_Path(self, cmd_name) -> str:
        if subprocess.getstatusoutput(f'type {cmd_name}')[0] == 0:
            return subprocess.check_output(f'which {cmd_name}', shell=True).strip().decode('utf8')
        else:
            print(f'{cmd_name} not found , install {cmd_name} ')
            exit()
    
    
    def get_ffmpeg_Command(self, ffmpeg_path, input, out_filename, auth_token=None, input_options='', output_options='') -> str:
        cmd = f'"{ffmpeg_path}" {input_options} -n -headers "X-Radiko-AuthToken: {auth_token}" -i "{input}" {output_options} "{out_filename}"'

        return cmd
    
    
    def get_ffplay_Command(self, ffplay_path, input) -> str:
        cmd = f'{ffplay_path} "{input}"'

        return cmd
    
    
    def save_mp4(self):
        program_information = self.get_Program_title()
        program_date = program_information['program_date']
        program_title = program_information['program_title']
        save_fime_name = f'./data/{self.save_extension}/{self.station_id}_{program_title}_{program_date}.{self.save_extension}'
        
        ffmpeg = self.get_Program_Path('ffmpeg')
        stream_info = self.get_Chunk_m3u8_Info()
        auth_token = stream_info['token']
        chunk_url = stream_info['url']
        print(f'auth_token: {auth_token}')
        print(f'chunk_url: {chunk_url}')
        
        full_stream_url = f'{chunk_url}?X-Radiko-AuthToken={auth_token}'
        print(f'full_url: {full_stream_url}')
        
        output_options = '-threads 8'
        save_cmd = self.get_ffmpeg_Command(ffmpeg_path=ffmpeg, input=chunk_url, out_filename=save_fime_name, auth_token=auth_token, output_options=output_options)
        save_cmd_split = shlex.split(save_cmd)

        process = subprocess.Popen(save_cmd_split)
        process.communicate()
        
        mp3_tag = self.set_mp3_Meta_Tag(file_path=save_fime_name, program_information=program_information)
        
        return ''
    
    
    def play_m3u8(self):
        ffplay = self.get_Program_Path('ffplay')
        stream_info = self.get_Chunk_m3u8_Info()
        chunk_url = stream_info['url']
        
        play_cmd = self.get_ffplay_Command(ffplay_path=ffplay, input=chunk_url)
        play_cmd_split = shlex.split(play_cmd)

        process = subprocess.Popen(play_cmd_split)
        process.communicate()
        
        return ''
    
    
    def set_mp3_Meta_Tag(self, file_path, program_information):
        station_id = program_information['station_id']
        station_name = program_information['station_name']
        program_date = program_information['program_date']
        program_title = program_information['program_title']
        program_performer = program_information['program_performer']
        program_logo_url = program_information['program_logo_url']
        
        audiofile = load(file_path)
        
        response = requests.get(program_logo_url)
        imagedata = response.content
        audiofile.tag.images.set(3, imagedata, 'image/png', u'Description')
        
        audiofile.tag.title = program_title
        audiofile.tag.artist = program_performer
        audiofile.tag.album = f'{program_title} {program_date}'
        audiofile.tag.album_artist = program_performer
        audiofile.tag.recording_date = program_date
        audiofile.tag.original_release_date = program_date
        audiofile.tag.release_date = program_date
        audiofile.tag.tagging_date = program_date
        audiofile.tag.encoding_date = program_date
        audiofile.tag.track_num = 1

        audiofile.tag.save()
        
        return ''
    
    
    def get_Full_Stream_URL(self):
        stream_info = self.get_Chunk_m3u8_Info()
        auth_token = stream_info['token']
        chunk_url = stream_info['url']
        print(f'auth_token: {auth_token}')
        print(f'chunk_url: {chunk_url}')

        full_stream_url = f'{chunk_url}?X-Radiko-AuthToken={auth_token}'
        print(f'full_url: {full_stream_url}')
        
        return ''
