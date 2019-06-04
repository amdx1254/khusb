var currentDirId;
var urls;
var uploadid;
var item = {'Parts': []};
var finished = 0;
var uploaded_size = [];

$(document).ready(function () {
    var token = document.getElementById("token").value
    currentDirId = document.getElementById("path").value
    $.ajaxSetup({
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
});



function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("Table");
    switching = true;
    dir = "asc";
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function make_upload(file_len, file_num) {
    if(file_len > file_num){
        var unloadHandler = function () {
            $.post('/api/upload_abort/', {
                        'name': $("#uploadInput")[0].files[file_num].name,
                        'path': currentDirId,
                        'uploadid': uploadid
            });
        }

        window.onunload = function() {
            unloadHandler();
            alert('Bye.');
        }

        $.ajax({
            method: "POST",
            data: {
                'name': $("#uploadInput")[0].files[file_num].name,
                'is_directory': false,
                'path': currentDirId,
                'size': $("#uploadInput")[0].files[file_num].size
            },
            url: '/api/upload_start/',
            success: function (data) {
                urls = data['url'];
                uploadid = data['uploadid']
            },
            error: function (data) {
                alert("An error occured, please try again later")
            }
        }).done(function () {
            finished = 0;
            $('#uploadProgress'+file_num).val(0).show();
            var slice_length = 1024 * 1024 * 1024 * 5;
            var processed = 0;
            var len_url = Object.keys(urls).length;
            var chunk_num = 1;
            var len_file = $("#uploadInput")[0].files[file_num].size;
            item = {'Parts': []};
            uploaded_size = [];
            for (url in urls) {
                uploaded_size.push(0);
            }
            for (url in urls) {
                filedata = $("#uploadInput")[0].files[file_num].slice(processed, processed + slice_length);
                upload_file(urls[url], filedata, chunk_num, len_url, len_file, file_num);
                processed = processed + slice_length;
                chunk_num++;
            }
        });
    } else {
        location.reload();
    }

}

function upload_file(url, filedata, chunk_id, len_url, len_file, file_num) {
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", function (e) {
        uploaded_size[chunk_id - 1] = e.loaded;
        var sum = 0;
        for (var i = 0; i < len_url; i++) {
            sum = sum + uploaded_size[i];
        }
        var per = sum * 100 / len_file;
        $('#uploadProgress'+file_num).val(per);
        $('#size'+file_num).html(sum+'/'+len_file);
        if (e.lengthComputable) {
            //console.log(e.loaded / (e.total*len_url));

        }
    });


    xhr.open("PUT", url);
    xhr.send(filedata);
    xhr.onreadystatechange = function () {
        if (this.readyState == this.HEADERS_RECEIVED) {
            var etag = xhr.getResponseHeader("ETag");
            etag = etag.replace("/\"/gi", "");
            item['Parts'].push({'ETag': etag, 'PartNumber': chunk_id});
            finished++;
            if (finished == len_url) {
                window.onbeforeunload = null
                $.ajax({
                    method: "POST",
                    data: {
                        'name': $("#uploadInput")[0].files[file_num].name,
                        'path': currentDirId,
                        'uploadid': uploadid,
                        'size': len_file,
                        'items': JSON.stringify(item)
                    },
                    url: '/api/upload_complete/',
                    success: function (data) {
                        window.onunload=null;
                        make_upload($("#uploadInput")[0].files.length, file_num+1);
                    },
                    error: function (data) {
                        alert("An error occured, please try again later")
                    }
                });
            }
        }
    }
}

$(document).on('click', '#uploadBtn', async function () {
    make_upload($("#uploadInput")[0].files.length, 0);
});

$(document).on('click', '#createBtn', async function () {
    $.ajax({
        method: "POST",
        data: {
            'name': $("#directoryName").val(),
            'path': currentDirId
        },
        url: '/api/create/',
        success: function (data) {
            location.reload()
        },
        error: function (data) {
            alert("An error occured, please try again later")
        }
    });
});

$(document).on('change', '#uploadInput', function() {
    var files = $("#uploadInput")[0].files;
    var html="";
    for(var i=0;i<files.length;i++) {
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+files[i].name+"</td><td><progress max=\"100\" value=\"0\" id=\"uploadProgress"+i+"\"></progress></td><td style='text-align: left;'><span id='size"+i+"'>0/"+files[i].size+"</span></td></tr>";
    }
    $("#uploadeditem").html(html);
});