function get_free_players(fnc){
  fetch("/players_to_match").then( (resp) => resp.json())
                            .then( (data) => fnc(data));
}

//This function reloads the player pairs available for pairing. 
function update_player_pairs(){
  $("#suggested_pairings").find("tbody tr").remove();
  $("#white").empty().append($('<option>',{
             value: -1,
             text: ""
           }));
  $("#black").empty().append($('<option>',{
             value: -1,
             text: ""
           }));
  get_free_players((pl) => {
    pl.forEach((p) => {
      $("#white").append($('<option>',{
             value: p["id"],
             text: p["fName"]+" "+p["sName"]
           }));
      $("#black").append($('<option>',{
             value: p["id"],
             text: p["fName"]+" "+p["sName"]
           }));

    });
  });
}

function make_auto_match(){

  fetch("/matchings").then(resp => resp.json())
                     .then(function(data){

    $("#suggested_pairings").find("tbody tr").remove();
    data.forEach(
      function(m){
        str=""
        str+="<tr>";
        str+="<td><a class='player_info' href=#"+m[0]+">";
        str+=id_to_player[m[0]]["fName"];
        str+=" ";
        str+=id_to_player[m[0]]["sName"];
        str+="</a></td>";
        str+="<td><a class='player_info' href=#"+m[1]+">";
        str+=id_to_player[m[1]]["fName"];
        str+=" ";
        str+=id_to_player[m[1]]["sName"];
        str+="</a></td>";
        str+="<td><button type='button' class='btn accept_pairing btn-secondary' id='"+m[0]+"_"+m[1]+"'>Accept</button></td>";
        //str+="<td><button type='button' class='btn accept_pairing_f btn-secondary' id='"+m[1]+"_"+m[0]+"'>Flip colors and Accept</button></td>";
        str+="<td><button type='button' class='btn flip btn-secondary' id='"+m[1]+"_"+m[0]+"'>Flip colors</button></td>";
        str+="</tr>";

        $("#suggested_pairings tbody").append(str);
    });
       
  });
}

//convenience function to prevent players being matched against themselves
$("#white").on("change", () =>
 {
   $("#black option").removeAttr("disabled");
   if ($("#white").val()!=-1)
     $("#black option[value='"+$("#white").val()+"']").attr("disabled","disabled");
 }
);

$("#black").on("change", () =>
 {
   $("#white option").removeAttr("disabled");
   if ($("#black").val()!=-1)
     $("#white option[value='"+$("#black").val()+"']").attr("disabled","disabled");
 }
);

function match_players(white,black){
    fetch("/game/"+white+"/"+black,{method: 'POST'}).then((resp) => resp.json()).then( (data) => update_player_pairs());
}

$("#pills-pairings-tab").on("show.bs.tab",update_player_pairs);
$("#refresh_players").on("click",update_player_pairs);
$("#manual_pair").on("click", function(){  
  if ($("#white").val()!=-1 & $("#black").val()!=-1)
  {
     match_players($("#white").val(),$("#black").val())
     $("#suggested_pairings").find("tbody tr").remove();
  }
 }
);

$("#make_auto_pair").on("click",function(){
make_auto_match();
});

$(document).on('click','.accept_pairing', function(){
  $(this).prop('disabled',true);
  var a=$(this).attr("id").split("_");
  match_players(a[0],a[1]);
  $(this).closest("tr").remove();
});

/*
$(document).on('click','.accept_pairing_f', function(){
  $(this).prop('disabled',true);
  var a=$(this).attr("id").split("_");
  match_players(a[0],a[1]);
  $(this).closest("tr").remove();
});
*/

$(document).on('click','.flip', function(){
  var button=$(this);
  var tr=button.closest("tr");
  var td1=$(tr).find("td:eq(0)");
  var td2=$(tr).find("td:eq(1)");
  var ttd=$(td1).html();
  $(td1).html((td2).html());
  $(td2).html(ttd);
  var accept_button=$(tr).find("button:eq(0)")
  var ids=$(accept_button).attr("id").split("_");
  $(accept_button).attr("id",ids[1]+"_"+ids[0]);
  var ids=$(accept_button).attr("id").split("_");
});

//functions to populate summary
$("#white").on("change",function(){
  if ($("#white").val()!=-1){
    fetch("/player_summary/"+$("#white").val())
        .then(resp=>resp.json())
        .then(function(data){
          update_w_summary(data["fName"]+" "+data["sName"],
                           data["grade"],
                           data["num_games"],
                           data["num_graded_games"],
                           data["num_win"],
                           data["num_draw"],
                           data["num_lost"],
                           data["performance_rating"],
                           data["avoids"],
                           data["club"]
);
        });
  }
  else {
          update_w_summary("White Player",0,0,0,0,0,0,0,[],"None");
  }
});

$("#black").on("change",function(){
  if ($("#black").val()!=-1){
    fetch("/player_summary/"+$("#black").val())
        .then(resp=>resp.json())
        .then(function(data){
          update_b_summary(data["fName"]+" "+data["sName"],data["grade"],data["num_games"],data["num_graded_games"],data["num_win"],data["num_draw"],data["num_lost"],data["performance_rating"],data["avoids"],data["club"]);
        });
  }
  else {
          update_b_summary("Black Player",0,0,0,0,0,0,0,[],"None");
  }
});

function update_w_summary(name,grade,num_games,num_graded_games,num_won,num_draw,num_lost,performance_rating,avoids,club)
{
  $("#w_SummaryName").text(name);
  $("#w_grade").text(grade);
  $("#w_num_games").text(num_games);
  $("#w_num_graded_games").text(num_graded_games);
  $("#w_num_won").text(num_won)
  $("#w_num_draw").text(num_draw)
  $("#w_num_lost").text(num_lost)
  $("#w_perf_rating").text(parseFloat(performance_rating).toFixed(0))
  $("#w_club").text(club)
  avStr="<ul>"
  avoids.forEach(a => avStr=avStr+"<li>"+a+"</li>")
  avStr=avStr+"</ul>"
  $("#w_avoids").html(avStr)
}

function update_b_summary(name,grade,num_games,num_graded_games,num_won,num_draw,num_lost,performance_rating,avoids,club)
{
  $("#b_SummaryName").text(name);
  $("#b_grade").text(grade);
  $("#b_num_games").text(num_games);
  $("#b_num_graded_games").text(num_graded_games);
  $("#b_num_won").text(num_won)
  $("#b_num_draw").text(num_draw)
  $("#b_num_lost").text(num_lost)
  $("#b_perf_rating").text(parseFloat(performance_rating).toFixed(0))
  $("#b_club").text(club)
  avStr="<ul>"
  avoids.forEach(a => avStr=avStr+"<li>"+a+"</li>")
  avStr=avStr+"</ul>"
  $("#b_avoids").html(avStr)
}

$(document).on("click",".player_info",function(){
  var id=$(this).attr("href").replace('#','');
  var tdindex=$(this).closest("td").index()
  fetch("/player_summary/"+id).then(resp=>resp.json()).then(function(data){
    var fnc=update_w_summary
    if (tdindex==1)
       fnc=update_b_summary
    fnc(data["fName"]+" "+data["sName"],data["grade"],data["num_games"],data["num_graded_games"],data["num_win"],data["num_draw"],data["num_lost"],data["performance_rating"],data["avoids"],data["club"]);
  });
});
