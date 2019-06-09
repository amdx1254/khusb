var currentDirId;
var urls;
var uploadid;
var item = {'Parts': []};
var finished = 0;
var uploaded_size = [];
var parentDirId;
var isfavorite = false;
var view_share = false;
var view_recent = false;
var available_size;
var used_size
var uploadaborted = false;



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


function printsize() {
    var kb = 1024;
    var mb = 1048576;
    var gb = 1073741824;
    var us = used_size;
    var as = available_size + used_size;
    $(".over_rocket").css("clip","rect(calc(("+available_size+" - " + used_size + ") / " + available_size + " * 137.5 * 1px) 137.5px 137.5px 0px)")
    if (us / gb >= 1) {
        $(".size").html((us / gb).toFixed(2) + " GB/ " + (as / gb).toFixed(2) + " GB");
    } else if (us / mb >= 1) {
        $(".size").html((us / mb).toFixed(2) + " MB/ " + (as / gb).toFixed(2) + " GB");
    } else if (us / kb >= 1) {
        $(".size").html((us / kb).toFixed(2) + " KB/ " + (as / gb).toFixed(2) + " GB");
    } else {
        $(".size").html(us + " B/ " + as / gb + " GB");
    }
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

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

function list_files(recently) {
    var url = '/api/list'+currentDirId;
    if(recently != null){
        url = "/api/list?recently="+recently;
    }
    $.ajax({
            method: "GET",
            url: url,
            success: function (data) {
                if(recently == null)
                {
                    parentDirId = data['parent'];
                    available_size = data['available_size'];
                    used_size = data['used_size'];
                    load_files('', data['items']);
                    printsize();

                }
                else
                    load_files(recently, data['items']);
            },
            error: function (data) {
                showSnackBar("An error occured, please try again later")
            }
    });
}

function list_share() {
    var id = getParameterByName('id');
    var loc = '/api/listshare/';
    if(id != null)
        loc = loc+"?id="+id;
    $.ajax({
        method: "GET",
        url: loc,
        success: function (data) {
            parentDirId = data['parent'];
            load_files("",data['items']);
            available_size = data['available_size'];
            used_size = data['used_size'];

            printsize();
        },
        error: function (data) {
            showSnackBar("An error occured, please try again later")
        },
        async: false
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
    var displayname
    var path;
    var isDirectory;
    var file_id;
    if (currentDirId != "/" || isfavorite || view_share || view_recent) {
        html += "<tr class='hover'>";
        html += "<td></td>";
        var id = getParameterByName('id');
        if(isfavorite){
            html += "<td style='text-align: left;'><a class='file' href='/list'>..</a></td>";
        } else if(view_share)
        {
            if(parentDirId != '' && id != null)
                html += "<td style='text-align: left;'><a class='file' href='/listshare/?id=" + parentDirId + "'>..</a></td>";
            else if(parentDirId == '' && id != null)
                html += "<td style='text-align: left;'><a class='file' href='/listshare/'>..</a></td>";
            else
                html += "<td style='text-align: left;'><a class='file' href='/list'>..</a></td>";
        }
        else {
            html += "<td style='text-align: left;'><a class='file' href='/list" + parentDirId + "'>..</a></td>";
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
            file_id = files[i]['id'];
            if(value=="")
                displayname = name + "/";
            else
                displayname = path;
            html += "<tr class='hover'>";
            html += "<td><input type='checkbox' class='check' hidden='false'/></td>";
            if(view_share)
                html += "<td style='text-align: left;'><a class='file' href='/listshare?id=" + file_id + "'>" + displayname + "</a></td>";
            else
                html += "<td style='text-align: left;'><a class='file' href='/list" + path + "'>" + displayname + "</a></td>";
            html += "<td>" + dateToString(modified) + "</td>";
            html += "<td>folder</td>";
            if(!view_share){
                if(!files[i]['favorite'])
                    html += "<td id='star' style='cursor:default'>★</td>\n";
                else
                    html += "<td id='star' style='cursor:default; color:orange;'>★</td>\n";
            } else {
                html += "<td>"+ files[i]['owner'] + "</td>\n";
            }

            html += "<td id='path' hidden>" + files[i]['path'] + "</td>";
            html += "</tr>";
        }
    }
    for (var i = 0; i < files.length; i++) {
        isDirectory = files[i]['is_directory'];
        if (!isDirectory) {
            name = files[i]['name'];
            modified = files[i]['modified'];
            path = files[i]['path'];
            file_id = files[i]['id'];
            isDirectory = files[i]['is_directory'];
            if(value=="")
                displayname = name;
            else
                displayname = path;
            html += "<tr class='hover'>";
            html += "<td><input type='checkbox' class='check' hidden='false'/></td>";
            if(view_share)
                html += "<td style='text-align: left;'><a class='file' href='/download/share/?id=" + file_id + "'>" + displayname + "</a></td>";
            else
                html += "<td style='text-align: left;'><a class='file' href='/download" + path + "'>" + displayname + "</a></td>";

            html += "<td>" + dateToString(modified) + "</td>";
            html += "<td>file</td>";
            if(!view_share){
                if(!files[i]['favorite'])
                    html += "<td id='star' style='cursor:default'>★</td>\n";
                else
                    html += "<td id='star' style='cursor:default; color:orange;'>★</td>\n";
            } else {
                html += "<td>"+ files[i]['owner'] + "</td>\n";
            }
            html += "<td id='path' hidden>" + files[i]['path'] + "</td>";
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
    uploadaborted = false;
    if(file_len > file_num && !uploadaborted){

        var unloadHandler = function () {
            uploadaborted = true;
            $.post('/api/upload_abort/', {
                        'name': $("#uploadInput")[0].files[file_num].name,
                        'path': currentDirId,
                        'uploadid': uploadid
            });
            closeSnackBar();
            $("#uploadeditem").html("");
            $("#uploadInput").val("");
            showSnackBar("업로드 중단");
            $("#uploadBtn").show();
            $("#abortBtn").attr("hidden",'');

        }

        window.onunload = function() {
            unloadHandler();
            alert('Bye.');
        }

        $(document).on('click','#abortBtn', function() {
           unloadHandler();
        });

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
                uploadid = data['uploadid'];
                if(file_num==0){
                    $("#uploadModal").modal('toggle');
                    $("#uploadBtn").hide();
                    $("#abortBtn").removeAttr("hidden");
                }
            },
            error: function (data) {
                showSnackBar("An error occured, please try again later")
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
                upload_file(urls[url], filedata, chunk_num, len_url, len_file, file_num, file_len);
                processed = processed + slice_length;
                chunk_num++;
            }
        });
    } else {
        $("#uploadBtn").show();
        $("#abortBtn").attr("hidden",'');
        $(document).on('click','#abortBtn', function() {

        });
        closeSnackBar();
        showSnackBar("업로드 완료");
        $("#uploadeditem").html("");
        $("#uploadInput").val("");
    }
}

function upload_file(url, filedata, chunk_id, len_url, len_file, file_num, file_len) {
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
        showPermanantSnackBar((file_num+1) + "/" + file_len + "  " + $("#uploadInput")[0].files[file_num].name + "   " + "<progress max=\"100\" value=\"0\" id=\"snackprogress\"></progress>" + "   " + display_sum + "/" + display_len);
        $('#snackprogress').val(per);
        if(uploadaborted){
            xhr.abort();
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
                window.onbeforeunload = null;

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
                        list_files();
                        make_upload($("#uploadInput")[0].files.length, file_num+1);
                    },
                    error: function (data) {
                        showSnackBar("An error occured, please try again later")
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
                'path': items[file_num]
            },
            url: '/api/delete/',
            success: function (data) {
                removed++;
                showSnackBar("삭제중...");
                $("#removed"+file_num).html("deleted");
                list_files();
            },
            error: function (data) {
                showSnackBar("An error occured, please try again later")
            }
        });
}

