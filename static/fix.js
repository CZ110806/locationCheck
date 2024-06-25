var vid1 = ""


function upload_video(){
    
    
    var fd = new FormData();

    var files = $('#filePath')[0].files;
    // vid1.src = files
     //vid1.onduractionchange = function(){
       // alert(this.duration)
     //}
    // Check file selected or not
    if(files.length > 0 ){
       fd.append('file',files[0]);
       console.log(files[0])

       $.ajax({
          url: '/upload',
          type: 'post',
          data: fd,
          contentType: false,
          processData: false,
          success: function(response){
             if(response != 0){

                    vid1 = response           
             }else{
                alert('file not uploaded');
             }
          },
       });
    }else{
       alert("Please select a file.");
    }
}



function getresult(){
    $("#result").text("")
    
    var redo = document.getElementById("redo")
    redo.style.visibility = "hidden"
    document.getElementById("googleMap").style.visibility = "hidden"
    // var load = document.getElementById("loader")
    // load.style.visibility = "visible"
    $.ajax({
        url:"/result/" + vid1, 
        success:function(result){
            
            
            var mapProp= {
                center:new google.maps.LatLng(51.508742,-0.120850),
                zoom:5,
                };
            // load.style.visibility = "hidden"
            var map = new google.maps.Map(document.getElementById("googleMap"),mapProp); 
            document.getElementById("googleMap").style.visibility = "visible"
            const uluru = {lat: -25.344, lng: 131.031};
            var count = 0;
            var legend = [];
            var empty = [{'mark': "", 'location': ""}];
            buildtable(empty);

            for(var key in result){
                count++;
                var value = result[key];
                const pos = {lat: value[0], lng: value[1]}
                const marker = new google.maps.Marker({
                    position: pos,
                    label: count.toString(),
                    map: map,
                });
	        map.setCenter(marker.getPosition());
		legend.push({'mark': count, 'location': key});
            }
            buildtable(legend);
            legend = [];
            if(Object.keys(result).length === 0){
                $("#result").text("Sorry, could not find any valid locations, maybe try another frame rate.")
                var redo = document.getElementById("redo")
                redo.style.visibility = "visible"
                var videolength = "redo";
                const request = new XMLHttpRequest();
                request.open('POST', `/ProcessVideolength/${JSON.stringify(videolength)}`);
                request.send();
            }
        }
        
    });
}

function buildtable(data){
    var table = document.getElementById('table_content');
    table.innerHTML = "";
    
    for(var i = 0; i < data.length; i++){
        var row = `<tr>
                        <td>${data[i].mark}</td>
                        <td>${data[i].location}</td>
                    </tr>`
        table.innerHTML += row;
        console.log(data[i].mark);
        console.log(data[i].location);
    }
}

// $(function(ready){
//     $('#filePath').change(function(event) {


//         var tempPath = URL.createObjectURL(event.target.files[0]);
//         alert(tempPath)
//         console.log(tempPath)
//         var path = String.raw`${tempPath}`;
//         console.log(typeof path);
//         const request = new XMLHttpRequest();
//         var videoPath = "/GetVideoPath/name"
//         var jsonPath = JSON.parse('{"path": path}')
//         console.log(typeof jsonPath)

        // request.open('POST', videoPath);
        // console.log( `/GetVideoPath/${JSON.stringify(path)}`)
        // //request.open('POST', "/GetVideoPath/helloo");
        // request.send();


//     });
// });


// $('#filePath').change( function(event) {
//     console.log("HERE")
//     // var tmppath = URL.createObjectURL(event.target.files[0]);
//     //     $("img").fadeIn("fast").attr('src',URL.createObjectURL(event.target.files[0]));
        
//     //     $("#disp_tmp_path").html("Temporary Path(Copy it and try pasting it in browser address bar) --> <strong>["+tmppath+"]</strong>");
// });

function getPath(){
    var inputPath = document.getElementById("filePath");
    console.log(inputPath);
    // var tmppath = URL.createObjectURL(inputPath);
    // console.log(tmppath);

    // var tmppath = URL.createObjectURL(event.target.files[0]);


    // console.log(inputPath.value);
    var path = String.raw`${inputPath.value}`;
    const request = new XMLHttpRequest();
    request.open('POST', `/GetVideoPath/${JSON.stringify(path)}`);
    request.send();
}




