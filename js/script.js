// Generate PDF of the Overview tab
// var doc = new jsPDF();
//
// $('#downloadBtn').click(function () {
//     console.log('Downloading... '+filename);
//     doc.fromHTML($('#overview').html(), 15, 15, {
//         'width': 170
//     });
//     log_file = window.location.href.substr(window.location.href.lastIndexOf("/")+1).split('.')[0];
//     filename = 'Network-Analyzer-Bot-Dashboard--'+log_file+'--.pdf';
//
//     doc.save(filename);
// });




//$(function(){
    //ui validation
    //$('#topN').html("Top "+parseInt($(location).attr('href').split("/")[5])+" interfaces");
   // $('#cntInt').val(parseInt($(location).attr('href').split("/")[5]));
   // $('#refreshBtn').click( function () {
    //    window.location = '/dashboard/'+$(location).attr('href').split("/")[4]+'/'+$('#cntInt').val()+'#topN';
    //});
//});*/

//File upload extension  uploadErrorMsg
/*function CheckFileName() {
        var fileName = document.getElementById("uploadfileId").value;
        alert(fileName);
        if (fileName == "") {
            document.getElementById("uploadErrorMsg").html("Browse to upload a valid File with png extension");
            return false;
        }
        else if (fileName.split(".")[1].toUpperCase() == "txt")
            return true;
        else {
            document.getElementById("uploadErrorMsg").html("File with " + fileName.split(".")[1] + " is invalid. Upload a validfile with txt extensions");
            return false;
        }
        return true;
    }
*/



//Cookie

function SetCookie(cookieName,cookieValue,nDays) {
   
   var today = new Date();
   var expire = new Date();
   if (nDays==null || nDays==0) nDays=1;
   expire.setTime(today.getTime() + 3600000*24*nDays);
   document.cookie = cookieName+"="+escape(cookieValue)
                   + ";expires="+expire.toGMTString();
    
  }

function loginAuth()
{

  var ID = Math.random().toString(36).substr(2, 9); 
  document.getElementsByName("frm_ck")[0].value=ID;
  SetCookie('nab_ck', ID);

  return true;

}



function ReadCookie(cookieName) {
 var theCookie=" "+document.cookie;
 var ind=theCookie.indexOf(" "+cookieName+"=");
 if (ind==-1) ind=theCookie.indexOf(";"+cookieName+"=");
 if (ind==-1 || cookieName=="") return "";
 var ind1=theCookie.indexOf(";",ind+1);
 if (ind1==-1) ind1=theCookie.length; 
 return unescape(theCookie.substring(ind+cookieName.length+2,ind1));
}