var shared = 0;
function share_file(items, file_len, file_num, email) {
        $.ajax({
            method: "POST",
            data: {
                'path': items[file_num],
                'email': email
            },
            url: '/api/share/',
            success: function (data) {
                shared++;
                if(shared == file_len) {
                    $("#shareModal").modal("toggle");
                    showSnackBar(file_len + "개의 파일이 공유되었습니다");
                }
            },
            error: function (data) {
                showSnackBar("존재하지 않는 Email입니다");
            }
        });
}

var downloaded = 0;
function download_file(items, file_len, file_num) {
        var checked_items = findCheckedItems();
        $.ajax({
            method: "GET",
            data: {
                'path': currentDirId + items[file_num]
            },
            url: '/api/download/'+checked_items[file_num],
            success: function (data) {
                window.location = 'http://127.0.0.1:8000/download/' + checked_items[downloaded];
                downloaded++;
                $("#downloaded"+file_num).html("downloaded");
                if(downloaded == file_len)
                    location.reload();
            },
            error: function (data) {
                showSnackBar("An error occured, please try again later")
            }
        });
}

function showSnackBar(text) {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar")
    $("#snackbar").html(text);
    // Add the "show" class to DIV
    x.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function(){ x.className = x.className.replace("show", "hide"); }, 3000);
}

