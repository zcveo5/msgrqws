#meta
# {"req": ["LibSettings"]}
import Application
import J
from LibSettings import SettingsAPI


def _sh():
    J.SetRestartFlag()
    Application.shutdown()


SettingsAPI.create_widget('ROOT', 'Button', text='Restart', fg='red', command=_sh)