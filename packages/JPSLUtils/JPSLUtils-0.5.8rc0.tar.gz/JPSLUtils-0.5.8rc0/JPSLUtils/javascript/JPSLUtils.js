// Jupyter Notebook Utilities
JPSLUtils = new Object();
/*
Initialization
*/
JPSLUtils.init = function(){
    // Run all input table cells to make sure the tables are showing and
    // active. Also hide the table creation code.
    JPSLUtils.hide_input_table_code();
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].execute();
            }
        }
    }
    // Hide the code for cells marked with metadata.JPSL.hide_code = true.
    JPSLUtils.hide_hide_code_code();
};

/*
Cell Utilities
*/

JPSLUtils.select_containing_cell = function(elem){
    //Create a synthetic click in the cell to force selection of the cell
    // containing the element (elem).
    var event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
    });
    var cancelled = !elem.dispatchEvent(event);
    if (cancelled) {
    // A handler called preventDefault.
    alert("Something is wrong. Try rerunning the cell.");
    }
};

JPSLUtils.select_cell_immediately_below = function(){
    Jupyter.notebook.select_next(true);
};

JPSLUtils.replace_text_of_current_cell = function(text){
    Jupyter.notebook.get_selected_cell().set_text(text);
};

JPSLUtils.insert_newline_at_end_of_current_cell = function(text){
    var lastline = Jupyter.notebook.get_selected_cell().code_mirror.doc.
        lineCount();
    Jupyter.notebook.get_selected_cell().code_mirror.doc.setCursor(lastline,0);
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
         replaceSelection("\n" + text);
};

JPSLUtils.insert_text_at_beginning_of_current_cell = function(text){
    // append \n to line insert as a separate line.
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
           setCursor({line:0,ch:0});
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
           replaceSelection(text);
};

JPSLUtils.hide_hide_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_on_print==true){
                celllist[i].element[0].classList.add("hidden");
            }
        }
    }
    JPSLUtils.hide_hide_code_on_print_code();
};

JPSLUtils.show_hide_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_on_print==true){
                celllist[i].element[0].classList.remove("hidden");
            }
        }
    }
        JPSLUtils.show_hide_code_on_print_code();
};

JPSLUtils.hide_input_table_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_input_table_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

JPSLUtils.hide_hide_code_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_hide_code_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

JPSLUtils.hide_hide_code_on_print_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code_on_print==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_hide_code_on_print_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code_on_print==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

/*
input/textarea utilities
*/

JPSLUtils.record_input = function (element){
    var nodetype = element.nodeName.toLowerCase();
    var tempval = ''+element.value;//force to string
    var tempsize = ''+element.size;
    if (tempsize==null){tempsize='7'};
    var tempclass = element.className;
    if (tempclass==null){tempclass=''};
    var tempid = element.id;
    if (tempid==null){tempid=''};
    var tempelem = document.createElement(nodetype);
    tempelem.className =tempclass;
    tempelem.id=tempid;
    tempelem.setAttribute('size',tempsize);
    if (nodetype=='input'){
        tempelem.setAttribute('value',tempval);
    } else {
        tempelem.innerHTML = element.value;
    }
    tempelem.setAttribute('onblur','JPSLUtils.record_input(this)');
    element.replaceWith(tempelem);
};

/*
Python Execution
*/

JPSLUtils.executePython = function(python) {
    return new Promise((resolve, reject) => {
        var callbacks = {
            iopub: {
                output: (data) => resolve(data.content.text.trim())
            }
        };
        Jupyter.notebook.kernel.execute(`print(${python})`, callbacks);
    });
};

JPSLUtils.executePython2 = function(python) {
    return new Promise((resolve, reject) => {
        var callbacks = {
            iopub: {
                output: (data) => resolve(JSON.stringify(data, null, 4))
            }
        };
        Jupyter.notebook.kernel.execute(`print(${python})`, callbacks);
    });
};

/*
Dialogs
*/

