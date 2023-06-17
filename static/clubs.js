var club_list=[];
var id_to_club={};
var club_to_id={};

$("#pills-club-tab").on("show.bs.tab",()=>$("#club_dropdown").trigger("change"));

$( document ).on("clubListChanged",
  function(event){
    $("#club_dropdown").empty().append($('<option>',{ value: -1, text:"(Create Club)"}));
    club_list.forEach( val => {
      $("#club_dropdown").append($('<option>',{
        value: club_to_id[val]["id"],
        text: val
       }));
    });
    $("#club_dropdown").val(-1);
    $("#club_dropdown").trigger('change');
  }
);

$("#club_dropdown").on('change', function() {
  if (this.value!=-1){
    var club_id=this.value;
    /*fetch("/club/"+club_id)
      .then(resp => resp.json())
      .then(function(data){
         $("#club_name").val(data["name"]);
      });
    */
    $("#club_name").val(id_to_club[club_id]["name"]);
  }
  else{
    $("#club_name").val("");
  }
});

function update_club_list(){
	fetch("/clubs")
	  .then(resp=>resp.json())
	  .then(function(data){
		  club_list=[]
		  club_to_id={}
		  id_to_club={}

		  for (let i=0;i<data.length;i++)
		  {
			  club_list.push(data[i]["name"]);
			  club_to_id[data[i]["name"]]=data[i];
			  id_to_club[data[i]["id"]]=data[i];
		  }
	$( document ).trigger("clubListChanged");
	  });
}

$("#delete_club").on("click",
  function(){
	  if ($("#club_dropdown").val()==-1)
		  return;

          fetch("club/"+$("#club_dropdown").val(),{method:'DELETE'})
	    .then(res=>res.json())
	    .then(() =>{update_club_list();});
  }
);

$("#create_update_club").on("click",
  function(){
	  payload={name:$("#club_name").val()}
	  id=$("#club_dropdown").val()
	  if (id==-1)
	  {
		  fetch("/club",{method:"POST",
		       body:JSON.stringify(payload),
		       headers: {
			       "Content-Type": "application/json"
		       }}).then(resp=>resp.json())
		       .then(data => {update_club_list(); alert("club created");});
		       
	  } else
	  {
		  fetch("/club/"+id,{method:"PUT",
		      body: JSON.stringify(payload),
		       headers: {
                           "Content-Type": "application/json"
                         }}).then(resp=>resp.json())
			    .then(data=> {update_club_list(); alert("club updated");});
	  }
  });

$( document ).ready(function() {
	update_club_list();
});
