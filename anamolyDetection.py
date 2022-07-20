#importing modules from bolt and math
import conf, json, time, math, statistics
from boltiot import Sms, Bolt

#computing bounds of thershold ( HIGHER and LOWER )
def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]

#BOLT Object
mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
#SMS Object
sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
#Data List
history_data=[]

while True:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
        print("There was an error while retriving the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue

    print ("The intensity value of the lights in the room is "+data['value'])
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("There was an error while parsing the response: ",e)
        continue

    bound = compute_bounds(history_data,conf.FRAME_SIZE,conf.MUL_FACTOR)
    if not bound:
        required_data_count=conf.FRAME_SIZE-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue

    try:
        if sensor_value > bound[0] :
            print ("The light level increased suddenly.\nLooks like someone turned on lights.\nSending an SMS alert to Mohan.")
            response = sms.send_sms("The light level increased suddenly. Looks like someone turned on lights. If it was you ignore this.")
            print("This is the response ",response)
        elif sensor_value < bound[1]:
            print ("The light level decreased suddenly.\nLooks like someone turned off lights.\nSending an SMS alert to Mohan.")
            response = sms.send_sms("The light level decreased suddenly. Looks like someone turned off lights. If it was you ignore this.")
            print("This is the response ",response)
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(10)