JPSLUtils.record_names = function(){
    var currentcell = Jupyter.notebook.get_selected_cell();
    var dlg = document.createElement('div');
    dlg.setAttribute('id','get_names_dlg');
    var tmp = document.createElement('H4');
    var inststr = "In the box below type your name and your partners' names";
    inststr += " (one per line):";
    tmp.innerHTML=inststr
    dlg.append(tmp);
    tmp = document.createElement('div');
    tmp.innerHTML = '<textarea cols="30" onblur="JPSLUtils.record_input(this)"/>';
    dlg.append(tmp);
    $(dlg).dialog({modal:true,
                  classes:{'ui-dialog-titlebar-close' : 'hidden'
                  },
                  buttons:[
                  {text: 'OK/Do It',
                  click: function(){var rcrd = document.getElementById(
                                    'Last-User');
                                    var parent = rcrd.parentNode;
                                    var dlg = document.getElementById(
                                    'get_names_dlg');
                                    var textboxes = dlg.querySelectorAll(
                                    "textarea");
                                    var tmp = document.createElement('div');
                                    tmp.setAttribute('id','Grp-names');
                                    tmp.
                                    setAttribute('style','font-weight:bold;');
                                    var refeed = /\r?\n|\n\r?|\n/g;
                                    var tmpstr = 'Partners: '+ textboxes[0]
                                    .innerHTML.replace(refeed,'; ');
                                    //tmpstr.replace(refeed,'; ');
                                    tmp.innerHTML = tmpstr;
                                    tmpstr = '# '+rcrd.innerHTML +'\n# '
                                    +tmpstr;
                                    //rcrd.append(tmp);
                                    JPSLUtils.
                                    insert_newline_at_end_of_current_cell(
                                    tmpstr);
                                   $(this).dialog('destroy');}}
                  ]})
    Jupyter.notebook.focus_cell();//Make sure keyboard manager doesn't grab inputs.
    Jupyter.notebook.keyboard_manager.enabled=false;
    dlg.focus();
    Jupyter.notebook.keyboard_manager.enabled=false; //Make sure keyboard manager doesn't grab inputs.
};

/*
JPSL Tools Menu
*/
JPSLUtils.createJPSLToolsMenu = function(){
    if(!document.getElementById('JPSLToolsmnu')){
        var newselect=document.createElement('select');
        newselect.id = 'JPSLToolsmnu';
        newselect.classList.add('form-control'); //class to match notebook formatting
        newselect.classList.add('select-xs'); //class to match notebook formatting
        newselect.setAttribute('style','color:green;')
        newselect.onchange=function(){
            var lastvalue = this.value;
            this.value='JPSL Tools';
            if (lastvalue=='Hide Cells'){
                JPSLUtils.hide_hide_on_print_cells();
            }
            if (lastvalue=='Undo Hide Cells'){
                JPSLUtils.show_hide_on_print_cells();
            }
            if (lastvalue=='Show Table Creation Code'){
                JPSLUtils.show_input_table_code();
            }
            if (lastvalue=='Hide Table Creation Code'){
                JPSLUtils.hide_input_table_code();
            }
            if (lastvalue=='Show Hidden Code'){
                JPSLUtils.show_hide_code_code();
            }
            if (lastvalue=='Re-Hide Hidden Code'){
                JPSLUtils.hide_hide_code_code();
            }
        }
        var optiontxt = '<option title="Choose an option below"> \
        JPSL Tools</option>';
        optiontxt+='<option title="Hide cells set to hide-on-print"> \
        Hide Cells</option>';
        optiontxt+='<option title="Redisplay cells set to hide-on-print"> \
        Undo Hide Cells</option>';
        optiontxt+='<option title="Show input table creation code"> \
        Show Table Creation Code</option>';
        optiontxt+='<option title="Hide input table creation code"> \
        Hide Table Creation Code</option>';
        optiontxt+='<option title="Show hidden code cells"> \
        Show Hidden Code</option>';
        optiontxt+='<option title="Re-hide hidden code cells"> \
        Re-Hide Hidden Code</option>';
        newselect.innerHTML=optiontxt;
        document.getElementById('maintoolbar-container').appendChild(newselect);
    }
}