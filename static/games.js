
//if playerID=-1, return all games. If active=True, only show active games, if false, show finished games. 
//Game will ID, White, Black, Result
function getGames(playerID,active,processing_function){
  if (playerID!=-1)
    fetch("/games/"+playerID+"/"+(active==true? 1 : 0))
             .then( resp => resp.json())
             .then( data => {processing_function(data)})
  else
    fetch("/games/"+(active==true? 1 : 0))
             .then( resp => resp.json())
             .then( data => {processing_function(data)})
}

function get_game_list_content(divID,games){
  games.forEach(function(g){
    var str= "<tr  "+(g['result']=='GameResult.ACTIVE'? 'class=table-info':'')+"  ><td>"+
           id_to_player[g['white_player_id']]["fName"]+" "+
           id_to_player[g['white_player_id']]["sName"]+"</td><td> "+
           id_to_player[g['black_player_id']]["fName"]+" "+
           id_to_player[g['black_player_id']]["sName"]+"</td><td> "+
           "<select class='form-select game_result' id='"+g["id"]+"'>"+
             "<option value='active' "+(g['result']=='GameResult.ACTIVE'? "selected":"")+" >Active</option>"+
             "<option value='white_win' "+(g['result']=='GameResult.WHITE_WIN'? "selected":"")+">White win</option>"+
             "<option value='black_win' "+(g['result']=='GameResult.BLACK_WIN'? "selected":"")+">Black win</option>"+
             "<option value='draw' "+(g['result']=='GameResult.DRAW'? "selected":"")+">Draw</option>"+
           "</select></td><td>"+
           //"<button type='button' class='btn update_game btn-secondary' id="+g["id"]+">Update</button></td><td>"+
           "<button type='button' class='btn delete_game btn-secondary' id="+g["id"]+">Delete</button></td>"+
           "</tr>";
    $(divID+" tbody").append(str);
  });
}

$(document).on('click', '.delete_game', function() {
    var game_id=$(this).attr("id");
    fetch("/game/"+game_id,{method: 'DELETE'})
        .then(resp => resp.json())
        .then(data => {$(this).closest("tr").remove()});
  });

/* OLD CODE, SEE NEW CODE BELOW
$(document).on('click','.update_game', function() {
    var game_id=$(this).attr("id");
    var game_result=$(".game_result#"+game_id).val();
    fetch("/game/"+game_id+"/"+game_result)
        .then(resp=>resp.json())
        .then(data => alert("game result updated"))});
*/
//New code to allow for results to be captured immediately
$(document).on('change','.game_result',function(){
  var game_id=$(this).attr("id");
  var game_result=$(this).val();
  fetch("/game/"+game_id+"/"+game_result)
    .catch(error=>alert("error"))
  if (game_result=="active")
    $(this).closest("tr").attr("class","table-info");
  else
    $(this).closest("tr").attr("class","");
});
//////////////for games tab
$("#refresh_game_list").on("click",function(){
   $("#global_games_list").find("tbody tr").remove();
   getGames(-1,true,function(data){
     $("#global_games_list").append(get_game_list_content("#global_games_list",data));
     getGames(-1,false,function(data){ //put in here to have order preseved
       $("#global_games_list").append(get_game_list_content("#global_games_list",data));
     });
   });
});

$("#pills-games-tab").on("show.bs.tab",() => $("#refresh_game_list").trigger("click"));