//alert(ReadCookie('nab_ck'));


	$( document ).ready(function() {

    //Destroy cookie
    $('#logoutId').click( function () {
       //$.cookie("nab_ck", null, { path: '/' });       
       SetCookie('nab_ck', '', -1);       
    });

    //file upload validation

   /* $('input[name="uploadfileId"]').each(function () {
    $(this).rules('add', {
        required: true,
        accept: "image/jpeg, image/pjpeg"
    })
  })*/

    //ui dashboard
var log_Filename=$(location).attr('href').split("/")[5];
//alert(parseInt($(location).attr('href').split("/")[6]));
//$('#cntInt').val(parseInt($(location).attr('href').split("/")[6]));

$('#pdfExportUrl').attr('href','/nab/exportPdf/'+log_Filename+'/5');
$('#csvExportUrl').attr('href','/nab/exportExcel/'+log_Filename+'/5');
//Rest callInterface tables    
    function LoadInterfaceData(interface_cnt)
    {
    
    $.getJSON('/nab/interface_table/' + log_Filename+'/'+interface_cnt, 
      {},
      function(data) {
            //alert(data1.length);
            $('#cntInt').val(interface_cnt);
            //Get Response data
            input_rate_bps=data.input_rate_bps; input_rate_pps=data.input_rate_pps; input_rate_duration=data.input_rate_duration;
            output_rate_pps=data.output_rate_pps;output_rate_bps=data.output_rate_bps; output_rate_duration=data.output_rate_duration;
           rxload=data.rxload; txload=data.txload;  duplex=data.duplex; input_drop=data.input_drop; output_drop=data.output_drop;
           broadcasts=data.broadcasts; multicast=data.multicast; runts=data.runts; giants=data.giants; input_error=data.input_error; crc=data.crc;
            int_down=data.int_down; int_up=data.int_up;
            
            //Populate table data
            //input_rate_bps_TbleId
            tbodyContent="";
             for (i=0;i<input_rate_bps.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+input_rate_bps[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+input_rate_bps[i]["input_rate_mbps"]+"</td></tr>";
            }
            $("#input_rate_bps_TbleId tbody").html(tbodyContent);
            
            //input_rate_pps
            tbodyContent="";
             for (i=0;i<input_rate_pps.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+input_rate_pps[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+input_rate_pps[i]["input_rate_pps"]+"</td></tr>";
            }
            $("#input_rate_pps_TbleId tbody").html(tbodyContent);
            
            //input_rate_duration
            tbodyContent="";
             for (i=0;i<input_rate_duration.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+input_rate_duration[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+input_rate_duration[i]["input_rate_duration"]+"</td></tr>";
            }
            $("#input_rate_duration_TbleId tbody").html(tbodyContent);

            //output_rate_pps
            tbodyContent="";
             for (i=0;i<output_rate_pps.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+output_rate_pps[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+output_rate_pps[i]["output_rate_pps"]+"</td></tr>";
            }
            $("#output_rate_pps_TbleId tbody").html(tbodyContent);
            //output_rate_bps
            tbodyContent="";
             for (i=0;i<output_rate_bps.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+output_rate_bps[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+output_rate_bps[i]["output_rate_mbps"]+"</td></tr>";
            }            
            $("#output_rate_bps_TbleId tbody").html(tbodyContent);

            //output_rate_duration
            tbodyContent="";
             for (i=0;i<output_rate_duration.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+output_rate_duration[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+output_rate_duration[i]["output_rate_duration"]+"</td></tr>";
            }
            $("#output_rate_duration_TbleId tbody").html(tbodyContent);

            //rxload
            tbodyContent="";
             for (i=0;i<rxload.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+rxload[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+rxload[i]["rxload"]+"</td></tr>";
            }
            $("#rxload_TbleId tbody").html(tbodyContent);
            
            //txload
            tbodyContent="";
             for (i=0;i<txload.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+txload[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+txload[i]["txload"]+"</td></tr>";
            }            
            $("#txload_TbleId tbody").html(tbodyContent);
            
            //duplex
            tbodyContent="";
             for (i=0;i<duplex.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+duplex[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+duplex[i]["duplex"]+"</td></tr>";
            }
            $("#duplex_TbleId tbody").html(tbodyContent);
            
            //input_drop
            tbodyContent="";
             for (i=0;i<input_drop.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+input_drop[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+input_drop[i]["input_drop"]+"</td></tr>";
            }
            $("#input_drop_TbleId tbody").html(tbodyContent);
                
            //output_drop
            tbodyContent="";
             for (i=0;i<output_drop.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+output_drop[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+output_drop[i]["output_drop"]+"</td></tr>";
            }
            $("#output_drop_TbleId tbody").html(tbodyContent);
            
            //broadcasts
            tbodyContent="";
             for (i=0;i<broadcasts.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+broadcasts[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+broadcasts[i]["broadcasts"]+"</td></tr>";
            }
            $("#broadcasts_TbleId tbody").html(tbodyContent);

             //multicast
            tbodyContent="";
             for (i=0;i<multicast.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+multicast[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+multicast[i]["multicast"]+"</td></tr>";
            }
            $("#multicast_TbleId tbody").html(tbodyContent);
            
            //runts
            tbodyContent="";
             for (i=0;i<runts.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+runts[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+runts[i]["runts"]+"</td></tr>";
            }
            $("#runts_TbleId tbody").html(tbodyContent);
                
            //giants
            tbodyContent="";
             for (i=0;i<giants.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+giants[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+giants[i]["giants"]+"</td></tr>";
            }
            $("#giants_TbleId tbody").html(tbodyContent);
            
            //input_error
            tbodyContent="";
             for (i=0;i<input_error.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+input_error[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+input_error[i]["input_error"]+"</td></tr>";
            }
            $("#input_error_TbleId tbody").html(tbodyContent);

            //crc
            tbodyContent="";
             for (i=0;i<crc.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+crc[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+crc[i]["crc"]+"</td></tr>";
            }
            $("#crc_TbleId tbody").html(tbodyContent);
            

            //int_down
            tbodyContent="";
             for (i=0;i<int_down.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+int_down[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+int_down[i]["interface_status"]+"</td></tr>";
            }
            $("#int_down_TbleId tbody").html(tbodyContent);

            //int_up
            tbodyContent="";
             for (i=0;i<crc.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+int_up[i]["interface_name"].trim()+"</td><td class='col-xs-3'>"+int_up[i]["interface_status"]+"</td></tr>";
            }
            $("#int_up_TbleId tbody").html(tbodyContent);

     });
       } 


    $('#refreshBtn').click( function () {
        //window.location = '/nab/dashboard/'+$(location).attr('href').split("/")[5]+'/'+$('#cntInt').val()+'#topN';
        LoadProcessData($('#cntInt').val());  
        LoadInterfaceData($('#cntInt').val());  
        var cntIntr=$('#cntInt').val();
        $('#pdfExportUrl').attr('href','/nab/exportPdf/'+log_Filename+'/'+cntIntr);
        $('#csvExportUrl').attr('href','/nab/exportExcel/'+log_Filename+'/'+cntIntr);
    });


// Plotting the CPU history chart
//Rest call
process = new Array();
runtime_ms = new Array();
 $.getJSON('/nab/graph_top/' + log_Filename, 
                  {},
                  function(data1) {
                        //alert(data1.length);
                        graph_json=data1.data
                        //alert(graph_json[1]["Process"]);
                         for (i=0;i<graph_json.length;i++){
    
                            process[i]=graph_json[i]["Process"].trim();
                             runtime_ms[i]=graph_json[i]["Runtime_ms"]/1000;
                           }

            
            var data = [{
      x: runtime_ms,
      y: process,
      name:'Runtime (sec)',
      type: 'bar',
      marker: {color: '#2d97f7'},
        orientation:'h'

    }];
		//var data = [trace1];
		var layout1 = {
			xaxis: {
				title: 'Runtime (sec)',
				tickfont: {
					family: 'Helvetica Neue',
					size: 10,
					color: 'black'
                }
            },

			yaxis: {
				tickfont: {
					family: 'Helvetica Neue',
					size: 10,
					color: 'black'
                }
			},
			legend: {
				 x: 0.025,
        y: 1.225,
				font: {
				size: 8
				}
			},
			margin: {
				l: 90,
				r: 0,
				t: 10,
				b: 25
			}

		};

		
		Plotly.newPlot('graph-cpu-history', data, layout1, {staticPlot: true, displayModeBar:false});
            // $('.modebar-btn--logo.plotlyjsicon.modebar-btn').hide();

     });
     


    //Rest Memory Utilization table
     
    var tbodyContent="";
    $.getJSON('/nab/memory_utilization_table/'+log_Filename, 
      {},
      function(data) {
            //alert(data1.length);
            //Get Response data
            mem_processor_pool=data.mem_processor_pool;
            
            //Populate table data
            //input_rate_bps_TbleId


             for (i=0;i<mem_processor_pool.length;i++){
                memoryTotal=mem_processor_pool[i]["Total"]; memoryUsed=mem_processor_pool[i]["Used"]; memoryFree=mem_processor_pool[i]["Free"];
                if(memoryTotal==-99) { memoryTotal='-'; }
                if(memoryUsed==-99) { memoryUsed='-'; }
                if(memoryFree==-99) { memoryFree='-'; }
                tbodyContent+="<tr><td class='col-xs-3'>"+mem_processor_pool[i]["Memory"].trim()+"</td><td class='col-xs-2'>"+memoryTotal+"</td><td class='col-xs-2'>"+memoryUsed+"</td><td class='col-xs-2'>"+memoryFree+"</td></tr>";
                
            }
            $("#memory_utilization_TbleId tbody").append(tbodyContent);

        });

    //Error Log table
     
    
    $.getJSON('/nab/log_error_code/'+log_Filename, 
      {},
      function(data) {
            //alert(data1.length);
            //Get Response data
            log_error_code=data.log_error_code;
            
            //Populate table data
            //input_rate_bps_TbleId

            var tbodyContent="";
             for (i=0;i<log_error_code.length;i++){
                tbodyContent+="<tr><td class='col-xs-2'>"+(log_error_code[i]["index"]+1)+"</td><td class='col-xs-10'>"+log_error_code[i]["inference"]+"</td></tr>";
                
            }
            
            $("#log_error_code_TbleId tbody").append(tbodyContent);

        });

// Plotting the Memory TOP Process
//Rest call
process_list = new Array();
holding_val = new Array();
 $.getJSON('/nab/graph_memory_top/'+ log_Filename+'/6', 
                  {},
                  function(data1) {
                        //alert(data1.length);
                         mem_top_process=data1['mem_top_process'];
                        //alert(graph_json[1]["Process"]);
                         for (i=0;i<mem_top_process.length;i++){
    
                            process_list[i]=mem_top_process[i][0].trim();
                             holding_val[i]=mem_top_process[i][1]/(1024*1024);
                           }

            
            var data_memory = [{
      x: holding_val,
      y: process_list,
      name:'Memory (MB)',
      type: 'bar',
      marker: {color: '#ef5250'},
        orientation:'h'

    }];
    //var data = [trace1];
    var layout2 = {
      xaxis: {
        title: 'Memory (MB)',
        tickfont: {
          family: 'Helvetica Neue',
          size: 10,
          color: 'black'
                }
            },

      yaxis: {
        tickfont: {
          family: 'Helvetica Neue',
          size: 10,
          color: 'black'
                }
      },
      legend: {
        x: 0.025,
        y: 1.225,
        font: {
        size: 8
        }
      },
      margin: {
        l: 90,
        r: 0,
        t: 10,
        b: 25
      }

    };

    
    Plotly.newPlot('graph-memory-process', data_memory, layout2, {staticPlot: true, displayModeBar:false});
            // $('.modebar-btn--logo.plotlyjsicon.modebar-btn').hide();

     });

    //TOP Process with high memory consumption

    function LoadProcessData(ProcessCnt)
    {
    var tbodyContent="";
    $.getJSON('/nab/process_memory_table/'+log_Filename+'/'+ProcessCnt,  
      {},
      function(data) {
            //console.log(data['mem_top_process'][0][0]);
            //Get Response data
            mem_top_process=data['mem_top_process'];
            
            
             for (i=0;i<mem_top_process.length;i++){
                tbodyContent+="<tr><td class='col-xs-9'>"+mem_top_process[i][0].trim()+"</td><td class='col-xs-3'>"+mem_top_process[i][1]+"</td></tr>";
                
            }
            $("#mem_process_TbleId tbody").html(tbodyContent);

        });


     }   

    //Call Interface table
    LoadProcessData(5);
    LoadInterfaceData(5);        
    //var tbodyContent='<tr><td class="col-xs-9">TenGigabitEthernate10/1</td><td class="col-xs-3">226.165</td>	</tr>';
    //$("#mbpsId tbody").append(tbodyContent);

   




	});