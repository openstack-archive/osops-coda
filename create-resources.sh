#!/bin/bash

# TODO add how to use this

source set_coda_env.sh

function hasNetwork {
	networks=`neutron net-list | awk '{if ($2 != "id" && $2 != "|" && NF>1) print $2 " " $4}' | grep -v "ext-net"`

	if [ ${#networks} -eq 0 ]
	then
		CODA_NETWORK_ID=""
		return -1
	else
		parts=($networks)
		CODA_NETWORK_ID=${parts[0]}
	fi
}

function hasSecGroups {
	expectedCount=$1
	groups=`neutron security-group-list | awk '{if ($2 != "id" && NF>1) print $4}' | grep -v default`

	if [ ${#groups} -eq 0 ]
	then
		echo "No Security Groups"
		return -1
	else
		parts=($groups)
		if [ ${#parts[@]} -ne $expectedCount ]
		then
			echo "WARNING: Unexpected Number of Security Groups."
			return -1
		fi
	fi
	
	return 0
}

function createSecurityGroup {
	groupName=$1
	description=$2
	exists=`neutron security-group-show $groupName`
	
	if [[ ${exists:0:1} == "+" ]] 
	then
		echo "Group $groupName already exists."
		return -1
	else
		neutron security-group-create $groupName --description "$description"
		return 0
	fi
}

function createFloatingIPs {
	count=$1
	floatingIPs=`neutron floatingip-list | awk '{if ($2 != "id" && NF>1) print $2}'`

	if [ ${#floatingIPs} -eq 0 ]
	then
		echo "Creating $count floating IP's."
		for x in $(seq 1 $count)
		do
			neutron floatingip-create Ext-Net
		done
	else
		parts=($floatingIPs)
		if [ ${#parts[@]} -gt $count ]
		then
			echo "WARNING: Too many floating IP's."
		elif [ ${#parts[@]} -lt $count ]
		then
			diff=`expr $count - ${#parts[@]}`
			echo "Not enough floating IP's, creating $diff more."
			for x in $(seq 1 $diff)
			do
				neutron floatingip-create Ext-Net
			done
		else
			echo "Floating IP's already created."
		fi
	fi
	
	return 0
}

function assignAllFloatingIPs {
	for x in `nova list | awk '{if ($2 != "ID" && NF>1 && $13 == "|") print $2}'`; 
		do port=`neutron port-list -- --device_id $x | awk '{if ($2 != "id" && NF>1) print $2}'`;
		fip=`neutron floatingip-list | grep '| *|' | head -1 | awk '{print $2}'`;
		neutron floatingip-associate $fip $port;
	done;
}

function hasInstances {
	expectedCount=$1
	instances=`nova list | awk '{if ($2 != "ID" && NF>1) print $4}'`

	if [ ${#instances} -eq 0 ]
	then
		echo "No Instances"
		return -1
	else
		parts=($instances)
		if [ ${#parts[@]} -ne $expectedCount ]
		then
			echo "WARNING: Unexpected Number of instances."
		fi
	fi
	
	return 0
}

function createVolumes {
	count=$1
	name=$2
	volumes=`cinder list | awk '{if ($2 != "ID" && NF>1) print $2}'`

	if [ ${#volumes} -eq 0 ]
	then
		echo "Creating $count Volumes."
		for x in $(seq 1 $count)
		do
			cinder create --display-name "$name-0$x" --display-description "Testing a volume $x" 5
		done
	else
		parts=($volumes)
		if [ ${#parts[@]} -gt $count ]
		then
			echo "WARNING: Too many Volumes."
		elif [ ${#parts[@]} -lt $count ]
		then
			diff=`expr $count - ${#parts[@]}`
			echo "Not enough Volumes, creating $diff more."
			for x in $(seq 1 $diff)
			do
				cinder create --display-name "$name-0$x" --display-description "Testing a volume $x" 5
			done
		else
			echo "Volumes already created."
		fi
	fi
}

function createSnapshots {
	volumes=`cinder list | awk '{if ($2 != "ID" && NF>1) print $2}'`
	snapshots=`cinder snapshot-list | awk '{if ($2 != "ID" && NF>1) print $4}'`

	for vol in $volumes
	do
		exists=`echo $snapshots | grep $vol`
		echo $exists
		if [ ${#exists} -eq 0 ]
		then
			echo "Creating Snapshot of $vol."
			cinder snapshot-create --display-name "snapshot_$vol" --display-description 'Testing a snapshot' $vol
		else
			echo "Snapshot for Volume: $vol already exists."
		fi
	done
}

function createBackups {
	volumes=`cinder list | awk '{if ($2 != "ID" && NF>1) print $2}'`
	backups=`cinder backup-list | awk '{if ($2 != "ID" && NF>1) print $4}'`

	for vol in $volumes
	do
		exists=`echo $backups | grep $vol`
		echo $exists
		if [ ${#exists} -eq 0 ]
		then
			echo "Creating Backup of $vol."
			cinder backup-create --display-name "backup_$vol" --display-description 'Testing a backup.' $vol
		else
			echo "Backup for Volume: $vol already exists."
		fi
	done
}

function createImages {
	instances=`nova list | awk '{if ($2 != "ID" && NF>1) print $4}'`
	images=`glance -k image-list --property-filter owner_id=$OS_TENANT_ID | awk '{if ($2 != "ID" && NF>1) print $4}'`

	for i in $instances
	do
		exists=`echo $images | grep "$i-image"`
		echo $exists
		if [ ${#exists} -eq 0 ]
		then
			echo "Creating Image of $i."
			nova image-create $i "$i-image"
		else
			echo "Image of Instance: $i already exists."
		fi
	done
}

#==============================================================================================================================================================

# Create Resources for Project 1
echo "Creating Resources for Project 1"
export OS_USERNAME=$CODA_USER_1
export OS_TENANT_NAME=$CODA_PROJECT_NAME_1
export OS_TENANT_ID=$CODA_PROJECT_ID_1

# Network for Project 1
hasNetwork

if [ ${#CODA_NETWORK_ID} -eq 0 ]
then
	echo "creating coda-network"
	neutron net-create coda-network
	neutron subnet-create coda-network 10.0.0.0/24 --name coda-subnet
	neutron net-create coda2-net
	neutron subnet-create coda2-net 10.10.0.0/16 --name coda2-subnet
	neutron router-create coda-router
	neutron router-interface-add coda-router coda-subnet
	neutron router-interface-add coda-router coda2-subnet
	neutron router-gateway-set coda-router Ext-Net
	hasNetwork #Make sure we get the variable set when done.
else
	echo "coda-network already created."
fi

# Security Groups for Project 1
echo "Creating Security Groups."
if createSecurityGroup basenode 'The base security group for all nodes.'
then
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 22 --port_range_max 22 --remote-ip-prefix 10.0.0.0/8 basenode
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 9182 --port_range_max 9182 --remote-ip-prefix 10.0.0.0/8 basenode
fi

if createSecurityGroup chef-server 'Opens Chef ports'
then
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 4000 --port_range_max 4000 --remote-ip-prefix 10.0.0.0/8 chef-server
fi

if createSecurityGroup web-server 'Good for a web server'
then
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 80 --port_range_max 80 --remote-ip-prefix 10.0.0.0/8 web-server
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 81 --port_range_max 81 --remote-ip-prefix 10.0.0.0/8 web-server
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 443 --port_range_max 443 --remote-ip-prefix 10.0.0.0/8 web-server
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 8080 --port_range_max 8080 --remote-ip-prefix 10.0.0.0/8 web-server
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 8081 --port_range_max 8081 --remote-ip-prefix 10.0.0.0/8 web-server
fi

if createSecurityGroup email 'email ports'
then
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 25 --port_range_max 25 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 110 --port_range_max 110 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 143 --port_range_max 143 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 465 --port_range_max 465 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 993 --port_range_max 993 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 995 --port_range_max 995 --remote-ip-prefix 10.0.0.0/8 email
	neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 2525 --port_range_max 2525 --remote-ip-prefix 10.0.0.0/8 email
fi

# Instances for Project 1
if hasInstances 4
then
	echo "Instances already created."
else
	echo "Creating instances."
	# Two for user trumpetsherald
	nova boot --flavor $CODA_FLAVOR --image $CODA_IMAGE_1 --key_name $CODA_KEY --availability-zone $CODA_AZ1 --security-groups basenode,web-server --nic net-id=$CODA_NETWORK_ID blogs;
	nova boot --flavor $CODA_FLAVOR --image $CODA_IMAGE_2 --key_name $CODA_KEY --availability-zone $CODA_AZ2 --security-groups basenode,chef-server --nic net-id=$CODA_NETWORK_ID chef-server;

	# Two for user nkimball
	export OS_USERNAME=$CODA_USER_2
	nova boot --flavor $CODA_FLAVOR --image $CODA_IMAGE_3 --key_name $CODA_KEY --availability-zone $CODA_AZ1 --security-groups basenode,email --nic net-id=$CODA_NETWORK_ID email;
	nova boot --flavor $CODA_FLAVOR --image $CODA_IMAGE_4 --key_name $CODA_KEY --availability-zone $CODA_AZ2 --security-groups basenode,web-server --nic net-id=$CODA_NETWORK_ID web-server;
fi

# Floating IP's for Project 1
createFloatingIPs 4

sleep 10

# Assign All the Floating IP's
assignAllFloatingIPs

# Create Volumes for Project 1
createVolumes 2 'test'
echo "I'm sleeping for 30 seconds to allow the instances to build before creating images of them."
sleep 30
#createSnapshots
#createBackups
createImages
#==============================================================================================================================================================