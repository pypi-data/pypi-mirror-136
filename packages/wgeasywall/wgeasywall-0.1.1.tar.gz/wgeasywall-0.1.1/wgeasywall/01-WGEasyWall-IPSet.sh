echo "WGEasywall IPSet Generator"
echo "-----------------------------"
#!/bin/bash
echo "Remove WGEasywall generated IPSets"
echo "-----------------------------"
Sets2delete="$(ipset list | grep 'Name:' | cut -d\  -f2 | grep 'WGEasywall' | tr '\n' ' ')"
IFS=', ' read -r -a Sets2deleteArray <<< "$Sets2delete"
for set in "${Sets2deleteArray[@]}"; do
  echo "Remove IPSet $set"
  ipset destroy $set
done
echo "-----------------------------"
# Group Bonn
echo "Create Set WGEasywall-Bonn ..."
ipset create WGEasywall-Bonn hash:ip
Bonn_IPs=(192.168.0.53 192.168.0.51 192.168.0.59 192.168.0.52)

for IP in "${Bonn_IPs[@]}"; do
  ipset add WGEasywall-Bonn $IP
done
echo "Set WGEasywall-Bonn Done"
echo "-----------------------------"
ipset list WGEasywall-Bonn
echo "-----------------------------"
# Group Berlin
echo "Create Set WGEasywall-Berlin ..."
ipset create WGEasywall-Berlin hash:ip
Berlin_IPs=(192.168.0.56 192.168.0.55 192.168.0.54 192.168.0.57)

for IP in "${Berlin_IPs[@]}"; do
  ipset add WGEasywall-Berlin $IP
done
echo "Set WGEasywall-Berlin Done"
echo "-----------------------------"
ipset list WGEasywall-Berlin
echo "-----------------------------"
# Group Bonn-Dep1
echo "Create Set WGEasywall-Bonn-Dep1 ..."
ipset create WGEasywall-Bonn-Dep1 hash:ip
Bonn_Dep1_IPs=(192.168.0.51 192.168.0.59)

for IP in "${Bonn_Dep1_IPs[@]}"; do
  ipset add WGEasywall-Bonn-Dep1 $IP
done
echo "Set WGEasywall-Bonn-Dep1 Done"
echo "-----------------------------"
ipset list WGEasywall-Bonn-Dep1
echo "-----------------------------"
# Group Bonn-Dep2
echo "Create Set WGEasywall-Bonn-Dep2 ..."
ipset create WGEasywall-Bonn-Dep2 hash:ip
Bonn_Dep2_IPs=(192.168.0.52)

for IP in "${Bonn_Dep2_IPs[@]}"; do
  ipset add WGEasywall-Bonn-Dep2 $IP
done
echo "Set WGEasywall-Bonn-Dep2 Done"
echo "-----------------------------"
ipset list WGEasywall-Bonn-Dep2
echo "-----------------------------"
