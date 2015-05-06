 var csrftoken = $.cookie('csrftoken');
 var selectedValue = "";

 function setCountry(code){
        if(code || code==''){
            var text = jQuery('a[cunt_code="'+code+'"]').html();
            $(".dropdown dt a span").html(text);
        }
    }

function sendPost(sports_type){
    var senddata = {'selectedType': sports_type};
    //console.log(senddata);
            //console.log(data);
            //$.post(URL, {sportsType: data, csrfmiddlewaretoken:'{{ csrf_token }}'}, function(response){
              //  if(response === 'Success!!!'){ alert('Yay!');}
                //else{ alert('Error! :(');}
            //});
    $.ajax(URL, {
        type : 'POST',
        data : senddata,
        traditional: true,
        success: function (data, textStatus, jQxhr) {
            console.log(textStatus);
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
           
}

    $(document).ready(function() {
        /*$("#sports-select").change(function(){
            var selectedValue = $("#sports-select a:selected").val();
            console.log(selectedValue)
            $.post("",
            {name:"Donald Duck",
            city:"Duckburg",
            csrfmiddlewaretoken:'{{ csrf_token }}'
            });
        });*/

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $(".dropdown img.flag").addClass("flagvisibility");

        $(".dropdown dt a").click(function() {
            $(".dropdown dd ul").toggle();
        });

        $(".dropdown dd ul li a").click(function() {
            //console.log($(".dropdown dd ul li").val();
            //alert($(this).text());
            //sendPost($(this).text());
            var elem = document.getElementById("selectedValue");
            elem.value = $(this).text();
            var text = $(this).html();
            $(".dropdown dt a span").html(text);
            $(".dropdown dd ul").hide();
            $("#result").html("Selected value is: " + getSelectedValue("sports-select"));
        });

        function getSelectedValue(id) {
            //console.log(id,$("#" + id).find("dt a span.value").html())
            return $("#" + id).find("dt a span.value").html();
        }

        $(document).bind('click', function(e) {
            var $clicked = $(e.target);
            if (! $clicked.parents().hasClass("dropdown"))
                $(".dropdown dd ul").hide();
        });


        $("#flagSwitcher").click(function() {
            $(".dropdown img.flag").toggleClass("flagvisibility");
        });
    });