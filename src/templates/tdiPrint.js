       function printDiv() {
         window.frames["print_frame"].document.body.innerHTML = document.getElementById("table-responsive-sm").innerHTML;
         window.frames["print_frame"].window.focus();
         window.frames["print_frame"].window.print();
       }