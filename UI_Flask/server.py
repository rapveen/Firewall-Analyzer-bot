# Standard Python libraries
import time,  os, sqlite3, json, pandas as pd, sys, numpy as np
from random import randint

from datetime import datetime, timedelta

# BotModules
sys.path.append('../')
from BotModules import ProcessData
Log = ProcessData.ProcessDataClass()

# API Server libraries
from flask import request, Flask, jsonify, render_template, redirect, url_for, flash,session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import hashlib
from BotModules import Helpers

#Test pdf
from flask import make_response,current_app
from functools import wraps, update_wrapper
from datetime import datetime
#from reportlab.pdfgen import canvas
#from flask_weasyprint import HTML, render_pdf
#Test pdf

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['txt', 'log'])

app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.permanent_session_lifetime = timedelta(minutes=1)
CORS(app)

#orginVar=request.environ['HTTP_ORIGIN'] if request.environ['HTTP_ORIGIN']!=null else request.environ['HTTP_HOST']
#orginVar=if not request.environ['HTTP_ORIGIN']?request.environ['HTTP_ORIGIN']:request.environ['HTTP_HOST']
#print orginVar
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = '--'
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['server'] = 'Server'        
            h['X-Frame-Options']='DENY'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
#No cache
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)


# Landing page - Upload data
@app.route('/', methods=['GET','POST'])
@nocache 
def index():
    return redirect(url_for('login'))
    
# Landing page - Upload data
@app.route('/nab', methods=['GET','POST'])
@nocache 
def nab():
    return redirect(url_for('login'))

adminPwd='e6e061838856bf47e1de730719fb2609'
userPwd='ab100a52dc951abab0ca9235d7456705'

@app.route('/nab/login', methods=['GET','POST'])
#@app.errorhandler
@nocache 
@crossdomain(origin='*')
def login():
    #redirect(url_for('home_page'))
    error = None
    if session.get('bot_name') is not None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
      
    elif session.get('admin_bot_name') is not None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    
    if request.method == 'POST':
        #render_template('step1-upload.html')
        username = request.form.get('username')
        password = request.form.get('password')
        bot_cookie=request.cookies.get('nab_ck')
        form_cookie = request.form.get('frm_ck')
        
        if bot_cookie!=form_cookie: return redirect(url_for('clear'))
        
        username=username.strip(); password=password.strip()
        password=hashlib.md5(password.encode()).hexdigest()

        
        if username=='' or password=='':
            return render_template('Login.html', error='Incorrect Username and/or Password !!')
        #admin login    
        elif username=='admin' or password==adminPwd:
            session['admin_bot_name'] = username
            return redirect(url_for('productivity_matrix'))
        
        #ld = ldap.initialize('ldap://10.154.50.100:389')
        #ld.protocol_version = ldap.VERSION3
        if (username == 'fab1' and password == userPwd) or (username == 'fab2' and password == userPwd) or (username == 'fab3' and password == userPwd):
            session['bot_name'] = bot_cookie
            session['nab_username'] = username
            
            #create directory with username if not exists
            
            pathD="data\\"+session["nab_username"]
            if not os.path.exists(pathD):
                os.makedirs(pathD)            
            app.config['UPLOAD_FOLDER'] = pathD
            #Store in db
            ADID_val=username; usecase_val='Firewall Analyzer Bot'; manualEff_val='86400'           
                
            Log.store_data('db_login',ADID_val,usecase_val,manualEff_val)
            #Log.store_dataMysql('db_login',ADID_val,usecase_val,manualEff_val)
            return redirect(url_for('home_page'))
        else:
            error = 'Incorrect Username and/or Password !!'            
      
        #return render_template('step1-upload.html')
        #return redirect(url_for('home_page'))
    return render_template('Login.html', error=error)


#Admin- Productivity Matrix page

@app.route('/nab/productivity_matrix', methods=['GET'])      
@nocache  
@crossdomain(origin='*')                             
def productivity_matrix():
    
    
    if session.get('admin_bot_name') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))

    return render_template('productivity_Matrix.html')
    