function showPermanantSnackBar(text) {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar_download");
    $("#snackbar_content").html(text);
    // Add the "show" class to DIV
    x.className = "show";
}

function closeSnackBar() {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar_download");

    x.className = x.className.replace("show", "hide");
}

function findCheckedItems() {
    var checked_items = [];
    $('input[type="checkbox"]:checked').each(function() {
        var item = $(this).closest(".hover").find("#path").html();
        if(item != null)
           checked_items.push(item);
    });
    return checked_items;
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
            $("#createDirectoryModal").modal("toggle");
            showSnackBar("폴더 생성완료");
            list_files();
        },
        error: function (data) {
            showSnackBar("An error occured, please try again later")
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
            showSnackBar("An error occured, please try again later")
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
    if(view_share)
        window.history.pushState("", "", '/list/');

    $.ajax({
        method: "GET",
        url: '/api/listfavorite/',
        success: function (data) {
            isfavorite = true;
            load_files("",data['items']);
        },
        error: function (data) {
            showSnackBar("An error occured, please try again later")
        },
        async: false
    });
});

$(document).on('change','.check',function() {

    var filename = $(this).closest('.hover').find('#path').html();
    var checked = $(this).prop('checked');  // checked 상태 (true, false)
    var checked_items = findCheckedItems();
    if(checked)
    {
        if(!view_share){
            $(".delete").attr("hidden",false);
            $(".download").attr("hidden",false);
            $(".share").attr("hidden",false);
        }

        $(this).attr("hidden",false);
    }
    else
    {
        $(this).attr("hidden",true)
        if(checked_items.length==0){
            if(!view_share){
                $(".delete").attr("hidden",true);
                $(".download").attr("hidden",true);
                $(".share").attr("hidden",true);
            }
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
    var checked_items = findCheckedItems();
    var html="";
    for(var i=0;i<checked_items.length;i++) {
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+checked_items[i]+"</td><td style='text-align: left;'><span id='removed"+i+"'></span></td></tr>";
    }
    $('#deleteModal').find("#deleteditem").html(html);

});

$(document).on('click','#deleteBtn', function() {
    var path;
    var items = findCheckedItems();
    removed = 0;
    $("#deleteModal").modal('toggle');
    for(var i = 0; i<items.length;i++) {
        remove_file(items, items.length, i);
    }
});

$(document).on('click','#downloadItem', function() {
    $('#downloadModal').modal();
    var checked_items = findCheckedItems();
    var html="";
    for(var i=0;i<checked_items.length;i++) {
        html += "<tr class=\"hover\"><td style=\"text-align: left;\">"+checked_items[i]+"</td><td style='text-align: left;'><span id='downloaded"+i+"'></span></td></tr>";
    }
    $('#downloadModal').find("#downloaditem").html(html);

});

$(document).on('click','#downloadBtn', function() {
    var path;
    var items = findCheckedItems();
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
                showSnackBar("An error occured, please try again later")
            }
        });
    } else {
        list_files();
    }
});

$(document).on('click','#shareBtn', function() {
    var path;
    var items = findCheckedItems();
    shared = 0;
    for(var i = 0; i<items.length;i++) {
        share_file(items, items.length, i, $("#emailInput").val());
    }
});

$(document).on('click','#recent', function() {
    if(view_share)
        window.history.pushState("", "", '/list/');
    view_recent = true;
    list_files("modified");
});

$(document).on('click','#added', function() {
    if(view_share)
        window.history.pushState("", "", '/list/');
    view_recent = true;
    list_files("created");
});

$(document).on('click','#snackbar_content', function() {
    $('#uploadModal').modal('toggle');
});

$(document).on('hide.bs.modal', '#shareModal', function() {
    $("#shareresult").html("");
});

$(document).on('hide.bs.modal', '#uploadModal', function() {
});

$(document).on('hide.bs.modal', '#createDirectoryModal', function() {
    $("#directoryName").val("");
});

$(document).on('hide.bs.modal', '#deleteModal', function() {
    $("#deleteditem").html("");
});

