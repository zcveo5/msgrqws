# METADATA
# {"req": ["LibSettings.py"]}
import Application, J


@J.API.on_init
def add_setts():
    Application.PROD = False