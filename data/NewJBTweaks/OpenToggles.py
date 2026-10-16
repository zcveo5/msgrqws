#meta
# {"req": ["LibEasyConfig", "LibTweaksInfo"]}


import LibTweaksInfo
import LibEasyConfig


LibEasyConfig.create('button', 'Dump LTI Logs', None, lambda _: LibTweaksInfo.dump_logs())