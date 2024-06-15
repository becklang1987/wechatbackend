import re   
cmdpattern = re.compile(r'^( *show|ping|traceroute|trace|sh)', re.IGNORECASE)
cfgpattern = re.compile(r'(.*restart|.*reload|.*boot|.*delete)', re.IGNORECASE)
print(cmdpattern.match("       show123123"))
print(cfgpattern.match("  do restart"))


MNR8Q~4ZM8XKwjOEVaIs8ifHoXqk5NgG4g8XYaRc KEYvalue
b811f2ce-c6a1-4a2b-ae58-32e736fb5ea9 KeyID