#test
@app.route('/nab/matrix_test', methods=['GET'])   
@nocache       
@crossdomain(origin='*')                           
def matrix_test():
    cal_startdt=request.args.get('cal_startdt');  cal_enddt=request.args.get('cal_enddt'); 
   
    #structure cal date   
    cal_startdt=datetime.strptime(cal_startdt, "%d-%m-%Y").strftime("%Y-%m-%d")
    cal_enddt=datetime.strptime(cal_enddt, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    Log.fetch_matrixdata(cal_startdt,cal_enddt)
    matrix_data = Log.matrix_stats
    '''
    matrix_data['Date_Time'] = matrix_data['Date_Time'].apply(lambda d: str(d.strftime('%d %b,%Y %I:%M:%S %p')))
    matrix_data['Start_Time'] = matrix_data['Start_Time'].apply(lambda d: str(d.time().strftime('%I:%M:%S.%f %p')))
    matrix_data['End_Time'] = matrix_data['End_Time'].apply(lambda d: str(d.time().strftime('%I:%M:%S.%f %p')))
    '''
    matrix_data['Date_Time'] = matrix_data['Date_Time'].apply(lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f'))
    matrix_data['Date_Time'] = matrix_data['Date_Time'].apply(lambda d: str(d.strftime('%d %b,%Y %I:%M:%S %p')))
    
    matrix_data['Start_Time'] = matrix_data['Start_Time'].apply(lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f'))
    matrix_data['End_Time'] = matrix_data['End_Time'].apply(lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f'))
    
    #calculate Automation Efforts
    matrix_data['Automation_Efforts'] = matrix_data['End_Time'] -  matrix_data['Start_Time']
    Automation_Efforts_sec=matrix_data['Automation_Efforts'].apply(lambda d: d.total_seconds())
    matrix_data['Automation_Efforts'] = Automation_Efforts_sec.apply(lambda d: str(timedelta(seconds=d)).split('.')[0])
    
    #calculate Time Saved
    matrix_data['Manual_Efforts']=matrix_data['Manual_Efforts'].apply(lambda d: float(d))
    
    matrix_data['Time_Saved'] = abs(matrix_data['Manual_Efforts'] -  Automation_Efforts_sec)
    matrix_data['Time_Saved']= matrix_data['Time_Saved'].apply(lambda d: str(timedelta(seconds=d)).split('.')[0])
    
    #manual efforts
    matrix_data['Manual_Efforts']=matrix_data['Manual_Efforts'].apply(lambda d: str(timedelta(seconds=d)))
    
    matrix_data['Start_Time'] = matrix_data['Start_Time'].apply(lambda d: str(d.time().strftime('%I:%M:%S %p')))    
    matrix_data['End_Time'] = matrix_data['End_Time'].apply(lambda d: str(d.time().strftime('%I:%M:%S %p')))
    
    
    #return render_template('productivity_Matrix.html',matrix_data=matrix_data)
    #return jsonify({'display_text':matrix_data.to_json()}); 
    #val=json.dumps(json.loads(matrix_data.reset_index().to_json(orient='records')), indent=2)
    val=json.loads(matrix_data.reset_index().to_json(orient='records'))
    dict_r={}
    dict_r['data']=val
    return jsonify({'data':val})

    
@app.route('/nab/home_page', methods=['GET','POST'])
@nocache  
@crossdomain(origin='*')                                  
def home_page():
    global file_upload_status
    
    if session.get('bot_name') is None:
        # Here we know that a logged_in key is present in the session object.
        # Now we can safely check it's value
        return redirect(url_for('clear'))
    elif session['bot_name']!=request.cookies.get('nab_ck'):
        return redirect(url_for('clear'))

    if request.method == 'POST':
        session['Start_Time']=str(datetime.now())
        #takeda
        session['Start_Date']=str(datetime.now().date())

        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        
        #test=request.cookies.get('nab_ck')

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):              
            validFile=2
            #fileTest.close()
            if validFile!=-1:         
                filename = secure_filename(file.filename)            
                pathD="data\\"+session["nab_username"]
                file.save(os.path.join(pathD, filename))
                
                           
                return redirect(url_for('dashboard_page',
                                        log_file=filename))
            else:            
                return render_template('step1-upload.html',error='Please upload valid text file')
        else:            
            return render_template('step1-upload.html',error='Please upload only text file')

    return render_template('step1-upload.html')


# Attributes selection page
@app.route('/nab/attributes/<path:log_file>', methods=['GET','POST'])
@nocache 
@crossdomain(origin='*')
def attributes_selection(log_file):
    if request.method == 'POST':
        return redirect(url_for('dashboard_page',
                                log_file=log_file))

    return render_template('step2-attributes.html', log_file=log_file)
    
# This route will clear the variable sessions
# This functionality can come handy for example when we logout
# a user from our app and we want to clear its information
@app.route('/nab/clear')
@nocache 
@crossdomain(origin='*')
def clear():
    # Clear the session
    session.clear()
    
    # Redirect the user to the main page
    return redirect(url_for('index'))

########################
#bps -> bits to megabytes and section to display in model window 
#0.000125 * 0.001
########################

# Dashboard page
@app.route('/nab/dashboard/<path:log_file>', methods=['GET'])
@nocache
@crossdomain(origin='*')
def dashboard_page(log_file):
    if session.get('bot_name') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    elif session['bot_name']!=request.cookies.get('nab_ck'):
        return redirect(url_for('clear'))
      
    if session.get('Start_Time') is None: Start_Time=0;Start_Date=0 
    else: 
        Start_Time=session['Start_Time']; session.pop('Start_Time', None) 
        #takeda
        Start_Date=session['Start_Date']; session.pop('Start_Date', None) 
            
      
    #int_count = int(int_count)
    logfile_path="data/"+session['nab_username']+"/"+log_file
    # Check if the data for that log already exists
    db_conn = sqlite3.connect(Log.db_file)
    d = pd.read_sql("select * from cpu_utilization_stats where log_file='"+logfile_path+"'", db_conn)
    print d
    
    # Process the uploaded log if the log hasn't already been processed and saved to db
    if len(d) == 0:
        Log.process_data(logfile_path)
    #Log.process_data(logfile_path)
    # Fetch data from the database
    Log.fetch_data(logfile_path)

    #int_dims = Log.interfaces
    
    #Execution Count
    exec_count=Log.exec_count    
    
    ###CPU history Fetch from log file
    #Log.fetch_CpuHistory(logfile_path)
    #cpu_history_data = Log.cpu_history

    
    # Subset data for CPU Process history graph
    
    
    # Overview details
    overview = [str(Log.overview['hostname'][0]),
                str(Log.overview['device_info'][0]),
                str(Log.overview['image_version'][0]),
                str(Log.overview['uptime'][0]),
                str(Log.overview['config_register'][0]),
                str(Log.overview['config_changed'][0]),
                str(Log.overview['hardware'][0]),
                str(Log.overview['License'][0])]
    
    # CPU Utilization stats in tiles
    cpu_tiles = [str(Log.cpu_utilization_stats['five_sec'][0]),
                 str(Log.cpu_utilization_stats['one_min'][0]),
                 str(Log.cpu_utilization_stats['five_min'][0])]
    
    EOL = [str(Log.EOL['EOL'][0])]
    EOS = [str(Log.EOS['EOS'][0])]
    ACL1 = [str(Log.ACL1['ACL1'][0])]

    show_block_LOW = Log.sh_block_LOW
    show_block_CNT = Log.sh_block_CNT
    
    
    show_block_L=show_block_C=''
    if len(show_block_LOW)!=0:
        show_block_L = 'A zero in the LOW column indicates a previous event where memory was exhausted'

    if len(show_block_CNT)!=0:
        show_block_C = 'A zero in the CNT column means memory is exhausted. '
    elif len(show_block_LOW)== 0:
        show_block_C = ' No errors found in blocks'
    
    # Interfaces by status
    #int_down = Log.interfaces[Log.interfaces['interface_status'].isin(['down','administratively down'])][['interface_name','interface_status']]
    #int_up = Log.interfaces[Log.interfaces['interface_status'] == 'up'][['interface_name','interface_status']]
    
    #db store
    
    if Start_Time!=0:
        End_Time=str(datetime.now())
        #Log.store_data('db_transaction',session['nab_username'],'Network Analyzer Bot','2017-02-02 16:52:24.685000',Start_Time,End_Time)
        Log.store_data('db_transaction',session['nab_username'],'Firewall Analyzer Bot',Start_Time,Start_Time,End_Time)   
        #takeda
        #Log.store_dataMysql('db_transaction',session['nab_username'],'Network Analyzer Bot','0',Start_Date,Start_Time,End_Time)
        

    #mem_processor_pool=Log.mem_processor_pool[Log.mem_processor_pool.columns.tolist()[0:]],
    return render_template('step3-dashboard.html',                          
                           #cpu_history_data=cpu_history_data,
                           interfaces_data = Log.interfaces_data[Log.interfaces_data.columns.tolist()],
                           cpu_tiles=cpu_tiles,
                           #cpu_utilization=Log.cpu_utilization[Log.cpu_utilization.columns.tolist()[2:]],                                                     
                           overview=overview,
                           exec_count=exec_count,
                           final_throughput = Log.final_throughput[Log.final_throughput.columns.tolist()],
                           subnet = Log.subnet[Log.subnet.columns.tolist()],
                           failover_monitored = Log.failover_monitored,
                           fail_over_history = Log.fail_over_history[Log.fail_over_history.columns.tolist()],
                           EOL=EOL,
                           EOS=EOS,
                           processData=Log.processData[Log.processData.columns.tolist()],
                           load = Log.load[Log.load.columns.tolist()],
                           resourse_usage = Log.resourse_usage[Log.resourse_usage.columns.tolist()],
                           low_value= Log.low1[Log.low1.columns.tolist()],
                           low= Log.low[Log.low.columns.tolist()],
                           low2= Log.low2[Log.low2.columns.tolist()],
                           medium= Log.medium[Log.medium.columns.tolist()],
                           medium1= Log.medium1[Log.medium1.columns.tolist()],
                           #medium2= Log.medium2[Log.medium2.columns.tolist()],
                           #medium3= Log.medium3[Log.medium3.columns.tolist()],
                           #critical= Log.critical[Log.critical.columns.tolist()],
                           critical1= Log.critical1[Log.critical1.columns.tolist()],
                           LOW=Log.demm,
                           MED=Log.demm1,
                           CRI=Log.demm2,
                           route=Log.route,
                           cpu_utilization_stats_c=Log.cpu_utilization_stats_c,
                           traffic_data=Log.traffic_data,
                           ACL = Log.ACL[Log.ACL.columns.tolist()],
                           ACL1= ACL1[0],
                           ACL_count = str(Log.ACLC),
                           sh_block = Log.show_block,
                           show_block_L = show_block_L,
                           show_block_C = show_block_C,
                           input_errors = Log.input_errors,
                           agg_value1 = Log.agg_traffic1['a_traffic'][0],
                           console_time = Log.console_time['console_timeout'][0],
                           log_time_stamp = Log.log_time_stamp['log_time_stamp'][0],
                           summary_input = Log.summary_inp['summary_input'][0],
                           summary_output = Log.summary_output['summary_out'][0],
                           flow_off = Log.flow_off[Log.flow_off.columns.tolist()],
                           flow_ON = Log.flow_ON,
                           flow_ON_NA= Log.flow_ON_NA,
                           fail_reason = Log.fail_reason,
                           ACL_value1 =Log.ACL_rule_count
                           
                           )



#Error codes for log file
@app.route('/nab/log_error_code/<path:log_file>')
@nocache 
@crossdomain(origin='*')
def log_error_code(log_file):
    if session.get('nab_username') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    
    logfile_path="data/"+session['nab_username']+"/"+log_file   
    
    ###Error code for the log file
    Log.show_log_error_codes(logfile_path)
    
    log_error_code = Log.getlog_error_code[Log.getlog_error_code.columns.tolist()[0:]]
    
    # Convert to Json format
    log_error_code=json.loads(log_error_code.reset_index().to_json(orient='records'))             
    return jsonify({'log_error_code':log_error_code})    



 
 
#Memory Utilization
@app.route('/nab/memory_utilization_table/<path:log_file>')
@nocache 
@crossdomain(origin='*')
def memory_utilization_table(log_file):
    if session.get('nab_username') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    
    logfile_path="data/"+session['nab_username']+"/"+log_file   
    
    # Fetch data from the database
    Log.fetch_memory_utilization(logfile_path)

    mem_processor_pool = Log.mem_processor_pool[Log.mem_processor_pool.columns.tolist()[0:]]
    
    # Convert to Json format
    mem_processor_pool=json.loads(mem_processor_pool.reset_index().to_json(orient='records'))             
    return jsonify({'mem_processor_pool':mem_processor_pool})    
#exportPdf
@app.route('/nab/exportPdf/<path:log_file>/<int:int_count>')
@nocache 
@crossdomain(origin='*')
def exportPdf(log_file,int_count):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Image
    from reportlab.lib.styles import getSampleStyleSheet
    #barchart
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    #label
    from reportlab.graphics import shapes
    from reportlab.graphics.charts.textlabels import Label

    #design
    from reportlab.lib.styles import ParagraphStyle as PS
    from reportlab.lib.enums import TA_RIGHT
    
    if session.get('nab_username') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    
    logfile_path="data/"+session['nab_username']+"/"+log_file   

    #Pdf open
    time_stamp=str(time.time())
    filepathPdf="pdf/"+log_file+"_"+session['nab_username']+time_stamp+".pdf"
    #filepathPdf='test.pdf'
    doc = SimpleDocTemplate("static/"+filepathPdf, showBoundary=1,pagesize=letter)
    
    elements = []

    h1 = PS(name = 'Heading1',fontSize = 14,leading = 16)
    bodyTxt = PS(name='Times-Roman',fontSize=10,leading=12)
    tbleTxt = PS(name='Times-Roman',fontSize=8,leading=12)
    BotName = "<font size='12'>Firewall Analysis Bot</font>"
    dashName =  "<font size='12'>DashBoard</font>"
    policyfName =  "<font size='12'>Policy Findings</font>"
    interfaceName =  "<font size='12'>Interfaces</font>"
    observationName =  "<font size='12'>Observation</font>"
    
    styles = getSampleStyleSheet()
    BotNameP = Paragraph(BotName, h1)     
    dashNameP = Paragraph(dashName, h1)
    policyNameP = Paragraph(policyfName, h1)
    interfaceNameP = Paragraph(interfaceName, h1)
    observationNameP = Paragraph(observationName, h1) 
    # add a logo and size it
    logo = Image("static/img/holmes_logo.png")
    logo.drawHeight = 0.5*inch
    logo.drawWidth = 1*inch

    data = [[logo, BotNameP]]
    table = Table(data)
    table.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.blue)])

    data = [[dashNameP]]
    dtable = Table(data)
    dtable.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.magenta)])
    data = [[policyNameP]]
    ptable = Table(data)
    ptable.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.magenta)])
    data = [[interfaceNameP]]
    itable = Table(data)
    itable.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.magenta)])
    data = [[observationNameP]]
    otable = Table(data)
    otable.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.magenta)])

    
    elements.append(table)


    # Fetch data from the database
    Log.fetch_data(logfile_path)
    
    #Log file Name   
    elements.append(Paragraph("<br />Log File: "+logfile_path.split('/')[2], bodyTxt))   
    
    #Execution Count
    exec_count=Log.exec_count    
    elements.append(Paragraph("<br />Execution Count: "+str(exec_count), bodyTxt))
    #dashboard
    blankTbl=[['','']]
    tblank=Table(blankTbl,hAlign='CENTER')

    elements.append(tblank);
    elements.append(dtable)
    # CPU Utilization stats in tiles
    
    CPUStat = [['CPU Utilization','%'],
            ['5 sec utilization',str(Log.cpu_utilization_stats['five_sec'][0])],
            ['1 min utilization',str(Log.cpu_utilization_stats['one_min'][0])],
            ['5 min utilization',str(Log.cpu_utilization_stats['five_min'][0])]
            ]

    CPUStatTbl=Table(CPUStat,hAlign='CENTER')

    CPUStatTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),                   
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                       ('VALIGN',(0,0),(0,-1),'TOP'),
                       ('ALIGN',(0,0),(-1,-1),'LEFT'),
                       ('GRID', (0,0),(1,0), 1, colors.green),
                       ('TEXTCOLOR',(0,0),(1,0),colors.green),
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                       ]))

    
    elements.append(CPUStatTbl);
    
    
    
    
    #memory_utilization
    Log.fetch_memory_utilization(logfile_path)
    
    mem_processor_poolList =Log.mem_processor_pool.as_matrix().tolist()
    mem_processor_poolList.insert(0, ['Memory Utilization','Total','Used','Free'])

    mem_processor_poolTbl=Table(mem_processor_poolList,hAlign='CENTER')

    mem_processor_poolTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                    ('GRID', (0,0),(3,0), 1, colors.green),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),                   
                   ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                   ("VALIGN", (0,0), (-1,-1), "TOP"),
                   ('TEXTCOLOR',(0,0),(3,0),colors.green),
                   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                   ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                   ]))
    elements.append(tblank);
    elements.append(mem_processor_poolTbl);
    #Overview details
    overview = [['Hostname',Paragraph(str(Log.overview['hostname'][0]),tbleTxt)],
            ['Device info',Paragraph(str(Log.overview['device_info'][0]),tbleTxt)],
            ['Image version',Paragraph(str(Log.overview['image_version'][0]),tbleTxt)],
            ['Uptime',Paragraph(str(Log.overview['uptime'][0]),tbleTxt)],
            ['Config Register',Paragraph(str(Log.overview['config_register'][0]),tbleTxt)],
            ['Hardware',Paragraph(str(Log.overview['hardware'][0]),tbleTxt)]
            ]
    overview.insert(0, ['Device Summary',''])

    
    overviewTbl=Table(overview,hAlign='CENTER')

    overviewTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                        ('GRID', (0,0),(1,0), 1, colors.green),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),                       
                       ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                       ('TEXTCOLOR',(0,0),(1,0),colors.green),
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                       ]))
    elements.append(tblank);
    elements.append(overviewTbl);

    #policyfindings
    elements.append(tblank);
    elements.append(ptable)
    
    
    
    

    #ACL
    acl = Log.ACL.as_matrix().tolist()
    if(len(acl)):
        aclName = "<div size='8'>The total device-wide Access Control List (ACL) count is {0} ".format(Log.ACL1) + "</div><div>Top ACLs, by size, on this Firewall:</div>"
        aclNameP = Paragraph(aclName, h1)
        data = [[aclNameP]]
        acltable = Table(data)
        elements.append(acltable)
        #table.setStyle([("VALIGN", (0,0), (0,0), "TOP"),("LINEBELOW", (0,0), (-1,-1), 1, colors.blue)])
        table.setStyle([("VALIGN", (0,0), (0,0), "TOP")])
        acl.insert(0,['ACL_list','rule'])
        aclTbl=Table(acl,hAlign='CENTER')
        aclTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(1,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(1,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank)
        elements.append(aclTbl);
    #low
    low=Log.low.as_matrix().tolist()
    if(len(low)):
        low.insert(0,['Low'])
        lowTbl=Table(low,hAlign='CENTER')
        lowTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank)
        elements.append(lowTbl);
    #low
    low_valuE= Log.low1[Log.low1.columns.tolist()].as_matrix().tolist()
    if(len(low_valuE)):
        low_valuE.insert(0,['Low'])
        low_valueTbl=Table(low_valuE,hAlign='CENTER')
        low_valueTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(low_valueTbl);
    #low
    low2=Log.low2.as_matrix().tolist()
    if(len(low2)):
        low2.insert(0,['Low'])
        low2Tbl=Table(low2,hAlign='CENTER')
        low2Tbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
     #medium
    medium=Log.medium.as_matrix().tolist()
    if(len(medium)):
        medium.insert(0,['Medium'])
        mediumTbl=Table(medium,hAlign='CENTER')
        mediumTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(mediumTbl);

    
    
    
    
    #medium
    medium1=Log.medium1.as_matrix().tolist()
    if(len(medium1)):
        medium1.insert(0,['Medium'])
        medium1Tbl=Table(medium1,hAlign='CENTER')
        medium1Tbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(medium1Tbl);



    
     #critical
