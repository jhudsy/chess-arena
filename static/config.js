$(document).ready(function() {
    $("#upload_button_id" ).click(function() {
        var form_data = new FormData();
        form_data.append('file', $('#file_upload')[0].files[0]);
        fetch("/upload", {method: "POST",body: form_data}).then(
              response => {response.ok ?  alert("File Uploaded OK") 
 : alert("Error in file upload");
              update_player_list();
             }
        )});
});

function get_config()
{
  fetch("/config").then(resp=>resp.json())
                  .then(function(data){
    for (var key in data)
    {
      $("#"+key).val(data[key]);
    }
  });
}

function save_config()
{
  var dict={};
  $(".config_setting").each(function(){
    dict[$(this).attr("id")]=Number($(this).val())
  });

  fetch("/config",{method: "POST", body:JSON.stringify(dict),
        headers: { "Content-Type": "application/json"} }) .then( response => 
         {response.ok ? alert("Config saved") 
                      : alert("Error saving config");}
    );
}

$("#save_config").on("click",save_config);
$("#pills-config-tab").on("show.bs.tab",function(){get_config()});
