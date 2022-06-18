# -*- coding: cp1252 -*-
import pandas as pd
from itertools import izip as zip, count # izip for maximum efficiency
import re, sqlite3, time, os,csv
import numpy as np
import MySQLdb as mdb
from itertools import izip as zip, count # izip for maximum efficiency
import re, sqlite3, time, os, datetime, pandas as pd
from Helpers import *
from time import gmtime, strftime
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import defaultdict

hardware=''
speeds=['bytes','kbps','mbps','gbps','tbps']
speed=dict(zip(speeds,xrange(len(speeds))))

class ProcessDataClass():

    def __init__(self):
        self.getlog_error_code=self.fetch_error_codes=self.final_throughput=self.final_throughput=self.exec_count=self.matrix_stats =self.cpu_history=self.cpu_utilization_stats = self.cpu_utilization = self.mem_processor_pool = self.EOL = self.EOS =self.mem_io_pool = self.interfaces_data =self.fail_over_history= self.mem_top_process = ''
        self.subnet = self.failover_monitored=self.agg_traffic= self.agg_traffic1=self.sh_block_LOW=self.sh_block_CNT=self.fail_over_history = self.resourse_usage=self.low1=self.low=self.low2=self.medium=self.medium1=self.medium2=self.medium3=self.critical=self.critical1=''
        self.test=self.loww =self.input_errors=self.loww1=self.ACL =self.show_block=self.ACLC=self.loww2 =self.mediumm=self.ACL_count=self.ACL1=self.mediumm1=self.mediumm2=self.mediumm3=self.criticall=self.criticall1=self.demm=self.demm1=self.demm2=self.traffic_data=self.cpu_utilization_stats_c='' ''
        self.log_time_stamp=self.console_timeout =self.summary_inp =self.summary_output=self.flow_off= self.flow_ON=self.flow_ON_NA=self.fail2 =self.fail1=self.fail_reason=self.ACL_rule_count=''
        self.db_file = self.route = '../db/Firewall_Analyser_BOT_DB.sqlite'        

    def process_data(self, log_file):

        ########
        # Config
        ########
        db_file = self.db_file

        cpu_string = '-- show cpu usage --'
        mem_string = '-- show memory --'
        inf_string = '-- show interfaces --'
        pro_string = '-- show process --'
        pro_end_string = '-- show kernel process --'        
        res_begin='-- show resource usage counter all 1 --'
        res_end='-- show mode --'
        ########

        # Read log file
        log = open(log_file, 'r').readlines()

        # Create result dictionary
        result = dict()
        res2 = dict()
        res3 = dict()
        res4 = dict()
        #################
        # Log file Error Code
        #################
        #read error codes from db
        self.db_error_codes()
        get_error_codes=self.fetch_error_codes        
        error_codesDict=get_error_codes.set_index('error_code').T.to_dict('list')        
       
        # Create temporary  dictionary
        tmpResult=dict()
        for val in error_codesDict: 
            if val in ','.join(log):
                tmpResult[val]=[val,error_codesDict[val][0]]

        result['log_error_code']=tmpResult.values()
        tbl_log_error_code = pd.DataFrame(result['log_error_code'],columns=['error_code','inference'])       

        ########## End - Log file Error Code###############


        ################# 
        # CPU PROCESS LOG
        #################

        ## Extract relevant cpu process data
        # Find "show cpu usage" string in log
        cpu_pos = begins_with(cpu_string, log)

        # Store all the lines till the end of "show process cpu" log
        cpu_end_pos = begins_with('-------', log)

        for i in range(0, len(cpu_end_pos)):
            if cpu_end_pos[i][0] > cpu_pos[0][0]:
                cpu_end_pos = cpu_end_pos[i][0]
                break
        cpu_process_log = log[(cpu_pos[0][0] + 2):(cpu_end_pos - 1)]
        #print cpu_process_log
        cpu_util_data = cpu_process_log[0].replace('\n', '').split(';')

        cpu_utilization_5_sec = cpu_util_data[0].replace('CPU utilization for 5 seconds = ', '')
        cpu_utilization_1_min = cpu_util_data[1].replace(' 1 minute: ','')
        cpu_utilization_5_min = cpu_util_data[2].replace(' 5 minutes: ','')
        ## Append to result
        result['cpu_utilization_5_sec'] = cpu_utilization_5_sec
        result['cpu_utilization_1_min'] = cpu_utilization_1_min
        result['cpu_utilization_5_min'] = cpu_utilization_5_min

        #####################
        # PROCESS MEMORY LOG
        #####################

        ## Extract relevant process memory data
        # Find "show process mem" string in log
        mem_pos = begins_with(mem_string, log)

        # Store all the lines till the end of "show process mem" log
        start_pos = mem_pos[0][0] + 1
        end_pos = mem_pos[0][0] + 6

        mem_process_log = log[start_pos:end_pos]
        f_mem = (mem_process_log[1].replace('Free memory:        ',''))
        f_mem1 = int((f_mem).split(' bytes')[0])
        u_mem = (mem_process_log[2].replace('Used memory:        ',''))
        t_mem = (mem_process_log[4].replace('Total memory:       ',''))
        u_mem1 = int((u_mem).split(' bytes')[0])
        t_mem1 = int((t_mem).split(' bytes')[0])

        Free_memory =GetHumanReadable(f_mem1 )
        Used_memory = GetHumanReadable(u_mem1 )
        Total_memory = GetHumanReadable( t_mem1)

        # Append to result
        result['mem_processor_pool'] = {'total': Total_memory,
                                        'used': Used_memory,
                                        'free': Free_memory}

        #################

        #################
        # INTERFACES DATA
        #################
        inf_pos = begins_with('-- show interface --', log)
        inf_end_pos = begins_with('-------', log)
        for i in range(0, len(inf_end_pos)):
            if (inf_end_pos[i][0] > inf_pos[0][0]):
                inf_end_pos = inf_end_pos[i][0]
                break

        # Extract interfaces related data

        inf_data = log[inf_pos[0][0]:inf_end_pos]

        # Identifying position of interface name
        inf_name_pos = begins_with('line protocol', inf_data)

        # Extract data for each interface
        interfaces = dict()
        for i in range(0, len(inf_name_pos)):
            int_discr=int_device=int_device_state=duplex=sub_net_data=overrun=underruns=Flow_state=Mode='NA'
            inputerror = '0 Input errors'
            inf_name = inf_name_pos[i][1].replace('Interface ','').split(',')[0]
            inf_des = inf_name.split('"')
            interface_name = inf_des[0]
            interface_discription = inf_des[1]
            #print int_discr
            #print int_device
            int_status = inf_name_pos[i][1].split(',')[1].split(' is ')[1]
            line_protocol_status = inf_name_pos[i][1].split(',')[1].split(' is ')[1]
            if int_status and line_protocol_status == 'up':
                interface_state = 'UP'
            else:
                interface_state = 'DOWN'

            
            # Initiate default values for interfaces not having certain parameters

            if inf_name_pos[i][0] < inf_name_pos[len(inf_name_pos) - 1][0]:
                inf_start = inf_name_pos[i][0]
                inf_end = inf_name_pos[i + 1][0]

                # Each interface's details
                inf_details = inf_data[inf_start:inf_end]

                # Duplex
                duplex_details = begins_with('uplex', inf_details)
                if len(duplex_details) != 0:
                    duplex = re.sub('	', '', duplex_details[0][1].split(',')[0])

                # Throughput summary
                #9,077,109 bytes/sec 13,765 packets/sec | Output: 9,701,745 bytes/sec 14,725 packets/sec
                packets_input = begins_with('packets input', inf_details)
                if len(packets_input) != 0:
                    packet = packets_input[0][1].split(',')[0].replace(' packets input','')
                    byte_value = packets_input[0][1].split(',')[1].replace(' bytes','')

                    throughput_sum = 'Throughput summary input : {0} bytes/sec {1} packets/sec'.format(byte_value,packet)

                packets_output = begins_with('packets output', inf_details)
                if len(packets_output) != 0:
                    packet = packets_output[0][1].split(',')[0].replace(' packets output','')
                    byte_value = packets_output[0][1].split(',')[1].replace(' bytes','')

                    throughput_out_sum = "Output : {0}  bytes/sec {1} packets/sec".format(byte_value,packet)
                final_throughput= "{0}|{1}".format(throughput_sum,throughput_out_sum).replace('\t','')


                sub_net_mask = begins_with('subnet mask', inf_details)
                if len(sub_net_mask) !=0:
                    sub_net = sub_net_mask[0][1].split(',')
                    sub_net_data = ('The subnet mask of the ' +sub_net[0]+ ' is '+sub_net[1].replace('subnet mask ','')).replace('\t','')

                overrun_details = begins_with('overrun', inf_details)
                
                
                if len(overrun_details) != 0:
                    #print overrun_details

                    overrun = re.sub('   ', '', overrun_details[0][1].split(',')[3])

                    #overrun2=overrun1.split(" ")
                    #print overrun2
                    #overrun= overrun2[1]
                    #print overrun

                underruns_details = begins_with('underruns', inf_details)
                
                
                if len(underruns_details) != 0:
                    underruns = re.sub('   ', '', underruns_details[0][1].split(',')[2])
                no_buffer_details = begins_with('no buffer', inf_details)
                
                
                if len(no_buffer_details) != 0:
                    no_buffer = re.sub('   ', '', no_buffer_details[0][1].split(',')[2])

                input_queue_hardware_details = begins_with('input queue', inf_details)
                
                
                if len(input_queue_hardware_details) != 0:
                    #print overrun_details

                    input_queue_hardware = re.sub('   ', '', input_queue_hardware_details[0][1].split(':')[1])
                    #print input_queue_hardware
                output_queue_hardware_details = begins_with('output queue', inf_details)
                
                
                if len(output_queue_hardware_details) != 0:
                    #print overrun_details

                    output_queue_hardware = re.sub('   ', '', output_queue_hardware_details[0][1].split(':')[1])
                input_error = begins_with('input errors',inf_details)
                if len(input_error) != 0:
                    i_e = input_error[0][1].lstrip()
                    if i_e.startswith('0'):
                        pass
                    else:
                        inputerror = i_e.split(',')[0]
                auto_v = begins_with('Auto' ,inf_details)

                flow_control = begins_with('flow control is', inf_details)
                if len(flow_control)!=0:
                    flow_off = (flow_control[0][1].split(','))[1]
                    if 'output flow control is off' in flow_off:
                        Flow_state = 'Flow control OFF'
                        if len(auto_v)!=0:
                            Mode = 'Auto'
                        else:
                            Mode = 'Not Auto'
                    elif 'output flow control is on' in flow_off:
                        Flow_state = 'Flow control ON'
                        if len(auto_v)!=0:
                            Mode = 'Auto'                  
                        else:
                            Mode = 'Not Auto'
                    #print output_queue_hardware
            interfaces[i + 1] = {'interface_name': interface_name,
                                 'interface_discription': interface_discription,
                                 'interface_state': interface_state,
                                 'duplex': duplex,
                                 'final_throughput':final_throughput,
                                 'sub_net_data' :sub_net_data,
                                 'overrun':overrun,
                                 'underruns':underruns,
                                 'inputerror':inputerror,
                                 'Flow_state':Flow_state,
                                 'Mode':Mode
                                 }

        result['interfaces_data'] = interfaces

        #################
        # SHOW FAILOVER DATA
        #################
        fail1_pos = begins_with('-- show failover --', log)
        fail1_end_pos = begins_with('-------', log)
        for i in range(0, len(fail1_end_pos)):
            if (fail1_end_pos[i][0] > fail1_pos[0][0]):
                fail1_end_pos = fail1_end_pos[i][0]
                break

        # Extract interfaces related data

        fail1_data = log[fail1_pos[0][0]:fail1_end_pos]
        

        # Identifying position of interface name
        fail1_name_pos = begins_with('This host: Primary', fail1_data)
        #print type(fail1_name_pos)
        if fail1_name_pos !=[]:
            fail1_name_end_pos = begins_with('Other host: Secondary', fail1_data)
            #print inf_name_end_pos
            for i in range(0, len(fail1_name_end_pos)):
                if (fail1_name_end_pos[i][0] > fail1_name_pos[0][0]):
                    fail1_name_end_pos = fail1_name_end_pos[i][0]
                    break
            pri_Mon_int=[]
            fail1_primary_data = fail1_data[inf_name_pos[0][0]:fail1_name_end_pos]
            #print inf_primary_data
            primary_interface = begins_with('Interface',fail1_primary_data)
            for r,r1 in enumerate(primary_interface):
                if '(Not-Monitored)' not in str(r1):
                    r2 = r1[1].split()
                    pri_Mon_int.append(r2[1])     
            
            fail1_name_pos1 = begins_with('Other host: Secondary', fail1_data)
            #print inf_name_pos
            fail1_name_end_pos1 = begins_with('Stateful Failover', fail1_data)
            #print inf_name_end_pos
            for i in range(0, len(fail1_name_end_pos1)):
                if (fail1_name_end_pos1[i][0] > fail1_name_pos1[0][0]):
                    fail1_name_end_pos1 = fail1_name_end_pos1[i][0]
                    break
            sec_Mon_int = []
            fail1_secondary_data = fail1_data[fail1_name_pos1[0][0]:fail1_name_end_pos1]
            #print inf_primary_data
            secondary_interface = begins_with('Interface',fail1_secondary_data)

            for r,r1 in enumerate(secondary_interface):
                if '(Not-Monitored)' in str(r1):
                    r2 = r1[1].split()
                    sec_Mon_int.append(r2[1])


            for p,p1 in enumerate(pri_Mon_int):
                for s,s1 in enumerate(sec_Mon_int):
                    if p1==s1:
                        failover="Interface {0} is Monitored in Primary but not Monitored in Secondary".format(s1)
                        #print failover
                    else:
                        failover='All Interfaces are currently monitored'
        else:
            failover='NA'
         
      

        #######################
        ###Failover history ###
        #######################
        result3 = dict()
        # Find "show show failover history" string in log
        fail_over_history = begins_with('-- show failover history --', log)

        # Store all the lines till the end of "show process cpu" log
        fail_over_ends = begins_with('-------', log)

        for i in range(0, len(fail_over_ends)):
            if (fail_over_ends[i][0] > fail_over_history[0][0]):
                fail_end_pos = fail_over_ends[i][0]
                break
        from dateutil.relativedelta import relativedelta
        from datetime import datetime
        
        today_date = datetime.now()
        one_month_ago = today_date - relativedelta(months=7)
        date_value = one_month_ago.strftime("%b %d %Y")
        date_value = datetime.strptime(date_value, "%b %d %Y")
        date_values =[]
        fail_data = log[fail_over_history[0][0]:fail_end_pos]
        find_dates =[]
        for i_val, fd_val in enumerate(fail_data):            
            date_v = re.findall((r'\w{3}\s+[0-9]{1,2}\s+[0-9]{4}'), fd_val)
            if date_v !=[]:
                dt123 = datetime.strptime(date_v[0], "%b %d %Y")
                if dt123 > date_value:
                    date_values.append(date_v[0])

        f_history = dict()
        time_lines=[]
        fail_data1 = log[fail_over_history[0][0]:fail_end_pos]

      
        if date_values !=[]:
            for i in range(len(fail_data1)):
                for x in date_values:
                    if x in fail_data1[i]:
                        time_lines.append(fail_data1[i+1].strip())
                        
            deded=set(time_lines)
            time_lines=list(deded)

            for i in range(len(time_lines)):
                dat123=filter(None,time_lines[i].split('   '))
                #print dat123
                from_state=dat123[0]
                to_state=dat123[1]
                reason=dat123[2]
                f_history[i+1]={'from_state':from_state,
                                    'to_state':to_state,
                                    'reason':reason
                                    }

        else:
            f_history[i+1]={'from_state':'NA',
                            'to_state':'NA',
                            'reason':'NA'
                            }
        result['f_history']= f_history
        
        #######################
        ###Critical/Medium/Low ###
        #######################
        c_pos = begins_with('-- show running-config --', log)
        c_end_pos = begins_with('------- ', log)

        for i in range(0, len(c_end_pos)):
            if (c_end_pos[i][0] > c_pos[0][0]):
                c_end_pos = c_end_pos[i][0]
                break

        # Extract interfaces related data

        c_data = log[c_pos[0][0]:c_end_pos]

        #severity_starts = begins_with('access-list',log)
        rule_allow = dict()
        critical=dict()
        low = dict()
        medium=dict()
        critical1=dict()
        low1 = dict()
        medium1=dict()        
        low2 = dict()
        medium2=dict()
        medium3=dict()
        rule_check = dict()

        medium[1]={'medium':'NA'}
        medium1[1]={'medium':'NA'}
        medium2[1]={'medium':'NA'}
        medium3[1]={'medium':'NA'}
        low[1]={'low':'NA'}
        low1[1]={'low':'NA'}
        low2[1]={'low':'NA'}
        critical[1]={'critical':'NA'}
        critical1[1]={'critical':'NA'} 
        p_any_any = begins_with('permit ip any any',c_data)
        if len (p_any_any) != 0:
            for c in range(0,len(p_any_any)):
                critical[c+1]={'critical':p_any_any[c][1]}
        p_any_any1= begins_with('deny ip any any log',c_data)
        p_any_any3 = begins_with('deny ip any4 any4 log',c_data)

        # high deny ip any any log(if line not present)
        if len (p_any_any1) == 0 and len (p_any_any3) ==0:
            
            low[1]={'low':"Filter Drop Rules Were Configured Without Logging. It is recommended to enable logging" }
            
        # high permit ip any any 
        p_any_any2 = begins_with('permit ip any any',c_data)
        if len (p_any_any2) != 0:
            for c2 in range(0,len(p_any_any2)):
                critical1[c2+1]={'critical':p_any_any2[c2][1]}

        p_any_any4 = begins_with('permit ip any',c_data)

        for i1,i in enumerate(p_any_any4):            
            if len (i[1]) != 0:
                if 'eq' in i[1]:
                    pass
                elif 'range ' in i[1]:
                    pass
                else:
                    medium[i1+1]={'medium':i[1].lstrip()}

        p_any_any6 = begins_with('permit tcp any',c_data)

        for i1,i in enumerate(p_any_any6):            
            if len (i[1]) != 0:
                if 'eq' in i[1]:
                    pass
                elif 'range ' in i[1]:
                    pass
                else:
                    medium2[i1+1]={'medium':i[1].lstrip()}
        p_any_any7 = begins_with('permit ip any4 host',c_data)
        for i1,i in enumerate(p_any_any7):            
            if len (i[1]) != 0:                
                if (i[1].count('any')) >1 :
                    medium3[i1+1]={'medium':i[1]}
              
        p_any_any8 = begins_with('permit',c_data)
        for i1,i in enumerate(p_any_any8):            
            if len (i[1]) != 0:
                if 'permit tcp any' in i[1] :
                    pass
                elif 'permit tcp any4' in i[1]:
                    pass
                elif 'permit ip any' in i[1]:
                    pass
                elif 'permit ip any4' in i[1]:
                    pass
                elif 'permit tcp' in i[1] or 'permit ip' in i[1]:
                    if i[1].endswith('any'):
                        print i
                        low2[i1+1]={'low':i[1]}
                    
        ip_reverse = begins_with('ip verify reverse-path',c_data)
        if len(ip_reverse) ==0:
            low1[1]={'low':'There is no ip verify reverse-path'}
        strings = (' eq 25 ' or ' eq 80 ' or ' eq 49' or ' eq 21' or ' eq 23 ' or ' eq www' or ' eq ftp' or ' eq smtp' or ' eq telnet' )
        for x,line1 in enumerate((c_data)):
            line = line1.replace('\n','')
            if 'eq 25 ' in line:
                #print line
                medium1[x+1]={'medium':line}
            elif ' eq 49 ' in line:
                medium1[x+1]={'medium':line}
            elif ' eq 21 ' in line:
                medium1[x+1]={'medium':line}
            elif ' eq 23 ' in line:
                medium1[x+1]={'medium':line}
            elif 'eq ftp' in line:
                medium1[x+1]={'medium':line}
            elif 'eq smtp' in line:
                medium1[x+1]={'medium':line}
            elif 'eq telnet' in line:
                medium1[x+1]={'medium':line}
        result['critical']= critical
        result['critical1']= critical1
        result['low']= low
        result['low1']= low1
        result['low2']= low2
        result['medium']= medium
        result['medium1']= medium1
        result['medium2']= medium2
        result['medium3']= medium3

        
        ####access-group####
        ACL=dict()
        ACL1=0
        x = 0
        c_data1 = begins_with('access-group',c_data)
        for i, access_list_v in enumerate(c_data1):
            #print access_list_v[1]
            list_v = access_list_v[1].replace('access-group ','').split()[0]
            for x,list1 in enumerate(begins_with('access-list '+list_v,c_data)):
                final_ACL = list_v 
                rule_count = (x + 1)

                #print str(x + 1)
                ACL[i+1]={'ACL':final_ACL,
                          'rule':rule_count}

            ACL1 = ACL1 +(x+1)

        result['ACL']=ACL

        ####################
        ### Show-Process ###
        ####################
        showpro = dict()
        pro_pos = begins_with(pro_string, log)
        pro_end_pos = begins_with(pro_end_string, log)
        show_pro_log = log[pro_pos[0][0]+3:pro_end_pos[0][0]-1]
        
        g=[]
        a=show_pro_log[0].split()
        a.insert(0, 'SNo')
        d=dict()
        for i in range(0,len(a)):
            d[a[i]]=[]
        for i in range(1,len(show_pro_log)):
            g=show_pro_log[i].split()
            if('-' in g):
                break
            for j in range(0,len(a)):
                d[a[j]].append(g[j])

        for i in range(len(d[a[0]])):
                       sno=d[a[0]][i]
                       pc=d[a[1]][i]
                       sp=d[a[2]][i]
                       state=d[a[3]][i]
                       runtime=d[a[4]][i]
                       sbase=d[a[5]][i]
                       stack=d[a[6]][i]
                       process=d[a[7]][i]
    
                       showpro[i+1] = {'runtime':runtime,
                                       'process':process
                                       }
                       
        res2['processData'] = showpro
       #################
        # Show traffic
        #################
        def comparevalue(main_value, compared_value):

            if (compared_value != 0):

                main_value1 = GetHumanReadable1(int(main_value))
                                                                
                main_value2 = main_value1.split(' ')
                # print main_value2
                compared_value1 = compared_value.split(' ')
                # print compared_value1
                critical = "Firewall current Throughput value is "+(main_value1)+" and it is within the Firewall spec limit of "+compared_value
                if (speed[main_value2[1].lower()] < speed[compared_value1[1].lower()]):
                    main_value2[1], "is less than", compared_value1[1]
                elif (speed[main_value2[1].lower()] == speed[compared_value1[1].lower()]):
                    main_value2[1], "is same as", compared_value1[1]
                    cv_80 = 0.8 * float(compared_value1[0])
                    cv_80, "value is 80% of hardware value", compared_value1[0]
                    mv = float(main_value2[0])
                    if (mv < cv_80):
                        mv, type(mv), cv_80, type(cv_80)
                        main_value2[0], "value is less than of 80 % ", compared_value1[0]
                    elif (float(main_value2[0]) >= cv_80):
                        float(main_value2[0]), "value is greater than of 80 % ", compared_value1[0]
                        critical = "Firewall current Throughput value is "+(main_value1)+" and it reached above 80% of Firewall througput limit "+compared_value
                elif (speed[main_value2[1].lower()] > speed[compared_value1[1].lower()]):
                    main_value2[1], " greater than ", compared_value1[1]
                    critical = main_value2
                    critical = ' '.join(critical)
                return critical
        def comparef(main_value, compared_value):

            if (compared_value != 0):
                critical = "NA"
                main_value1 = GetHumanReadable1(int(main_value))
                                                                
                main_value2 = main_value1.split(' ')
                # print main_value2
                compared_value1 = compared_value.split(' ')
                # print compared_value1
                if (speed[main_value2[1].lower()] < speed[compared_value1[1].lower()]):
                    main_value2[1], "is less than", compared_value1[1]
                elif (speed[main_value2[1].lower()] == speed[compared_value1[1].lower()]):
                    main_value2[1], "is same as", compared_value1[1]
                    cv_80 = 0.8 * float(compared_value1[0])
                    cv_80, "value is 80% of hardware value", compared_value1[0]
                    mv = float(main_value2[0])
                    if (mv < cv_80):
                        mv, type(mv), cv_80, type(cv_80)
                        main_value2[0], "value is less than of 80 % ", compared_value1[0]
                    elif (float(main_value2[0]) >= cv_80):
                        float(main_value2[0]), "value is greater than of 80 % ", compared_value1[0]
                        critical = main_value2
                        critical = ' '.join(critical)
                        # print "------------------"
                        # print critical
                elif (speed[main_value2[1].lower()] > speed[compared_value1[1].lower()]):
                    main_value2[1], " greater than ", compared_value1[1]
                    critical = main_value2
                    critical = ' '.join(critical)
                    # print "--------------------"
                    # print critical
                return critical
        hardware_name = begins_with('Hardware: ', log)
        if len(hardware_name) != 0:
            hardware = hardware_name[0][1].split(',')[0].replace('Hardware:   ','')
        def get_input(csv_file, column_value):
            columns = defaultdict(list)
            with open(csv_file) as csvfile:
                Csreader = csv.DictReader(csvfile)
                for row in Csreader:
                    for (k,v) in row.items():
                        columns[k].append(v)
                        column_output = columns[column_value]
            return column_output
        
        traffic_value = get_input('../db/ASA_Details.csv', hardware)[0]            
        agg_pos = begins_with('Aggregated Traffic on', log)
        agg_end_pos = begins_with('------------------ show ', log)
        for i in range(0, len(agg_end_pos)):
            if (agg_end_pos[i][0] > agg_pos[0][0]):
                agg_end_pos = agg_end_pos[i][0]
                break


        agg_data = log[agg_pos[0][0]:agg_end_pos]

        # Identifying position of interface name
        agg_name_pos = begins_with('bytes/sec', agg_data)

        agg_v = []
        for i in range(0, len(agg_name_pos)):
            if 'minute' not in agg_name_pos[i][1]:
                agg_v1 = (agg_name_pos[i][1].split())[2]
                agg_v.append(agg_v1)
        summary_input =0
        summary_out =0
        input_rec = agg_v[1::2]
        for row in input_rec:
            summary_input= summary_input + int(row)
        output_rec = agg_v[::2]
        for row in output_rec:
            summary_out= summary_out + int(row)
         
        agg_inital = 0
        for row in agg_v:
            agg_inital= agg_inital + int(row)
        a_traffic1 = comparevalue(agg_inital,traffic_value)
        a_traffic = a_traffic1            

        hv = traffic_value
        tra_pos = begins_with('Aggregated Traffic on Physical Interface', log)
        tra_end_pos = begins_with('--------', log)
        for i in range(0, len(tra_end_pos)):
            if (tra_end_pos[i][0] > tra_pos[0][0]):
                tra_end_pos = tra_end_pos[i][0]
                break

        # Extract interfaces related data

        tra_data = log[tra_pos[0][0]:tra_end_pos]
        
        a = len(tra_data)
        c = 2
        inf_n = []
        inf1 = []

        for i in range(0, (len(tra_data) - 1)):
            if len(tra_data) != 0:

                if (i == c):

                    a = tra_data[c]
                    c = c + 13
                    b = tra_data[i:c]
                    inf2 = []
                    interface_name_m = tra_data[i]
                    tra_1_input = begins_with('1 minute input rate', b)
                    tra_1i = tra_1_input[0][1].split(',')[1]
                    value = 0
                    tra1i = tra_1i.replace(' bytes/sec', '').replace('  ', '')
                    # print tra1i
                    critical_1_input = comparef(tra1i, hv)

                    tra_1_output = begins_with('1 minute output rate', b)
                    output_1 = "1 minute output rate"
                    # inf2.append(output_1)
                    tra_1o = tra_1_output[0][1].split(',')[1]
                    tra1o = tra_1o.replace(' bytes/sec', '').replace('  ', '')
                    # print tra1o
                    critical_1_output = comparef(tra1o, hv)

                    tra_5_input = begins_with('5 minute input rate', b)
                    input_5 = "5 minute input rate"
                    # inf2.append(input_5)
                    tra_5i = tra_5_input[0][1].split(',')[1]
                    tra5i = tra_5i.replace(' bytes/sec', '').replace('  ', '')
                    # print tra5i
                    critical_5_input = comparef(tra5i, hv)

                    # print "--------5 minute output rate---------"
                    tra_5_output = begins_with('5 minute output rate', b)
                    output_5 = "5 minute output rate"
                    # inf2.append(output_5)
                    tra_5o = tra_5_output[0][1].split(',')[1]
                    tra_5o = tra_5o.replace(' bytes/sec', '').replace('  ', '')
                    # print tra_5o
                    critical_5_output = comparef(tra_5o, hv)

                    inf2.append(interface_name_m)

                    inf2.append(critical_1_input)

                    inf2.append(critical_1_output)

                    inf2.append(critical_5_input)

                    inf2.append(critical_5_output)

                    inf2.append(interface_name_m)
                    if c > len(tra_data):
                        break
                    inf1.append(inf2)
        show_traffic = dict()
        print (inf1)
        for i in range(0, len(inf1)):
            interface_name = inf1[i][0].split(':')[0]
            i1_minute_input_rate = inf1[i][1]
            o1_minute_output_rate = inf1[i][2]
            i5_minute_input_rate = inf1[i][3]
            o5_minute_output_rate = inf1[i][4]
            show_traffic[i + 1] = {'interface_name': interface_name,
                                   'minute_1_input_rate': i1_minute_input_rate,
                                   'minute_1_output_rate': o1_minute_output_rate,
                                   'minute_5_input_rate': i5_minute_input_rate,
                                   'minute_5_output_rate': o5_minute_output_rate
                                   }

        result['traffic_data'] = show_traffic


        #################
        # OVERVIEW
        #################

        config_register = hostname = uptime = image_version = device_info = config_changed = hardware =licensedetail='NA'


        config_register_pos = begins_with('Configuration register is', log)
        if len(config_register_pos) != 0:
            config_register = config_register_pos[0][1].split('is ')[1]
            
        hostname_pos = begins_with('hostname', log)

        if len(hostname_pos) != 0:
                hostname = hostname_pos[0][1].split('hostname ')[1]

        uptime_pos = begins_with(hostname + ' up', log)

        if len(uptime_pos) != 0:
            uptime = uptime_pos[0][1].split(' up ')[1]

        device_info_pos = begins_with('Software Version', log)
        if len(device_info_pos) != 0:
            device_info = log[device_info_pos[0][0]]


        image_version_pos = begins_with('image file is', log)
        if len(image_version_pos) != 0:
            image_version = image_version_pos[0][1].split('System image file is ')[1]

        configuration_last_modified = begins_with('Configuration last modified by ', log)
        configuration_not_modified = begins_with('Configuration has not been modified', log)

        if len(configuration_last_modified) !=0:    
            config_changed = configuration_last_modified[0][1].split('Configuration last modified by ')[1]

        elif len(configuration_not_modified) !=0:
            config_changed = configuration_not_modified[0][1]
        hardware_name = begins_with('Hardware: ', log)
        if len(hardware_name) != 0:
            hardware = hardware_name[0][1].split(',')[0].replace('Hardware:   ','')
        License_detail = begins_with('This platform has an', log)
        if len(License_detail) !=0:
            licensedetail = License_detail[0][1].replace('This platform has an ','')

        ####################
        ####EOL and EOS#####
        ####################
        
        sowtware_version  = device_info.replace('Cisco Adaptive Security Appliance Software Version ','')
       
        sw = (sowtware_version).split("(")
        sw1 = sw[0]
        csv_file = csv.reader(open('../db/Firewall_EOL_EOS.csv', "rb"), delimiter=",")
        for row in csv_file:
            if row[0] == sw1:
                asa = row

        EOL = asa[1]
        EOS = asa[2]
        ##############
        ####route#####
        ##############


        #print rou_int_log
        z=[]
        def areSame(a, b):

            for line in fail1_data:
                if ' Interface ' in line:
                    z=line.strip().split(' ')
                    if 'Interface' in z:
                        h=re.findall(r'(\d+.\d+.\d+).\d+',z[2])
                        if(z[1]==a and h[0]==b):
                            return True
                    
            return False
                

        d = dict()
        
        i=0
        roudict=dict()
        roudict[1]={'route_ip':'NA'}
        b=[]
        c=[]
        c1=[]
        for line in begins_with('route ',log):
            if line[1].startswith('route '):
                
                a1=line[1].rstrip()
                a = a1.split()
                if(a[4] in b):
                    pass
                else:
                    #print a
                    b.append(a[4])
                    k=a[4]
                    k=re.findall(r'(\d+.\d+.\d+).\d+',k)
                    c.append(k[0])
                    c1.append(a[4])
                    
        #print roudict
        
        #############
        #+++++++++++#
        #############

        inter_begin = begins_with("IP address",log)
        #print inter_begin
        l=[]
        for i in range(len(inter_begin)):
            if inter_begin[i][1].split()[2]!="unassigned":
                k=inter_begin[i][1].split()[2]
                k=re.findall(r'(\d+.\d+.\d+).\d+',k)
                if k[0] not in l:
                    l.append(k[0])
        print l
        print c
        for i3,(i1,i2) in enumerate(zip(c,c1)):
            if i1 not in l:
                roudict[i3+1]={'route_ip':i2}
                i3+=1

        res4['route']=roudict

                
        #####---#####
        if "logging timestamp" in open(log_file).read():
            log_time_stamp =  'Logging timestamp was configured'
        else:
            log_time_stamp = 'Logging timestamp was not configured which can make log analysis difficult'
        ####===####
        if "console timeout" in open(log_file).read():
            console_timeout= 'Console timeout was configured'
        else:
            console_timeout ='Console timeout was disabled on this device. Improve the security posture of the device by enforcing a console timeout'
        #print cnt
        ######################
        ##show resourse usage#
        ######################
       
        respon = dict()
        store=0
        header=[]
        peak=[]
        respon[1]={'resourse':'NA',
                    'current':'NA',
                    'peak':'NA',
                    'limit':'NA',
                    'denied':'NA',
                    'context':'NA'
                    }
        res3['resourse_usage']=respon


        res_pos = begins_with(res_begin, log)
        res_end_pos = begins_with('-------', log)
        for i in range(0, len(res_end_pos)):
            if (res_end_pos[i][0] > res_pos[0][0]):
                res_end_pos = res_end_pos[i][0]
                break
        
        # Extract interfaces related data

        r_data = log[res_pos[0][0]:res_end_pos -1]
        #print r_data
        h_value = get_input('../db/ASA_Details.csv', hardware)
        if len(h_value)!=0:
            print 'Insise'
            store=int(get_input('../db/ASA_Details.csv', hardware)[1])
            store=store*.85
            d=dict()
            a = r_data[2].split()
            print a
            g=[]
            cnt44=0
            for x1,x in enumerate(r_data):
                if x1 >= 3:
                    g=x.split()
                    store2=int(g[2])
                    print store,store2
                    if(store2>=store):
                        for i in range(1):
                            resourse=g[0]
                            print resourse
                            current=g[1]
                            peak=g[2]
                            limit=g[3]
                            denied=g[4]
                            context=g[5]
                            respon[i+1]={'resourse':resourse,
                                         'current':current,
                                         'peak':peak,
                                         'limit':limit,
                                         'denied':denied,
                                         'context':context
                                        }
                
            res3['resourse_usage']=respon
            print respon
        #################
        ## Show Blocks ##
        #################
        blocks_begin = begins_with('------ show blocks -----',log)
        blocks_end = begins_with('65536',log)
        for i in range(0, len(blocks_end)):
            if (blocks_end[i][0] > blocks_begin[0][0]):
                blocks_end = blocks_end[i][0]
                break
        block_data = log[(blocks_begin[0][0]+3):(blocks_end+1)]
        sh_block = dict()

            
        for i,row in enumerate(block_data):
            block_value = row.split()
            b_size = block_value[0]
            b_max = block_value[1]
            b_low = block_value[2]
            b_cnt = block_value[3]
            sh_block[i+1]={'SIZE':b_size,
                           'MAX':b_max,
                           'LOW':b_low,
                           'CNT':b_cnt
                           }
                           
        result['Show_blocks']=sh_block

        ##################################
        ## Store results in DataFrames  ##
        ##################################
        # CPU
        tbl_cpu_utilization_stats = pd.DataFrame({'five_sec': result['cpu_utilization_5_sec'],
                                                  'one_min': result['cpu_utilization_1_min'],
                                                  'five_min': result['cpu_utilization_5_min']},
                                                 index=['cpu_utilization_stats'])

        # Memory
        tbl_mem_processor_pool = pd.DataFrame(result['mem_processor_pool'], index=['processor_pool'])

        # Interfaces
        tbl_interfaces = pd.DataFrame(columns=interfaces.values()[0].keys())
        for inf in result['interfaces_data'].values():
            tbl_interfaces = tbl_interfaces.append(pd.Series(inf), ignore_index=True)
        # show_blocks
        tbl_sh_blocks = pd.DataFrame(columns=sh_block.values()[0].keys())
        for inf in result['Show_blocks'].values():
            tbl_sh_blocks = tbl_sh_blocks.append(pd.Series(inf), ignore_index=True)
        # a_traffic
        tbl_a_traffic = pd.DataFrame({'a_traffic':a_traffic},index=[0])
        
        # Overview
        tbl_overview = pd.DataFrame({'config_register': config_register,
                                     'hostname': hostname,
                                     'uptime': uptime,
                                     'image_version': image_version,
                                     'config_changed': config_changed,
                                     'device_info': device_info,
                                     'hardware':hardware,
                                     'License':licensedetail},index=[0])
        
        tbl_monitored_failover = pd.DataFrame({'not_monitored': failover},index=['Failover_monitored'])
        # Fail over history
        tbl_fail_over_history = pd.DataFrame(columns=f_history.values()[0].keys())
        for inf in result['f_history'].values():
            tbl_fail_over_history = tbl_fail_over_history.append(pd.Series(inf), ignore_index=True)
        

        # EOL and EOS
        tbl_EOL = pd.DataFrame({'EOL':EOL},index=[0])

        tbl_EOS = pd.DataFrame({'EOS':EOS},index=[0])

        tb1_ACL1= pd.DataFrame({'ACL1':ACL1},index=[0])
        tb1_summary_input= pd.DataFrame({'summary_input':summary_input},index=[0])        
        tb1_summary_out= pd.DataFrame({'summary_out':summary_out},index=[0]) 
        tb1_log_time_stamp = pd.DataFrame({'log_time_stamp':log_time_stamp},index=[0])
        tb1_console_timeout = pd.DataFrame({'console_timeout':console_timeout},index=[0])
     
        #Show-Process
        tbl_showprocess = pd.DataFrame(columns=showpro.values()[0].keys())
        for row in res2['processData'].values():
            tbl_showprocess = tbl_showprocess.append(pd.Series(row), ignore_index=True)

        #Fail_over config
            
        tbl_critical= pd.DataFrame(columns=critical.values()[0].keys())        
        for row in result['critical'].values():
            tbl_critical = tbl_critical.append(pd.Series(row), ignore_index=True)

        tbl_critical1= pd.DataFrame(columns=critical1.values()[0].keys())        
        for row in result['critical1'].values():
            tbl_critical1 = tbl_critical1.append(pd.Series(row), ignore_index=True)

        tbl_low= pd.DataFrame(columns=low.values()[0].keys())        
        for row in result['low'].values():
            tbl_low = tbl_low.append(pd.Series(row), ignore_index=True)

        tbl_low1= pd.DataFrame(columns=low1.values()[0].keys())        
        for row in result['low1'].values():
            tbl_low1 = tbl_low1.append(pd.Series(row), ignore_index=True)

        tbl_low2= pd.DataFrame(columns=low2.values()[0].keys())        
        for row in result['low2'].values():
            tbl_low2 = tbl_low2.append(pd.Series(row), ignore_index=True)

        tbl_medium= pd.DataFrame(columns=medium.values()[0].keys())        
        for row in result['medium'].values():
            tbl_medium = tbl_medium.append(pd.Series(row), ignore_index=True)

        tbl_medium1= pd.DataFrame(columns=medium1.values()[0].keys())        
        for row in result['medium1'].values():
            tbl_medium1 = tbl_medium1.append(pd.Series(row), ignore_index=True)

        tbl_medium2= pd.DataFrame(columns=medium2.values()[0].keys())        
        for row in result['medium2'].values():
            tbl_medium2 = tbl_medium2.append(pd.Series(row), ignore_index=True)

        tbl_medium3= pd.DataFrame(columns=medium3.values()[0].keys())        
        for row in result['medium3'].values():
            tbl_medium3 = tbl_medium3.append(pd.Series(row), ignore_index=True)           

        #access_list
        tbl_ACL = pd.DataFrame(columns=ACL.values()[0].keys())

        for row in result['ACL'].values():
            tbl_ACL = tbl_ACL.append(pd.Series(row),ignore_index=True)
        #Resourse-usage
        tbl_resourse_usage= pd.DataFrame(columns=respon.values()[0].keys())
        for row in res3['resourse_usage'].values():
            tbl_resourse_usage = tbl_resourse_usage.append(pd.Series(row), ignore_index=True)

        #route
        tbl_route= pd.DataFrame(columns=roudict.values()[0].keys())
        for row in res4['route'].values():
            tbl_route = tbl_route.append(pd.Series(row), ignore_index=True)
            
        tbl_show_traffic = pd.DataFrame(columns=show_traffic.values()[0].keys())
        for inf in result['traffic_data'].values():
            tbl_show_traffic = tbl_show_traffic.append(pd.Series(inf), ignore_index=True)
        ##################################
        ## Export all DataFrames to SQLite
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        to_db(dataframe=tbl_cpu_utilization_stats,
              db_table='cpu_utilization_stats',
              db_conn=conn,
              log_file=log_file)
        
        to_db(dataframe=tbl_interfaces,
              db_table='interfaces_data',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_show_traffic,
              db_table='traffic_data',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_mem_processor_pool,
              db_table='mem_processor_pool',
              db_conn=conn,
              log_file=log_file)
        
        to_db(dataframe=tbl_log_error_code,
              db_table='log_error_code',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_monitored_failover,
              db_table='Failover_monitored',
              db_conn=conn,
              log_file=log_file)

        to_db(dataframe=tbl_fail_over_history,
              db_table='fail_over_history',
              db_conn=conn,
              log_file=log_file)

        to_db(dataframe=tbl_overview,
              db_table='overview',
              db_conn=conn,
              log_file=log_file)
        
        to_db(dataframe=tbl_EOL,
              db_table='EOL',
              db_conn=conn,
              log_file=log_file)
        
        to_db(dataframe=tbl_EOS,
              db_table='EOS',
              db_conn=conn,
              log_file=log_file)
        
        to_db(dataframe=tb1_ACL1,
              db_table='ACL1',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_showprocess,
              db_table='processData',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_resourse_usage,
              db_table='resourse_usage',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_route,
              db_table='route',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_critical,
              db_table='critical',
              db_conn=conn,
              log_file=log_file)

        to_db(dataframe=tbl_critical1,
              db_table='critical1',
              db_conn=conn,
              log_file=log_file)

        to_db(dataframe=tbl_low,
              db_table='low',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_low1,
              db_table='low1',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_low2,
              db_table='low2',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_medium,
              db_table='medium',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_medium1,
              db_table='medium1',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_medium2,
              db_table='medium2',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_medium3,
              db_table='medium3',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_ACL,
              db_table='ACL',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_sh_blocks,
              db_table='Show_blocks',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tbl_a_traffic,
              db_table='a_traffic',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tb1_log_time_stamp,
              db_table='log_time_stamp',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tb1_console_timeout ,
              db_table='console_timeout',
              db_conn=conn,
              log_file=log_file)
        to_db(dataframe=tb1_summary_input,
              db_table='summary_input',
              db_conn=conn,
              log_file=log_file)        
        to_db(dataframe=tb1_summary_out,
              db_table='summary_out',
              db_conn=conn,
              log_file=log_file)
        # Close the connection
        conn.close()

    def db_error_codes(self):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'

        # Connect to DB
        conn = sqlite3.connect(db_file)

        # Read data        
        self.fetch_error_codes = pd.read_sql('select error_code, inference from error_code_tbl', conn)
        conn.close()

    #fetch log error codes
    def show_log_error_codes(self, log_file):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'

        # Connect to DB
        conn = sqlite3.connect(db_file)

        # Read data
        self.getlog_error_code = pd.read_sql('select * from log_error_code where log_file="' + log_file + '"', conn)              
        

        # Close the connection to DB
        conn.close()
        

    def fetch_data(self, log_file):
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'
        conn = sqlite3.connect(db_file)
        self.overview = pd.read_sql('select * from overview where log_file="' + log_file + '"', conn)
        self.cpu_utilization_stats = pd.read_sql('select * from cpu_utilization_stats where log_file="' + log_file + '"',
                                            conn)
        self.cpu_utilization_stats_c = pd.read_sql('select five_sec as five_sec,one_min as one_min,five_min as five_min from cpu_utilization_stats where log_file="' + log_file + '"',
        conn)
        self.cpu_utilization_stats_c['one_min']= self.cpu_utilization_stats_c['one_min'].str.zfill(3)
        self.cpu_utilization_stats_c['five_min'] =self.cpu_utilization_stats_c['five_min'].str.zfill(3)
        self.cpu_utilization_stats_c['five_sec'] =self.cpu_utilization_stats_c['five_sec'].str.zfill(3)
        self.cpu_utilization_stats_c.one_min[self.cpu_utilization_stats_c.one_min <"80%"]="NA"
        self.cpu_utilization_stats_c.five_min[self.cpu_utilization_stats_c.five_min < "80%"] = "NA"
        self.cpu_utilization_stats_c.five_sec[self.cpu_utilization_stats_c.five_sec < "80%"] = "NA"

        if self.cpu_utilization_stats_c['one_min'][0] and self.cpu_utilization_stats_c['five_min'][0] and self.cpu_utilization_stats_c['five_sec'][0] == 'NA':
            self.cpu_utilization_stats_c = 'CPU Utilization is normal'
        self.traffic_data = pd.read_sql('select interface_name as interface_name,minute_1_input_rate as minute_1_input_rate,minute_5_input_rate as minute_5_input_rate, \
                                        minute_1_output_rate as minute_1_output_rate, minute_5_output_rate as minute_5_output_rate  from traffic_data \
                                        where minute_5_output_rate != "NA" OR minute_1_output_rate != "NA" OR  \
                                        minute_1_input_rate != "NA" OR minute_5_input_rate != "NA" AND log_file="'+ log_file + '"',conn)
        subQry="select 'Memory utilization' as Memory,total as Total,used as Used,free as Free from mem_processor_pool where log_file='" +log_file + "'"
        testr = pd.read_sql(subQry , conn)
        self.mem_processor_pool = testr
        self.interfaces_data = pd.read_sql('select interface_name as "Interface Name",interface_discription as "Interface discription" ,interface_state as "Interface state",duplex as "duplex state" from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%"))  and log_file="' + log_file + '"', conn)
        self.final_throughput = pd.read_sql("select interface_name as 'Interface Name',final_throughput as 'Throughput' from interfaces_data where log_file='"+ log_file + "'",conn)
        self.subnet = pd.read_sql("select interface_name as 'Interface Name', sub_net_data as subnet from interfaces_data where log_file='"+ log_file + "'",conn)
        self.failover_monitored = pd.read_sql('select not_monitored as "Not-Monitored"from Failover_monitored where (not_monitored <>"NA") and log_file="' + log_file + '"', conn)

        self.load = pd.read_sql('select interface_name as "Interface Name", inputerror as "Input error",overrun as Overrun,underruns as Underruns from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%")) and (overrun <> "NA" AND underruns <> "NA") AND (overrun <> " 0 overrun" OR underruns <> " 0 underruns" )AND log_file="'+ log_file + '"',conn)
        self.fail_over_history = pd.read_sql('select from_state as "From State" ,to_state as "To state",reason as "Reason" from fail_over_history where log_file="' + log_file + '"', conn)
        self.fail_reason = pd.read_sql('select reason from fail_over_history where log_file="' + log_file + '"', conn)

        self.fail1 = pd.read_sql('select reason from fail_over_history where (reason = "HELLO not heard from mate") and log_file="' + log_file + '"', conn)
        self.fail2 = pd.read_sql('select reason from fail_over_history where (reason = "Configuration mismatch due to wr standby in active") and log_file="' + log_file + '"', conn)
        self.fail_reason = 'There is no failover reason'
        if len(self.fail1)!=0:
            self.fail_reason = 'Failover history has "HELLO not heard from mate"'
        elif len(self.fail2)!=0:
            self.fail_reason = 'Failover history has "Configuration mismatch due to wr standby in active"'

        self.resourse_usage = pd.read_sql('select peak as "Peak Value",resourse as "Resource" from resourse_usage where (peak <> "NA") AND (resourse <> "NA") and log_file="' + log_file + '"',conn)
        print self.resourse_usage
        self.input_errors = pd.read_sql('select interface_name as "Interface Name",inputerror as "input error" from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%")) and (inputerror <> "NA") AND log_file="'+ log_file + '"',conn)
        self.flow_off = pd.read_sql('select interface_name as "Interface Name",Flow_state as Flow_State, Mode as Mode from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%")) and (Flow_state = "Flow control OFF") and (Mode = "Auto") AND log_file="'+ log_file + '"',conn)
        self.flow_ON = pd.read_sql('select interface_name as "Interface Name",Flow_state as Flow_State, Mode as Mode from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%")) and (Flow_state = "Flow control ON") and (Mode = "Auto") AND log_file="'+ log_file + '"',conn)
       
        self.flow_ON_NA = pd.read_sql('select interface_name as "Interface Name",Flow_state as Flow_State, Mode as Mode from interfaces_data where ((interface_name like "%ethernet%") or (interface_name like "%management%")) and (Flow_state = "Flow control ON") and (Mode = "Not Auto") AND log_file="'+ log_file + '"',conn)
        self.EOL = pd.read_sql('select * from EOL where log_file="' + log_file + '"', conn)
        self.EOS = pd.read_sql('select * from EOS where log_file="' + log_file + '"', conn)
        self.ACL1 = pd.read_sql('select ACL1 as ACL1 from ACL1 where log_file="' + log_file + '"', conn)
        self.processData = pd.read_sql('select process as "Process Name", runtime as runtime from processData where (process <> "NA") and log_file="' + log_file + '" order by runtime*1 desc limit 1',conn)

        self.low1 = pd.read_sql('select low as low from low1 where (low <> "NA" ) and log_file="' + log_file + '"',conn)
        self.low = pd.read_sql('select low as "Risk rating : High" from low where (low <> "NA" ) and log_file="' + log_file + '"',conn)
        self.low2 = pd.read_sql('select low as "Risk value: Low" from low2 where (low <> "NA" ) and log_file="' + log_file + '"',conn)
        self.medium = pd.read_sql('select medium as "Risk value: Medium" from medium where (medium <> "NA" ) and log_file="' + log_file + '" union select medium as medium from medium2 where (medium <> "NA" ) and log_file="' + log_file + '"',conn)        
        self.medium1 = pd.read_sql('select medium as "Risk rating : Medium" from medium1 where (medium <> "NA" ) and log_file="' + log_file + '"',conn)
        #self.medium2 = pd.read_sql('select medium as medium from medium2 where (medium <> "NA" ) and log_file="' + log_file + '"',conn)
        #self.medium3 = pd.read_sql('select medium as medium from medium3 where (medium <> "NA" ) and log_file="' + log_file + '"',conn)
        #self.critical = pd.read_sql('select critical as critical from critical where (critical <> "NA" ) and log_file="' + log_file + '"',conn)
        self.critical1 = pd.read_sql('select critical as "Risk rating : High" from critical1 where (critical <> "NA" ) and log_file="' + log_file + '"',conn)
        cur = conn.cursor()
        self.loww=pd.read_sql('select count(*) from low where low<>"NA" and log_file="'+log_file+'"',conn)
        self.loww1=pd.read_sql('select count(*) from low1 where low<>"NA" and log_file="'+log_file+'"',conn)
        self.loww2=pd.read_sql('select count(*) from low2 where low<>"NA" and log_file="'+log_file+'"',conn)
        self.mediumm=pd.read_sql('select count(*) from medium where medium<>"NA" and log_file="'+log_file+'"',conn)
        self.mediumm1=pd.read_sql('select count(*) from medium1 where medium<>"NA" and log_file="'+log_file+'"',conn)
        #self.mediumm2=pd.read_sql('select count(*) from medium2 where medium<>"NA" and log_file="'+log_file+'"',conn)
        #self.mediumm3=pd.read_sql('select count(*) from medium3 where medium<>"NA" and log_file="'+log_file+'"',conn)
        #self.criticall=pd.read_sql('select count(*) from critical where critical<>"NA" and log_file="'+log_file+'"',conn)
        self.criticall1=pd.read_sql('select count(*) from critical1 where critical<>"NA" and log_file="'+log_file+'"',conn)
        self.ACL=pd.read_sql('select distinct ACL as ACL_list ,rule as rule from ACL where log_file="' + log_file + '"order by rule desc limit 10',conn)
        self.ACL_rule_count = sum(self.ACL['rule'])
        print self.ACL_rule_count
        self.ACL_count = pd.read_sql('select count(*) from ACL where log_file="' + log_file + '"',conn)
        self.ACLC = (self.ACL_count)['count(*)'][0]
        self.show_block = pd.read_sql('select SIZE as SIZE , MAX as MAX,LOW as LOW, CNT as CNT from Show_blocks where log_file="' + log_file + '"',conn)
        self.sh_block_LOW = pd.read_sql( 'select LOW,CNT from Show_blocks where (LOW=0) and log_file="'+log_file+'"',conn)
        self.sh_block_CNT = pd.read_sql( 'select LOW,CNT from Show_blocks where (CNT=0)and log_file="'+log_file+'"',conn)
        self.agg_traffic1 = pd.read_sql('select a_traffic from a_traffic where log_file="' + log_file + '"',conn)

        self.console_time = pd.read_sql('select console_timeout from console_timeout where log_file="' + log_file + '"',conn)
        self.log_time_stamp = pd.read_sql('select log_time_stamp from log_time_stamp where log_file="' + log_file + '"',conn)        
        self.summary_inp = pd.read_sql('select summary_input from summary_input where log_file="' + log_file + '"',conn)
        self.summary_output = pd.read_sql('select summary_out from summary_out where log_file="' + log_file + '"',conn)   
        self.demm=(self.loww1+self.loww2)['count(*)'][0]
        self.demm1=(self.mediumm+self.mediumm1)['count(*)'][0]
        self.demm2=(self.loww+self.criticall1)['count(*)'][0]
        self.route = pd.read_sql('select route_ip as "Route IP" from route where ( route_ip <> "NA") and log_file="' + log_file + '"', conn)
        get_Tool_Execution = cur.execute("SELECT ID from Tool_Execution_Time")
        get_Tool_ExecutionList=get_Tool_Execution.fetchall()
        self.exec_count=len(get_Tool_ExecutionList)

        # Close the connection to DB
        conn.close()

        
   #Insert data to db
    def store_data(self,dbProcess,ADID_val,usecase_val,manualEff_val,Start_Time='',End_Time=''):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'

        # Connect to DB
        conn = sqlite3.connect(db_file)
        
        #store data
        cur = conn.cursor()
        if dbProcess=='db_login':        
            get_Record = cur.execute("SELECT ID from Effort_Estimation_Report where UserID='"+ADID_val+"'")
            get_RecordList=get_Record.fetchall()
            if len(get_RecordList)==0:
                cur.execute("insert into Effort_Estimation_Report (UserID,UsecaseName,ManualEfforts) values ('"+ADID_val+"', '"+usecase_val+"','"+manualEff_val+"')")          
        elif dbProcess=='db_transaction':
            
            cur.execute("insert into Tool_Execution_Time (UserID,UsecaseName,Date,StartTime,EndTime) values ('"+ADID_val+"','"+usecase_val+"','"+Start_Time+"','"+Start_Time+"','"+End_Time+"')")  
            
        #commit transaction
        conn.commit()
            
        # Close the connection to DB
        conn.close()
        
        
    #fetch admin - Productivity matrix
    def fetch_matrixdata(self,cal_startdt,cal_enddt):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'
        
        # Connect to DB
        conn = sqlite3.connect(db_file)
        subQ=" AND Date_Time > '"+cal_startdt+"' AND Date_Time < date('"+cal_enddt+"','+1 days')" 
        #print "select A.UserId as UserId,A.UsecaseName as UsecaseName,A.Date as Date_Time,B.ManualEfforts as Manual_Efforts,A.StartTime as Start_Time, A.EndTime as End_Time from Tool_Execution_Time A, Effort_Estimation_Report B where A.UserId=B.UserId"+subQ
        # Read data
        self.matrix_stats = pd.read_sql("select A.UserId as UserId,A.UsecaseName as UsecaseName,A.Date as Date_Time,B.ManualEfforts as Manual_Efforts,A.StartTime as Start_Time, A.EndTime as End_Time from Tool_Execution_Time A, Effort_Estimation_Report B where A.UserId=B.UserId"+subQ,
                                            conn)

        # Close the connection to DB
        conn.close()
        
    def fetch_cpu_utilization(self, log_file):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'

        # Connect to DB
        conn = sqlite3.connect(db_file)

        # Read data
        self.cpu_utilization = pd.read_sql('select * from cpu_utilization where log_file="' + log_file + '"', conn)              
        

        # Close the connection to DB
        conn.close()
        
    #Memory Utilization
    def fetch_memory_utilization(self, log_file):
        # File to create empty database with all the required tables and columns
        db_file = '../db/Firewall_Analyser_BOT_DB.sqlite'

        # Connect to DB
        conn = sqlite3.connect(db_file)

        # Read data        
        
        subQry="select 'Memory utilization' as Memory,total as Total,used as Used,free as Free from mem_processor_pool where log_file='" + log_file + "'"
        
        self.mem_processor_pool = pd.read_sql(subQry , conn)       

        # Close the connection to DB
        conn.close()

    #memory consumption Process

    #Insert data to Mysqldb
    def store_dataMysql(self,dbProcess,ADID_val,usecase_val,manualEff_val,Start_Date='',Start_Time='',End_Time=''):
        #Connect to DB
        dbM = mdb.connect(host="10.179.22.130",    # your host, usually localhost
                     user="admin",         # your username
                     passwd="wipro@123",  # your password
                     db="ProductivityMatrix")


        curM = dbM.cursor()
        curM.execute("USE ProductivityMatrix") 

        #store data
        
        if dbProcess=='db_login':        
            curM.execute("SELECT ID from t_effort_estimation_report where UserID='"+ADID_val+"' AND UsecaseName='"+usecase_val+"'")
            #get_RecordList=get_Record.fetchall()
            if len(curM.fetchall())==0:
                curM.execute("insert into t_effort_estimation_report (UserID,UsecaseName,Manual_Efforts) values ('"+ADID_val+"', '"+usecase_val+"','"+manualEff_val+"')")          
        elif dbProcess=='db_transaction':
            #print "insert into t_tool_Execution_Time (UserID,UsecaseName,Date,StartTime,EndTime) values ('"+ADID_val+"','"+usecase_val+"','"+Start_Date+"','"+Start_Time+"','"+End_Time+"')"
            curM.execute("insert into t_tool_Execution_Time (UserID,UsecaseName,Date,StartTime,EndTime) values ('"+ADID_val+"','"+usecase_val+"','"+Start_Date+"','"+Start_Time+"','"+End_Time+"')")  
            
        #commit transaction
        dbM.commit()
            
        # Close the connection to DB
        curM.close()        
        dbM.close()
        

log_file = r'C:\Users\jp user\Desktop\project\NABv2\BotModules\cisco Tech support.txt'
d = ProcessDataClass()
d.process_data(log_file)
d.fetch_data(log_file)

