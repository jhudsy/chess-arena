var player_list=[];
var player_to_id={};
var id_to_player={};

$("#pills-players-tab").on("show.bs.tab",() => $("#player_dropdown").trigger("change"));

//////////////////////////////////////////////////
//Update all things which need updating on the player list changing
$( document ).on("playerListChanged",
    function(event) {
      //Player dropdown in player tab
      $("#player_dropdown").empty().append($('<option>',{ value: -1, text:"(Create Player)"}));
      player_list.forEach( val => {
        $("#player_dropdown").append($('<option>',{
           value: player_to_id[val]["id"], 
           text: val 
           }));
      });
      $("#player_dropdown").val(-1);
      $("#player_dropdown").trigger('change');
    }
 );

//////////////////////////////////////////////////
$("#player_dropdown").on('change', function() {
  if (this.value!=-1){
    var player_id=this.value;
    response = fetch("/player/"+player_id).then(function(response) {
       response.json().then(function(data){
         console.log(data);
         $("#fName").val(data["fName"]);
         $("#sName").val(data["sName"]);
         $("#grade").val(data["grade"]);
         $("#active").prop("checked",data["active"].toLowerCase()=="true");
         $("#num_graded_games").val(data["num_graded_games"]);

         $("#player_club_dropdown").empty();
	 $("#player_club_dropdown").append($('<option>',{
		 value: -1,
		 text: "(None)"
	 }));

         club_list.forEach(function(c){
			 $("#player_club_dropdown").append($('<option>',{
				 value: club_to_id[c]["id"],
				 text: c
			 }));
         });
         if (data["club_id"]=="None")
	   $("#player_club_dropdown").val(-1)
         else
	   $("#player_club_dropdown").val(data["club_id"])

         $("#avoid_list").empty();

         player_list.forEach(function(p){
               if ($("#player_dropdown").val()!=player_to_id[p]["id"]){
                 $("#avoid_list").append($('<option>',{
                   value: player_to_id[p]["id"],
                   text: p
                 }));
               }
         });
         $("#avoid_list").val(data["avoids"]);

         $("#player_games_list").find("tr:gt(0)").remove();

         getGames(player_id,true,function(data){
           $("#player_games_list").append(get_game_list_content("#player_games_list",data));
         });
         getGames(player_id,false,function(data){
           $("#player_games_list").append(get_game_list_content("#player_games_list",data));
         });
       });
    });
    
  }
  else{
    $("#fName").val("");
    $("#sName").val("");
    $("#grade").val(0);
    $("#player_club_dropdown").empty();
    $("#num_graded_games").val(0);
    $("#avoid_list").empty();
    $("#active").prop("checked",true)

    $("#player_games_list").find("tr:gt(0)").remove();

    player_list.forEach(function(p){
       if ($("#player_dropdown").val()!=player_to_id[p]["id"]){
           $("#avoid_list").append($('<option>',{
             value: player_to_id[p]["id"],
             text: p
           }));
       }
    })

    $("#player_club_dropdown").append($('<option>',{
                 value: -1,
                 text: "(None)"
         }));

         club_list.forEach(function(c){
             $("#player_club_dropdown").append($('<option>',{
                                 value: club_to_id[c]["id"],
                                 text: c
             }));
         });
  }
});

//////////////////////////////////////////////////
$("#clearAvoids").on("click", () => {
  $("#avoid_list").val("");
});

//////////////////////////////////////////////////
async function update_player_list(){
  var response= await fetch("/players");
  var data= await response.json();
 
  player_list=[]
  player_to_id={}
  id_to_player={}
  
  for (let i=0;i<data.length;i++)
  {
    player_list.push(data[i]["fName"]+" "+data[i]["sName"])
    player_to_id[data[i]["fName"]+" "+data[i]["sName"]]=data[i]
    id_to_player[data[i]["id"]]=data[i]
  }
  $( document ).trigger("playerListChanged");
}
//////////////////////////////////////////////////

$("#delete_player").on("click",
   function(){
     if ($("#player_dropdown").val()==-1)
        return;

     fetch("player/"+$("#player_dropdown").val(), {method: 'DELETE'})
          .then(res=>res.text())
          .then(() => {update_player_list();});
   }
);

$("#create_update_player").on("click",
   function(){
     payload={fName:$("#fName").val(),
              sName:$("#sName").val(),
              grade:$("#grade").val(),
              num_graded_games:$("#num_graded_games").val(),
              avoids:$("#avoid_list").val(),
              active:$("#active").prop("checked"),
	      club:$("#player_club_dropdown").val()
             };
     id=$("#player_dropdown").val()
     if (id==-1)
     {
        fetch("/player",{method:"POST",
                         body:JSON.stringify(payload),
                         headers: {
                           "Content-Type": "application/json"
                         }}
        ).then(resp => resp.json())
         .then(data => {update_player_list(); alert("player created");});
     } else
     {
        fetch("/player/"+id,{method:"PUT",
                         body:JSON.stringify(payload),
                         headers: {
                           "Content-Type": "application/json"
                         }}
        ).then(resp => resp.json())
         .then(data => {update_player_list(); alert("player updated");});
     }
   });

$( document ).ready(function() {
  update_player_list();
});

