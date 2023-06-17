function fill_crosstable(data){
  var tab=$("#crosstable").DataTable();
  tab.clear();
  
  
  data.forEach(function(row){
    var str=""
    row["games"].forEach(function(g){str+=" "+g});
    tab.row.add([ row["id"],row["fName"],row["sName"],row["numGamesPlayed"],row["points"],parseFloat(row["percent"]).toFixed(2),str])
    })

    /*var str="<tr>"
    str+="<td>"+row["id"]+"</td>"
    str+="<td>"+row["fName"]+"</td>"
    str+="<td>"+row["sName"]+"</td>"
    str+="<td>"+row["numGamesPlayed"]+"</td>"
    str+="<td>"+row["points"]+"</td>"
    str+="<td>"+row["percent"]+"</td>"
    str+="<td>"
    row["games"].forEach(function(g){
      str+=" "+g
    });
    str+="</td></tr>"
    $("#crosstable tbody").append(str)
  })*/

  tab.draw();
}

$(document).ready(function() {
   $("#crosstable").DataTable({"pageLength": 100, autoWidth: false,
                                columnDefs:[ 
                                   {orderable: false, targets: 6},
                                   {"width":"5%", "targets":0},
                                   {"width":"10%", "targets":1},
                                   {"width":"10%", "targets":2},
                                   {"width":"6%", "targets":3},
                                   {"width":"5%", "targets":4},
                                   {"width":"5%", "targets":5},
                                   {"width":"30%", "targets":6}
 ]}); 
});

$("#pills-crosstable-tab").on("show.bs.tab", function(){
    fetch("/crosstable").then(resp=>resp.json())
         .then(data=>fill_crosstable(data))
  }
);
