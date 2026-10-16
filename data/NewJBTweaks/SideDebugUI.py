# METADATA
# {"req": ["SideDebugServer", "LibSettings"]}
import J
import SideDebugServer
from LibSettings import SettingsAPI


SettingsAPI.create_page('SideDebug')
SettingsAPI.create_widget('SideDebug', 'Label', textfunc=lambda: f'State {SideDebugServer.enable}\n{SideDebugServer.DEBUGGER_PORT}\n{SideDebugServer.DEBUG_PASSWORD}')
SettingsAPI.create_widget('SideDebug', 'Button', text='start debugging', command=SideDebugServer.enable_side_debug)
SettingsAPI.create_widget('SideDebug', 'Button', text='stop debugging', command=SideDebugServer.disable_side_debug)
