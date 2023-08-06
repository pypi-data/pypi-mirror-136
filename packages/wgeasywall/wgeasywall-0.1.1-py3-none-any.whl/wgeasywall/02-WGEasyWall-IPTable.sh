echo "WGEasywall IPTable Rules Importer"
echo "-----------------------------"
chainName=WGEasywall
if iptables -L $chainName 2 > /dev/null 2>&1; then
  echo "The chain 'WGEasywall' exist"
  echo "Start fulshing ...."
  iptables -F $chainName
  iptables -D FORWARD -j $chainName
  echo "Flushing done"
  echo "-----------------------------"
else
  echo "The chain 'WGEasywall' doesn't exist. Let's create ..."
  iptables -N $chainName
  echo "The chain 'WGEasywall' is created"
  echo "-----------------------------"
fi
# RaaC definition:
# General(protocol=tcp:srcIP=192.168.0.59:dstIP=192.168.0.52:dstPorts=80:comment='WGEasywall generated rule for edge from Client2 to Client3')->ACCEPT()                
iptables -A WGEasywall  --protocol tcp --source 192.168.0.59 --destination 192.168.0.52 -m multiport --dports 80 -m comment --comment 'WGEasywall generated rule for edge from Client2 to Client3' -j ACCEPT
#---------------------------
# RaaC definition:
# Conntrack(ctstate=ESTABLISHED)::General(protocol=tcp)->ACCEPT()                
iptables -A WGEasywall -m conntrack --ctstate ESTABLISHED --source 192.168.0.52 -m set --match-set WGEasywall-Berlin dst -m comment --comment 'WGEasywall generated rule for edge from Client3 to Berlin' -j ACCEPT
#---------------------------
# RaaC definition:
# Conntrack(ctstate=ESTABLISHED)::General(protocol=tcp)->ACCEPT()                
iptables -A WGEasywall  --protocol tcp --source 192.168.0.52 -m set --match-set WGEasywall-Berlin dst -m comment --comment 'WGEasywall generated rule for edge from Client3 to Berlin' -j ACCEPT
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcIP=192.168.0.56:dstIP=178.1.2.0/24:dstPorts=443:comment='WGEasywall generated rule for edge from Client7 to Resource1')->LOG(logLevel=3:logPrefix=armin)                
iptables -A WGEasywall  --protocol tcp --source 192.168.0.56 --destination 178.1.2.0/24 -m multiport --dports 443 -m comment --comment 'WGEasywall generated rule for edge from Client7 to Resource1' -j LOG --log-level 3 --log-prefix armin
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcIP=192.168.0.56:dstIP=178.1.2.0/24:dstPorts=443:comment='WGEasywall generated rule for edge from Client7 to Resource1')->DROP()                
iptables -A WGEasywall  --protocol tcp --source 192.168.0.56 --destination 178.1.2.0/24 -m multiport --dports 443 -m comment --comment 'WGEasywall generated rule for edge from Client7 to Resource1' -j DROP
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcSet=WGEasywall-Bonn-Dep1:dstSet=WGEasywall-Bonn-Dep2:dstPorts=80:comment='WGEasywall generated rule for edge from Bonn-Dep1 to Bonn-Dep2')->LOG(logLevel=3:logPrefix=armin)                
iptables -A WGEasywall  --protocol tcp -m set --match-set WGEasywall-Bonn-Dep1 src -m set --match-set WGEasywall-Bonn-Dep2 dst -m multiport --dports 80 -m comment --comment 'WGEasywall generated rule for edge from Bonn-Dep1 to Bonn-Dep2' -j LOG --log-level 3 --log-prefix armin
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcSet=WGEasywall-Bonn-Dep1:dstSet=WGEasywall-Bonn-Dep2:dstPorts=80:comment='WGEasywall generated rule for edge from Bonn-Dep1 to Bonn-Dep2')->DROP()                
iptables -A WGEasywall  --protocol tcp -m set --match-set WGEasywall-Bonn-Dep1 src -m set --match-set WGEasywall-Bonn-Dep2 dst -m multiport --dports 80 -m comment --comment 'WGEasywall generated rule for edge from Bonn-Dep1 to Bonn-Dep2' -j DROP
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcSet=WGEasywall-Bonn-Dep2:dstSet=WGEasywall-Berlin:dstPorts=443:comment='WGEasywall generated rule for edge from Bonn-Dep2 to Berlin')->LOG(logLevel=3:logPrefix=armin)                
iptables -A WGEasywall  --protocol tcp -m set --match-set WGEasywall-Bonn-Dep2 src -m set --match-set WGEasywall-Berlin dst -m multiport --dports 443 -m comment --comment 'WGEasywall generated rule for edge from Bonn-Dep2 to Berlin' -j LOG --log-level 3 --log-prefix armin
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcSet=WGEasywall-Bonn-Dep2:dstSet=WGEasywall-Berlin:dstPorts=443:comment='WGEasywall generated rule for edge from Bonn-Dep2 to Berlin')->DROP()                
iptables -A WGEasywall  --protocol tcp -m set --match-set WGEasywall-Bonn-Dep2 src -m set --match-set WGEasywall-Berlin dst -m multiport --dports 443 -m comment --comment 'WGEasywall generated rule for edge from Bonn-Dep2 to Berlin' -j DROP
#---------------------------
# RaaC definition:
# General(protocol=tcp:srcSet=WGEasywall-Bonn:dstSet=WGEasywall-Berlin:dstPorts=443:comment='WGEasywall generated rule for edge from Bonn to Berlin')->ACCEPT()                
iptables -A WGEasywall  --protocol tcp -m set --match-set WGEasywall-Bonn src -m set --match-set WGEasywall-Berlin dst -m multiport --dports 443 -m comment --comment 'WGEasywall generated rule for edge from Bonn to Berlin' -j ACCEPT
#---------------------------
            
# AppendMode is not enabled. Update FORWARD chain to use WGEasywall chain
iptables -I FORWARD 1 -j WGEasywall

# ReturnMode is not enabled. Default chain policy is DROP            
iptables -A WGEasywall -j DROP
    