# from zk import ZK, const
# address='192.168.18.210'
# port=4370
# timeout=9

# zk = ZK(address, port=port, timeout=timeout, force_udp=True)
# lo_users=[]
# attend_record=[]

# try:
# 	connection=zk.connect()
# 	print('disabling...')
# 	connection.disable_device()
# 	users=connection.get_users()
# 	for user in users:
# 		lo_users.append([user.user_id, user.name])

# 	attnds=connection.get_attendance()
# 	for att in attnds:
# 		attend_record.append([att.user_id,att.timestamp, att.status, att.punch])

# 	connection.enable_device()
# 	print(attend_record)
# 	print(lo_users)
# except Exception as e:
# 	print('process terminate....{}'.format(e))
# finally:
# 	if connection:
# 		connection.disconnect()



from xmlrpc import client
from zk import ZK, const
from datetime import datetime
def fetch_attendance_data():
#fetch data from machine and returns a flag and properly structured data
	address='192.168.18.210'
	port=4370
	timeout=15
	attend_record=[]
	new_users=[]
	is_same_day=True
	zk = ZK(address, port=port, timeout=timeout, force_udp=True)
	try:
		connection=zk.connect()
		print('Disabling Device...')
		connection.disable_device()
		users=connection.get_users()
		attnds=connection.get_attendance()
		#print(attnds)
		print('Enabling device......')
		connection.enable_device()
	except Exception as e:
		print(e)
		exit()
	#get state:
	last_att_uid=0
	length_arr=len(attnds)-1
	with open('att.rec','r') as lastatt:
		last_att_uid=int(lastatt.readlines()[-1].rstrip())#############################################################
	print('recorde attendance',last_att_uid)
	attnds=attnds[last_att_uid+1:]
	day_rec=[]
	prev_day=''
	current_year=datetime.now().year
	for att in attnds:
		if att.timestamp.year<2021:
			corrected_date=att.timestamp.replace(year=current_year)
			d=corrected_date.strftime("%Y-%m-%d %H:%M:%S")
		else:
			d=att.timestamp.strftime("%Y-%m-%d %H:%M:%S")
		if d[0:10]>prev_day and prev_day != '':#[0:10]use upto seconds only
			attend_record.append(day_rec)
			day_rec=[]
			is_same_day=False
		day_rec.append([att.user_id,d,att.status,att.punch])
		prev_day=d[0:10]
	if day_rec:
		attend_record.append(day_rec)

	#update state

	#last_uid=0##################
	#n_users=users[last_uid:]#############################
	for user in users:
		new_users.append([user.user_id, user.name])


	return attend_record,is_same_day,new_users,length_arr


def main():
	#start_scheduler
	
	attend_record,is_same_day,new_users,length_arr=fetch_attendance_data()
	print(attend_record,is_same_day,new_users)
	current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	#srv="http://localhost:8015"
	srv="https://samadhan05-attendance1.odoo.com"
	#db = 'neafs'
	db = 'samadhan05-attendance1-main-5078117'
	password = 'admin'
	try:
		#common = client.ServerProxy("%s/xmlrpc/2/common" % srv)
		api = client.ServerProxy("%s/xmlrpc/2/object" % srv, allow_none=True)
		#print(common.version())
		if new_users:
			api.execute_kw(db, 2, password, "employee.uid","update_mapper",[new_users])
		api.execute_kw(db, 2, password, "biometric.attendance","fetch_attendance",[attend_record,is_same_day])
		file=open('att.rec','a')
		file.write(str(length_arr)+'\n')
		file.close()
	except Exception as e:
		print(e)
if __name__ == "__main__":
	main()