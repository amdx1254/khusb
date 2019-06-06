var currentDirId;
var urls;
var uploadid;
var item = {'Parts': []};
var finished = 0;
var uploaded_size = [];
var checked_items = [];
var parendDirId;
var isfavorite = false;
$(document).ready(function () {
    var token = document.getElementById("token").value
    currentDirId = document.getElementById("path").value
    parendDirId = document.getElementById("parent").value
    $.ajaxSetup({
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    list_files();
});



$(document).ready(function () {
    //Show contextmenu:
    $(document).contextmenu(function (e) {
        //Get window size:
        var winWidth = $(document).width();
        var winHeight = $(document).height();
        //Get pointer position:
        var posX = e.pageX;
        var posY = e.pageY;
        //Get contextmenu size:
        var menuWidth = $(".contextmenu").width();
        var menuHeight = $(".contextmenu").height();
        //Security margin:
        var secMargin = 10;
        //Prevent page overflow:
        if (posX + menuWidth + secMargin >= winWidth
            && posY + menuHeight + secMargin >= winHeight) {
            //Case 1: right-bottom overflow:
            posLeft = posX - menuWidth - secMargin + "px";
            posTop = posY - menuHeight - secMargin + "px";
        } else if (posX + menuWidth + secMargin >= winWidth) {
            //Case 2: right overflow:
            posLeft = posX - menuWidth - secMargin + "px";
            posTop = posY + secMargin + "px";
        } else if (posY + menuHeight + secMargin >= winHeight) {
            //Case 3: bottom overflow:
            posLeft = posX + secMargin + "px";
            posTop = posY - menuHeight - secMargin + "px";
        } else {
            //Case 4: default values:
            posLeft = posX + secMargin + "px";
            posTop = posY + secMargin + "px";
        }
        ;
        //Display contextmenu:
        $(".contextmenu").css({
            "left": posLeft,
            "top": posTop
        }).show();
        //Prevent browser default contextmenu.
        return false;
    });
    //Hide contextmenu:
    $(document).click(function () {
        $(".contextmenu").hide();
    });
});

function byteTosize(byte){
    var result = byte + "Byte";
    if(byte > 1024 && byte < 1024*1024){
        result = byte/1024;
        result = result.toFixed(2);
        result = result + "KB";
    } else if(byte >= 1024*1024 && byte < 1024*1024*1024) {
        result = byte/(1024*1024);
        result = result.toFixed(2);
        result = result + "MB";
    } else if(byte >= 1024*1024*1024 && byte < 1024*1024*1024*1024) {
        result = byte/(1024*1024*1024);
        result = result.toFixed(2);
        result = result + "GB";
    }
    return result;
}

function list_files() {
    $.ajax({
            method: "GET",
            url: '/api/list'+currentDirId,
            success: function (data) {
                 load_files('', data['items'])
            },
            error: function (data) {
                alert("An error occured, please try again later")
            }
    });
}

function dateToString(date) {
    var year = date.substring(0, 10);
    var time = date.substring(11,16);
    return year + " " + time;
}

function load_files(value, files) {
    var html = "";

    $("#items").html("")
    var name;
    var modified;
    var displayname;
    if (currentDirId != "/" || isfavorite) {
        html += "<tr class='hover'>";
        html += "<td></td>";
        if(isfavorite){
            html += "<td style='text-align: left;'><a class='file' href='/list" + currentDirId + "'>..</a></td>";
        } else
        {
            html += "<td style='text-align: left;'><a class='file' href='/list" + parendDirId + "'>..</a></td>";
        }

        html += "<td></td>";
        html += "<td></td>\n";
        html += "</tr>";
    }

    for (var i = 0; i < files.length; i++) {
        isDirectory = files[i]['is_directory'];
        if (isDirectory) {
            name = files[i]['name'];
            modified = files[i]['modified'];
            path = files[i]['path'];
            if(value=="")
                displayname = name + "/";
            else
                displayname = path;
            html += "<tr class='hover'>";
            html += "<td><input type='checkbox' class='check' hidden='false'/></td>";
            html += "<td style='text-align: left;'><a class='file' href='/list" + path + "'>" + displayname + "</a></td>";
            html += "<td>" + dateToString(modified) + "</td>";
            html += "<td>folder</td>";
            if(!files[i]['favorite'])
                html += "<td id='star' style='cursor:default'>★</td>\n";
            else
                html += "<td id='star' style='cursor:default; color:orange;'>★</td>\n";
            html += "</tr>";
        }
    }
    for (var i = 0; i < files.length; i++) {
        isDirectory = files[i]['is_directory'];
        if (!isDirectory) {
            name = files[i]['name'];
            modified = files[i]['modified'];
            path = files[i]['path'];
            isDirectory = files[i]['is_directory'];
            if(value=="")
                displayname = name;
            else
                displayname = path;
            html += "<tr class='hover'>";
            html += "<td><input type='checkbox' class='check' hidden='false'/></td>";
            html += "<td style='text-align: left;'><a class='file' href='/download" + path + "'>" + displayname + "</a></td>";
            html += "<td>" + dateToString(modified) + "</td>";
            html += "<td>file</td>";
            if(!files[i]['favorite'])
                html += "<td id='star' style='cursor:default'>★</td>\n";
            else
                html += "<td id='star' style='cursor:default; color:orange;'>★</td>\n";
            html += "</tr>";
        }

    }


    $("#items").html(html);
}


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
        var display_len = byteTosize(len_file);
        var display_sum = byteTosize(sum);
        $('#size'+file_num).html(display_sum+'/'+display_len);
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
var removed = 0;
function remove_file(items, file_len, file_num) {
        $.ajax({
            method: "POST",
            data: {
                'path': currentDirId + items[file_num]
            },
            url: '/api/delete/',
            success: function (data) {
                removed++;
                $("#removed"+file_num).html("deleted");
                if(removed == file_len)
                    location.reload();
            },
            error: function (data) {
                alert("An error occured, please try again later")
            }
        });


}

var downloaded = 0;
function download_file(items, file_len, file_num) {
        $.ajax({
            method: "GET",
            data: {
                'path': currentDirId + items[file_num]
            },
            url: '/api/download/',
            success: function (data) {
                download++;
                $("#downloaded"+file_num).html("downloaded");
                if(downloaded == file_len)
                    location.reload();
            },
            error: function (data) {
                alert("An error occured, please try again later")
            }
        });
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

$(document).on('change', '#uploadInput', function(){

    var files = $("#uploadInput")[0].files;
    var html="";
    for(var i=0;i<files.length;i++) {
        var size = files[i].size;
        var display_size = byteTosize(size);
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+files[i].name+"</td><td><progress max=\"100\" value=\"0\" id=\"uploadProgress"+i+"\"></progress></td><td style='text-align: left;'><span id='size"+i+"'>0/"+display_size+"</span></td></tr>";
    }
    $("#uploadeditem").html(html);
});

$(document).on('mouseover','.hover', function() {
    $(this).find(".check").attr("hidden",false);
})

$(document).on('mouseout','.hover', function() {
    var checked =  $(this).find(".check").prop('checked');
    if(!checked)
        $(this).find(".check").attr("hidden",true);
})

$(document).on('click', '#star', function () {
    var name = $(this).parent().find(".file").html()
    var result;
    $.ajax({
        method: "POST",
        data: {
            'path': currentDirId + name
        },
        url: '/api/favorite/',
        success: function (data) {
            result = data;
        },
        error: function (data) {
            alert("An error occured, please try again later")
        },
        async: false
    });
    if (result['favorite']) {
        $(this).css('color', 'orange');
        $(this).css('cursor', 'default');
    } else {
        $(this).css('color', 'black');
        $(this).css('cursor', 'default');
    }
});

$(document).on('click', '#stars', function () {
    $.ajax({
        method: "GET",
        url: '/api/listfavorite/',
        success: function (data) {
            isfavorite = true;
            load_files("",data['items']);
        },
        error: function (data) {
            alert("An error occured, please try again later")
        },
        async: false
    });
});

$(document).on('change','.check',function() {

    var filename = $(this).closest('.hover').find('.file').html();
    var checked = $(this).prop('checked');  // checked 상태 (true, false)

    if(checked)
    {
        checked_items.push(filename);
        $(".delete").attr("hidden",false);
        $(".download").attr("hidden",false);
        $(this).attr("hidden",false);
    }
    else
    {
        $(this).attr("hidden",true)
        var index = checked_items.indexOf(filename);
        if(index > -1)
            checked_items.splice(index, 1);
        if(checked_items.length==0){
            $(".delete").attr("hidden",true);
            $(".download").attr("hidden",true);
        }
    }
});


$(document).on('click','#allCheck',function() {

    var checked = $(this).prop('checked');  // checked 상태 (true, false)

    if(checked)
        $("input[type=checkbox]").prop("checked",true).change();
    else
        $("input[type=checkbox]").prop("checked",false).change();
});

$(document).on('click','#removeItem', function() {
    $('#deleteModal').modal();
    var html="";
    for(var i=0;i<checked_items.length;i++) {
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+checked_items[i]+"</td><td style='text-align: left;'><span id='removed"+i+"'></span></td></tr>";
    }
    $('#deleteModal').find("#deleteditem").html(html);

});

$(document).on('click','#deleteBtn', function() {
    var path;
    var items = checked_items;
    removed = 0;
    for(var i = 0; i<items.length;i++) {
        remove_file(items, items.length, i);
    }
});

$(document).on('click','#downloadItem', function() {
    $('#downloadModal').modal();
    var html="";
    for(var i=0;i<checked_items.length;i++) {
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+checked_items[i]+"</td><td style='text-align: left;'><span id='downloaded"+i+"'></span></td></tr>";
    }
    $('#downloadModal').find("#uploadeditem").html(html);

});

$(document).on('click','#downloadBtn', function() {
    var path;
    var items = checked_items;
    downloaded = 0;
    for(var i = 0; i<items.length;i++) {
        download_file(items, items.length, i);
    }
});

$(document).on('input','#search', async function() {
    if ($("#search").val() != "")
    {
        $.ajax({
            method: "GET",
            data: {
                'name': $("#search").val()
            },
            url: '/api/search'+currentDirId,
            success: function (data) {
                 load_files($("#search").val(), data['items'])
            },
            error: function (data) {
                alert("An error occured, please try again later")
            }
        });
    } else {
        list_files();
    }

})

