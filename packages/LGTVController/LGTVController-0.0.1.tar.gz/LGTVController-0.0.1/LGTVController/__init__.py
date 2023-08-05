#!/usr/bin/env python3
import time
import sys
import json
import base64
import random
import stackprinter
from pprint import pprint
from box import Box # pip install python-box
from pathlib import Path

from wakeonlan import send_magic_packet
import socket
import websocket # pip install websocket-client

def write_json( file_path , python_object ):
	with open( file_path , "w" , encoding="utf-8" ) as f:
		json.dump( python_object , f , ensure_ascii=False , indent=4 )

def read_json( file_path ):
	with open( file_path ) as f:
		return json.load( f )

class LGTVController:

	def __init__( self , config={} ):
		self.config = Box( config )
		if "port" not in self.config:
			self.config.port = 3000
		self.connected = False
		self.websocket_url = f"ws://{self.config.ip_address}:{self.config.port}/"
		self.handshake_data_file_path = Path( __file__ ).parent.joinpath( "handshake.json" )
		self.handshake_data = read_json( self.handshake_data_file_path )
		self.endpoints_file_path = Path( __file__ ).parent.joinpath( "endpoints.json" )
		self.endpoints = Box( read_json( self.endpoints_file_path ) )
		if "client_key" not in self.config:
			print( "No Client Key Provided , Re-Pairing with TV" )
			# self.pair()
		else:
			self.handshake_data[ "payload" ][ "client-key" ] = self.config.client_key
			self.handshake_data_string = json.dumps( self.handshake_data )
		# write_json( "why.json" , self.handshake_data )
		# pprint( self.handshake_data )

	def pair( self ):
		try:
			ws = websocket.create_connection( websocket_url , sockopt=( ( socket.IPPROTO_TCP , socket.TCP_NODELAY , 1 ) , ) , suppress_origin=True , timeout=60 )
			# ws.timeout = 60
			if ws.connected != True:
				print( "Couldn't Connect to TV's Websocket Server" )
				sys.exit( 1 )
			ws.send( json.dumps( self.handshake_data ) )
			if ws.connected != True:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			first_response = ws.recv()
			first_response = json.loads( first_response )
			if "payload" not in first_response:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			if "returnValue" not in first_response[ "payload" ]:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			if first_response[ "payload" ][ "returnValue" ] != True:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			print( "You have 60 seconds to accept pairing prompt" )
			second_response = ws.recv()
			second_response = json.loads( second_response )
			if "payload" not in second_response:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			if "client-key" not in second_response[ "payload" ]:
				print( "Failed to Pair with TV" )
				sys.exit( 1 )
			self.config.client_key = second_response[ "payload" ][ "client-key" ]
			self.handshake_data[ "payload" ][ "client-key" ] = second_response[ "payload" ][ "client-key" ]
			self.handshake_data_string = json.dumps( self.handshake_data )
			print( "Succesfully Paired with TV" )
			return True
		except Exception as e:
			print( stackprinter.format() )
			sys.exit( 1 )

	def open_websocket( self ):
		try:
			self.ws = websocket.create_connection( self.websocket_url , sockopt=( ( socket.IPPROTO_TCP , socket.TCP_NODELAY , 1 ) , ) , suppress_origin=True , timeout=3 )
			# self.ws.timeout = 3
			self.connected = self.ws.connected
			return True
		except Exception as e:
			# print( stackprinter.format() )
			self.ws = False
			self.connected = False
			# return False
			if "always_wakeup" in self.config:
				if self.config.always_wakeup == True:
					try:
						if "mac_address" not in self.config:
							print( "you need to provide a mac-address to try and wakeup the tv" )
							sys.exit( 1 )
						print( f"Sending Magic Packet to : {self.config.mac_address}" )
						send_magic_packet( self.config.mac_address )
						print( "Sleeping for 10 seconds to wait for TV to boot up" )
						time.sleep( 10 )
						self.ws = websocket.create_connection( self.websocket_url , sockopt=( ( socket.IPPROTO_TCP , socket.TCP_NODELAY , 1 ) , ) , suppress_origin=True , timeout=3 )
						self.connected = self.ws.connected
						return True
					except Exception as extra:
						print( extra )
						print( "Sent Magic Packet to wakeup TV , but TV's websocket server still didn't respond" )
						sys.exit( 1 )
				else:
					print( "TV is probably off or asleep , send magic packet to mac-address to wake it up first" )
					sys.exit( 1 )
			else:
				print( "TV is probably off or asleep , send magic packet to mac-address to wake it up first" )
				sys.exit( 1 )

	def close_websocket( self ):
		try:
			self.ws.close()
			self.connected = self.ws.connected
			return True
		except Exception as e:
			print( stackprinter.format() )
			self.ws = False
			self.connected = False
			return False

	def handshake( self ):
		try:
			if self.connected == False:
				print( "Not Connected !" )
				return False
			self.ws.send( self.handshake_data_string )
			x = self.ws.recv() # you have to receive here , otherwise it fails
			# print( "Authenticated with TV's Websocket Server" )
			return True
		except Exception as e:
			print( stackprinter.format() )
			# return False
			print( "Failed to Handshake with TV's Websocket Server" )
			sys.exit( 1 )

	def generate_message_id( self , prefix=False ):
		if prefix != False:
			return f"lgtv_{prefix}_{random.randint( 1 , 100 )}"
		else:
			return f"lgtv_{random.randint( 1 , 100 )}"

	def send_message( self , message="hola" , icon_path=None ):
		try:
			icon_encoded_string = ""
			icon_extension = ""
			if icon_path is not None:
				icon_extension = os.path.splitext( icon_path )[ 1 ][ 1: ]
				with open( icon_path , "rb" ) as icon_file:
					icon_encoded_string = base64.b64encode( icon_file.read() ).decode( "ascii" )
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "send_message" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.show_message}" ,
				"payload": {
					"message": message ,
					"iconData": icon_encoded_string ,
					"iconExtension": icon_extension
				} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Apps
	def get_apps( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_apps" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_apps}" ,
				"payload": {} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_current_app( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_current_app" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_current_app_info}" ,
				"payload": {} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def launch_app( self , app_name="netflix" ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "launch_app" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.launch}" ,
				"payload": {
					"id": app_name
				} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def launch_app_with_params( self , app_name="netflix" , params={} ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "launch_app_with_params" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.launch}" ,
				"payload": {
					"id": app_name ,
					"params": params
				} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def launch_app_with_with_content_id( self , app_name="netflix" , content_id=False ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "launch_app_with_content_id" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.launch}" ,
				"payload": {
					"id": app_name ,
					"contentId": content_id
				} ,
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def close_app( self , app_name="netflix" ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "close_app" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.launch}" ,
				"payload": {
					"id": app_name
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Services
	def get_services( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_services" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_services}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_software_info( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_software_info" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_software_info}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def power_off( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "power_off" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.power_off}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def power_on( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "power_on" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.power_on}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			if "mac_address" in self.config:
				send_magic_packet( self.config.mac_address )
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# 3D Mode
	def turn_3d_on( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "turn_3d_on" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.x3d_on}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def turn_3d_off( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "turn_3d_off" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.x3d_off}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Inputs
	def get_inputs( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_inputs" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_inputs}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_input( self ):
		try:
			return self.get_current_app()
		except Exception as e:
			print( stackprinter.format() )
			return False

	def set_input( self , input_name="HDMI-1" ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "set_input" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.set_input}" ,
				"payload": {
					"inputId": input_name
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Audio
	def get_audio_status( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_audio_status" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_audio_status}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# def get_muted(self):
	# 	"""Get mute status."""
	# 	return self.get_audio_status().get('mute')

	def set_mute( self , mute=True ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "set_mute" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.set_mute}" ,
				"payload": {
					"mute": mute
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_volume( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_volume" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_volume}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def set_volume( self , volume=11 ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "set_volume" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.set_volume}" ,
				"payload": {
					"volume": volume
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def volume_up( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "volume_up" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.volume_up}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def volume_down( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "volume_down" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.volume_down}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# TV Channel
	def channel_up( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "channel_up" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.tv_channel_up}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def channel_down( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "channel_down" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.tv_channel_down}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_channels( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_channels" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_tv_channels}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_current_channel( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_current_channel" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_current_channel}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def get_channel_info( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "get_channel_info" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.get_channel_info}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def set_channel( self , channel=3 ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "set_channel" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.set_channel}" ,
				"payload": {
					"channelId": channel
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Media control
	def play( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "play" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_play}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def pause( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "pause" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_pause}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def stop( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "stop" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_stop}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def close( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "close" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_close}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def rewind( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "rewind" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_rewind}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def fast_forward( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "fast_forward" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.media_fast_forward}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Keys
	def send_enter_key( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "send_enter_key" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.send_enter}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def send_delete_key( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "send_delete_key" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.send_delete}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	# Web
	def open_url( self , url="https://www.windy.com/-Thunderstorms-thunder?thunder,39.793,-80.717,6" ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "open_url" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.open}" ,
				"payload": {
					"target": url
				}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

	def close_web( self ):
		try:
			self.open_websocket()
			self.handshake()
			self.ws.send(json.dumps({
				"id":  self.generate_message_id( "close_web" ) ,
				"type": "request" ,
				"uri": f"ssap://{self.endpoints.close_web_app}" ,
				"payload": {}
			}))
			result = self.ws.recv()
			self.close_websocket()
			return result
		except Exception as e:
			print( stackprinter.format() )
			return False

if __name__ == "__main__":
	x = LGTVController({
		"ip_address": "192.168.1.6" ,
		"port": 3000 ,
		"mac_address": "B4:B2:91:45:F7:B2" ,
		"client_key": "18370ed9f27f11668f899ca71e479bc6" ,
		"always_wakeup": True
	})
	pprint( x.get_current_app() )
	pprint( x.power_off() )