##    critical=Log.critical.as_matrix().tolist()
##    if(len(critical)):
##        critical.insert(0,['Critical'])
##        criticalTbl=Table(critical,hAlign='CENTER')
##        criticalTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
##                                                ('GRID', (0,0),(0,0), 1, colors.green),
##                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
##                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
##                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
##                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
##                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
##                                                 ]))
##        elements.append(tblank);
##        elements.append(criticalTbl);
    #critical
    critical1=Log.critical1.as_matrix().tolist()
    if(len(critical1)):
        critical1.insert(0,['Critical'])
        critical1Tbl=Table(critical1,hAlign='CENTER')
        critical1Tbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(critical1Tbl);

    #interfaces
    #Interfaces_data
    interfaces_list=Log.interfaces_data.as_matrix().tolist()
    if(len(interfaces_list)!=0):
        interfaces_list.insert(0,['Interface_name','Interface_description','Interface_state','Duplex_state'])
        interfaces_listTbl=Table(interfaces_list,hAlign='CENTER')
        interfaces_listTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(3,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(3,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        
        elements.append(tblank);
        elements.append(itable)
    
        elements.append(interfaces_listTbl);
    #Throughput_summary
    #final_throughput=Log.final_throughput.as_matrix().tolist()
    #if(len(final_throughput)!=0):
	
    throughputName = "<li>Input: {0} bytes/sec</li>".format(Log.summary_output)
    #throughputName = throughputName + "<li>| Output: {1} bytes/sec</li>".format(Log.summary_output)
    throughputP = Paragraph(throughputName, h1)
    data = [[throughputP]]
    throughputtable = Table(data)
    elements.append(throughputtable)

    
    
    elements.append(tblank);
    elements.append(otable)
    #log_time
    
    
    log_timeName = "<div >{0}</div>".format(Log.console_time)
    log_timeP = Paragraph(log_timeName, h1)
    data = [[log_timeP]]
    log_timetable = Table(data)
    elements.append(log_timetable)
    elements.append(tblank);
    #time_stamp
    time_stampName = "<div >{0}</div>".format(Log.log_time_stamp)
    time_stampP = Paragraph(time_stampName, h1)
    data = [[time_stampP]]
    time_stamptable = Table(data)
    elements.append(time_stamptable)
    elements.append(tblank);
##    #subnetmask_summary
##    subnet=Log.subnet.as_matrix().tolist()
##    if(len(subnet)!=0):
##        subnet.insert(0,['Interface_name','Subnet'])
##        subnetTbl=Table(subnet,hAlign='CENTER')
##        subnetTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
##                                                ('GRID', (0,0),(1,0), 1, colors.green),
##                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
##                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
##                                                 ('TEXTCOLOR',(0,0),(1,0),colors.green),
##                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
##                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
##                                                 ]))
##        elements.append(tblank);
##        elements.append(subnetTbl);
    #monitoring
    failover_monitored=Log.failover_monitored.as_matrix().tolist()
    if(len(failover_monitored)!=0):
        failover_monitored.insert(0,['not_monitored'])
        failover_monitoredTbl=Table(failover_monitored,hAlign='CENTER')
        failover_monitoredTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(failover_monitoredTbl);
    
    #Fail_over_HIstory
    fail_over_history = Log.fail_over_history.as_matrix().tolist()
    if(len(fail_over_history)!=0):
        fail_over_history.insert(0,['from_state','to_state','Reason'])
        fail_over_historyTbl=Table(fail_over_history,hAlign='CENTER')
        fail_over_historyTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(2,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(2,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(fail_over_historyTbl);
    
    #ProcessData
    processData = Log.processData.as_matrix().tolist()
    if(len(processData)!=0):
        processData.insert(0,['process','run_time'])
        processDataTbl=Table(processData,hAlign='CENTER')
        processDataTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(1,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(1,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(processDataTbl);
    #Resource_usage
    resourse_usage = Log.resourse_usage.as_matrix().tolist()
    if(len(resourse_usage)!=0):
        resourse_usage.insert(0,['peak_value','resource_name'])
        resourse_usageTbl=Table(resourse_usage,hAlign='CENTER')
        resourse_usageTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(1,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(1,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(resourse_usageTbl);
    #load_details
    load=Log.load.as_matrix().tolist()
    if(len(load)!=0):
        load.insert(0,['Interface_name','Overruns','Underruns'])
        loadTbl=Table(load,hAlign='CENTER')
        loadTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(2,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(2,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(loadTbl);
    #route
    route=Log.route.as_matrix().tolist()
    if(len(route)):
        route.insert(0,['IP'])
        routeTbl=Table(route,hAlign='CENTER')
        routeTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(0,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(0,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(routeTbl);


    #traffic_data
    traffic_daTa=Log.traffic_data.as_matrix().tolist()
    if(len(traffic_daTa)!=0):
        traffic_daTa.insert(0,['Interface_name','minute_1_input_rate','minute_5_input_rate','minute_1_output_rate','minute_5_output_rate'])
        traffic_daTaTbl=Table(traffic_daTa,hAlign='CENTER')
        traffic_daTaTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(4,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(4,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(traffic_daTaTbl);
    #cpu_utilization_stats
    cpu_utilName = "<div >{0}</div>".format(Log.cpu_utilization_stats_c)
    cpu_utilP = Paragraph(cpu_utilName, h1)
    data = [[cpu_utilP]]
    cpu_utiltable = Table(data)
    elements.append(tblank);
    elements.append(cpu_utiltable)
    elements.append(tblank);
     #show_L
    show_block_LOW = Log.sh_block_LOW
    show_block_CNT = Log.sh_block_CNT
    if len(show_block_LOW)!=0:
        show_block_L = 'A zero in the LOW column indicates a previous event where memory was exhausted'
    elif len(show_block_LOW)== 0:
        show_block_L = ' No errors found in Low column in blocks'
    if len(show_block_CNT)!=0:
        show_block_C = 'A zero in the CNT column means memory is exhausted. '
    elif len(show_block_LOW)== 0:
        show_block_C = ' No errors found in CNT columns in blocks'
   
    
    show_LName = "<div >{0}</div>".format(show_block_L)
    show_LP = Paragraph(show_LName, h1)
    data = [[show_LP]]
    show_Ltable = Table(data)
    elements.append(tblank);
    elements.append(show_Ltable)
    elements.append(tblank);

    #show_C
    
    show_CName = "<div >{0}</div>".format(show_block_C)
    show_CP = Paragraph(show_CName, h1)
    data = [[show_CP]]
    show_Ctable = Table(data)
    elements.append(tblank);
    elements.append(show_Ctable)
    elements.append(tblank);


    #show_block
    sho_block=Log.show_block.as_matrix().tolist()
    if(len(sho_block)!=0):
        sho_block.insert(0,['SIZE','MAX','LOW','CNT'])
        sho_blockTbl=Table(sho_block,hAlign='CENTER')
        sho_blockTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(3,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(3,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(sho_blockTbl);

    #flow_off
    flow_off=Log.flow_off.as_matrix().tolist()
    if(len(flow_off)!=0):
        flow_off.insert(0,['Interface Name','Flow_State','Mode'])
        flow_offTbl=Table(flow_off,hAlign='CENTER')
        flow_offTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(2,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(2,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(flow_offTbl);
    #flow_on
    flow_on=Log.flow_ON.as_matrix().tolist()
    if(len(flow_on)!=0):
        flow_on.insert(0,['Interface Name','Flow_State','Mode'])
        flow_onTbl=Table(flow_on,hAlign='CENTER')
        flow_onTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(2,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(2,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(flow_onTbl);

    #flow_on_na
    flow_on_na=Log.flow_ON_NA.as_matrix().tolist()
    if(len(flow_on_na)!=0):
        flow_on_na.insert(0,['Interface Name','Flow_State','Mode'])
        flow_on_naTbl=Table(flow_on_na,hAlign='CENTER')
        flow_on_naTbl.setStyle(TableStyle([('ALIGN',(0,0),(-2,-2),'LEFT'),
                                                ('GRID', (0,0),(2,0), 1, colors.green),
                                                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                 ('ALIGN',(0,-1),(-1,-1),'LEFT'),
                                                 ('TEXTCOLOR',(0,0),(2,0),colors.green),
                                                 ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                                 ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                                                 ]))
        elements.append(tblank);
        elements.append(flow_on_naTbl);
    
    doc.build(elements)     

    canvas = doc.canv 
    

    canvas.setTitle("Report - "+log_file) 

    canvas.showPage() 

    canvas.save() 
    
    return redirect(url_for('static', filename=filepathPdf)) 





#Export to Excel   
@app.route('/nab/exportExcel/<path:log_file>/<int:int_count>')
@nocache 
@crossdomain(origin='*')
def exportExcel(log_file,int_count):
    import xlsxwriter

    if session.get('nab_username') is None:
      # Here we know that a logged_in key is present in the session object.
      # Now we can safely check it's value
      return redirect(url_for('clear'))
    
    logfile_path="data/"+session['nab_username']+"/"+log_file    

    #Pdf open
    time_stamp=str(time.time())
    filepathExcel="csv/"+log_file+"_"+session['nab_username']+time_stamp+".xlsx"
    
    workbook = xlsxwriter.Workbook("static/"+filepathExcel)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})

    #add header
    # Insert an image with scaling.
    worksheet.insert_image('A1', 'static/img/holmes_logo.png', {'x_scale': 1.0, 'y_scale': 0.8})
    #worksheet.write('E1', 'Network Analysis Bot',bold)
    worksheet.insert_textbox('E1', 'Network Analysis Bot',
                             {'font': {'bold': True,
                                       'italic': False,
                                       'underline': True,
                                       'name': 'Arial',
                                       'color': 'blue',
                                       'size': 14},'x_scale': 1.25, 'y_scale': 0.25})

    #Log file Name   
    worksheet.write('A4', 'Log File:')
    worksheet.write('B4', logfile_path.split('/')[2])    

    # Fetch data from the database
    Log.fetch_data(logfile_path)


    
    # Add a bold format to use to highlight cells.
    header_format = workbook.add_format({'align':'left','bold': True, 'font_color': 'green', 'border':True,'border_color':'green'})
    cell_format= workbook.add_format({'align':'left','border':True})
    # Iterate over the data and write it out row by row.

    def excel_table(data,col,i):
        row_curr=i
        for item, cost in data:
            worksheet.set_column(i, col, len(str(item))+2)
            worksheet.set_column(i, col+1,len(str(cost))+2)
            if i==row_curr:
                worksheet.write(i,col,item,header_format)
                worksheet.write(i,col+1,cost,header_format)
            else:
                worksheet.write(i,col,item,cell_format)
                worksheet.write(i,col+1,cost,cell_format)
            i+=1
        return i

    row_no=5

    #Overview details
    overview = [['Device Summary',''],
            ['Hostname',str(Log.overview['hostname'][0])],
            ['Device info',str(Log.overview['device_info'][0])],
            ['Image version',str(Log.overview['image_version'][0])],
            ['Uptime',str(Log.overview['uptime'][0])],
            ['Config Register',str(Log.overview['config_register'][0])],
            ['Hardware',str(Log.overview['hardware'][0])]
            ]
    
    row_no=excel_table(overview,1,row_no)

    # CPU Utilization stats in tiles
    
    CPUStat = [['CPU Utilization','%'],
            ['5 sec utilization',str(Log.cpu_utilization_stats['five_sec'][0])],
            ['1 min utilization',str(Log.cpu_utilization_stats['one_min'][0])],
            ['5 min utilization',str(Log.cpu_utilization_stats['five_min'][0])]
            ]

    curr_row=row_no+2; col=1
    row_no=excel_table(CPUStat,col,curr_row);
    
    #memory_utilization
    Log.fetch_memory_utilization(logfile_path)
    
    mem_processor_poolList =Log.mem_processor_pool.as_matrix().tolist()
    mem_processor_poolList.insert(0, ['Memory Utilization','Total','Used','Free'])

    curr_row=row_no+2; col=1
    for key, val1,val2,val3 in mem_processor_poolList:
        worksheet.set_column(curr_row, col,len(str(key))+2)
        worksheet.set_column(curr_row, col+1,len(str(val1))+2)
        worksheet.set_column(curr_row, col+2,len(str(val2))+2)
        worksheet.set_column(curr_row, col+3,len(str(val3))+2)
        if curr_row==(row_no+2):
            worksheet.write(curr_row, col,  key, header_format)
            worksheet.write(curr_row, col + 1, val1, header_format)
            worksheet.write(curr_row, col + 2, val2, header_format)
            worksheet.write(curr_row, col + 3, val3, header_format)
        else:
            worksheet.write(curr_row, col,  key,cell_format)
            worksheet.write(curr_row, col + 1, val1,cell_format)
            worksheet.write(curr_row, col + 2, val2,cell_format)
            worksheet.write(curr_row, col + 3, val3,cell_format)
        curr_row += 1
        
    row_no=curr_row
    #ACL
    curr_row=row_no+2; col=1
    
    acl_xls = "The total device-wide Access Control List (ACL) count is %s " %(Log.ACL1)
    worksheet.write(curr_row,col,acl_xls,cell_format)
    row_no=curr_row
    acl = Log.ACL.as_matrix().tolist()
    acl.insert(0,['ACL_list','rule'])
    curr_row=row_no+2; col=1
    for key, val1 in acl:
        worksheet.set_column(curr_row, col,len(str(key))+2)
        worksheet.set_column(curr_row, col+1,len(str(val1))+2)
        
        if curr_row==(row_no+2):
            worksheet.write(curr_row, col,  key, header_format)
            worksheet.write(curr_row, col + 1, val1, header_format)
           
        else:
            worksheet.write(curr_row, col,  key,cell_format)
            worksheet.write(curr_row, col + 1, val1,cell_format)
           
        curr_row += 1
        
    row_no=curr_row
    #Interfaces_data
    interfaces_list=Log.interfaces_data.as_matrix().tolist()
    interfaces_list.insert(0,['Interface_name','Interface_description','Interface_state','Duplex_state'])
    curr_row=row_no+2; col=1
    for key, val1,val2,val3 in interfaces_list:
        worksheet.set_column(curr_row, col,len(str(key))+2)
        worksheet.set_column(curr_row, col+1,len(str(val1))+2)
        worksheet.set_column(curr_row, col+2,len(str(val2))+2)
        worksheet.set_column(curr_row, col+3,len(str(val3))+2)
        if curr_row==(row_no+2):
            worksheet.write(curr_row, col,  key, header_format)
            worksheet.write(curr_row, col + 1, val1, header_format)
            worksheet.write(curr_row, col + 2, val2, header_format)
            worksheet.write(curr_row, col + 3, val3, header_format)
        else:
            worksheet.write(curr_row, col,  key,cell_format)
            worksheet.write(curr_row, col + 1, val1,cell_format)
            worksheet.write(curr_row, col + 2, val2,cell_format)
            worksheet.write(curr_row, col + 3, val3,cell_format)
        curr_row += 1
        
    row_no=curr_row

    #low
    low=Log.low.as_matrix().tolist()
    if(len(low)):
        low.insert(0,['Low'])
        curr_row=row_no+2; col=1
        for val1 in low:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
    #low
    low_valuE= Log.low1[Log.low1.columns.tolist()].as_matrix().tolist()
    if(len(low_valuE)):
        low_valuE.insert(0,['Low'])
        curr_row=row_no+2; col=1
        for val1 in low_valuE:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
    #low
    low2=Log.low2.as_matrix().tolist()
    if(len(low2)):
        low2.insert(0,['Low'])
        curr_row=row_no+2; col=1
        for val1 in low2:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
     #medium
    medium=Log.medium.as_matrix().tolist()
    if(len(medium)):
        medium.insert(0,['Medium'])
        curr_row=row_no+2; col=1
        for val1 in medium:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row

    
    
    
    
    #medium
    medium1=Log.medium1.as_matrix().tolist()
    if(len(medium1)):
        medium1.insert(0,['Medium'])
        curr_row=row_no+2; col=1
        for val1 in medium1:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
    #critical
    critical1=Log.critical1.as_matrix().tolist()
    if(len(critical1)):
        critical1.insert(0,['Critical'])
        curr_row=row_no+2; col=1
        for val1 in critical1:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row

    #Throughput_summary
    final_throughput=Log.final_throughput.as_matrix().tolist()
    if(len(final_throughput)!=0):
        final_throughput.insert(0,['Interface_name','Final throughput'])
        curr_row=row_no+2; col=1
        for key, val1 in final_throughput:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
               
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    #subnetmask_summary
    subnet=Log.subnet.as_matrix().tolist()
    if(len(subnet)!=0):
        subnet.insert(0,['Interface_name','Subnet'])
        curr_row=row_no+2; col=1
        for key, val1 in subnet:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
               
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    #monitoring
    failover_monitored=Log.failover_monitored.as_matrix().tolist()
    if(len(failover_monitored)!=0):
        failover_monitored.insert(0,['not_monitored'])
        curr_row=row_no+2; col=1
        for val1 in failover_monitored:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
    
    #Fail_over_HIstory
    fail_over_history = Log.fail_over_history.as_matrix().tolist()
    if(len(fail_over_history)!=0):
        fail_over_history.insert(0,['from_state','to_state','Reason'])
        curr_row=row_no+2; col=1
        for key, val1,val2 in fail_over_history:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            worksheet.set_column(curr_row, col+2,len(str(val2))+2)
           
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
                worksheet.write(curr_row, col + 2, val2, header_format)
                
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
                worksheet.write(curr_row, col + 2, val2,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    
    #ProcessData
    processData = Log.processData.as_matrix().tolist()
    if(len(processData)!=0):
        processData.insert(0,['process','run_time'])
        curr_row=row_no+2; col=1
        for key, val1 in processData:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
               
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    #Resource_usage
    resourse_usage = Log.resourse_usage.as_matrix().tolist()
    if(len(resourse_usage)!=0):
        resourse_usage.insert(0,['peak_value','resource_name'])
        curr_row=row_no+2; col=1
        for key, val1 in resourse_usage:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
               
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    #load_details
    load=Log.load.as_matrix().tolist()
    if(len(load)!=0):
        load.insert(0,['Interface_name','Overruns','Underruns'])
        curr_row=row_no+2; col=1
        for key, val1,val2 in load:
            worksheet.set_column(curr_row, col,len(str(key))+2)
            worksheet.set_column(curr_row, col+1,len(str(val1))+2)
            worksheet.set_column(curr_row, col+2,len(str(val2))+2)
           
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col,  key, header_format)
                worksheet.write(curr_row, col + 1, val1, header_format)
                worksheet.write(curr_row, col + 2, val2, header_format)
                
            else:
                worksheet.write(curr_row, col,  key,cell_format)
                worksheet.write(curr_row, col + 1, val1,cell_format)
                worksheet.write(curr_row, col + 2, val2,cell_format)
               
            curr_row += 1
            
        row_no=curr_row
    #route
    route=Log.route.as_matrix().tolist()
    if(len(route)):
        route.insert(0,['Route IP'])
        curr_row=row_no+2; col=1
        for val1 in route:
            if curr_row==(row_no+2):
                worksheet.write(curr_row, col + 1, (val1[0]), header_format)
            else:
                worksheet.write(curr_row, col + 1, (val1[0]),cell_format)  
            curr_row += 1
            
        row_no=curr_row
    

    workbook.close()
    return redirect(url_for('static', filename=filepathExcel)) 
if __name__ == '__main__':
    app.run(port=8208,debug=True,use_reloader=True,threaded=True)
