from data.lib.utils2 import SNConfig


data = {'helloworld': 'Hello:World'}

print(data)

enc = SNConfig.dump(data)

print(repr(enc))

dec = SNConfig(enc).load()