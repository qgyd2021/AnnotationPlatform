
//global var
var last_annotation = {
  "audio_filename": "",
  "image_filename": "",
  "audio_display_name": ""
}


//click event
var when_click_search = function () {
  //var
  var username = $("#username").val();
  var language = $("#select_language").val();

  if (username === "") {
    alert("请输入用户名!")
    return null;
  } else {
    reset_choice_of_label();
    reset_annotator_workload();
    reset_labels_count();
    reset_model_info();
    download_one(username, language);

  }
}

var when_click_label_button = function (label) {
  //var
  var language = $("#select_language").val();

  reset_choice_of_label();

  annotate_one(label,res=>{
    var username = $("#username").val()
    if (username === "") {
      alert("请输入用户名!")
      return null;
    } else {
      download_one(username, language);
    }
  });
}

var when_click_play_button = function () {
  $("#voicemail_audio_box").load();
}

var when_click_last_button = function () {
  $("#spectrum_image").attr("src", last_annotation.image_filename);
  $("#voicemail_audio").attr("src", last_annotation.audio_filename);
  $("#audio_display_name").text(last_annotation.audio_display_name);
  $("#voicemail_audio_box").load();
}


//reset messages
var reset_choice_of_language = function(){
  var url = "voicemail/get_choice_of_language";

  $.ajax({
    async: false,
    type: "POST",
    url: url,
    data: {},
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      //var
      var element_select_language = $("#select_language")

      //reset language_choices
      element_select_language.empty();
      for (var i = 0; i < js.result.length; i++) {
        element_select_language.append("<option>" + js.result[i] + "</option>")
      }
    }
  });
}

var reset_choice_of_recommend_mode = function () {
  var url = "voicemail/get_choice_of_recommend_mode";

  //var
  var language = $("#select_language").val();

  $.ajax({
    async: false,
    type: "POST",
    url: url,
    data: {
      language: language
    },
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      //var
      var recommend_mode = $("#recommend_mode");

      //reset recommend modes
      recommend_mode.empty();
      for (var i = 0; i < js.result.length; i++) {
        recommend_mode.append("<option>" + js.result[i] + "</option>")
      }
    }
  });
}

var reset_choice_of_label = function () {
  var url = "voicemail/get_choice_of_label";

  //var
  var language = $("#select_language").val();

  $.ajax({
    type: "POST",
    url: url,
    data: {
      language: language
    },
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      //var
      var available_label_box = $("#available_label_box");

      //reset label buttons
      available_label_box.empty();
      for (var i = 0; i < js.result.length; i++) {
        available_label_box.append(`
            <div class="label_button" id="label_button_${js.result[i]}">
              <div class="label_button_prob" id="label_button_prob_${js.result[i]}"></div>
              <div class="label_button_label">${js.result[i]}</div>
            </div>
        `)
      }

      //bind click
      $(".label_button").click(function () {
        when_click_label_button($(this).children(".label_button_label").text());
      });
    }
  });
}

var reset_annotator_workload = function () {
  var url = "voicemail/get_annotator_workload";

  //var
  var username = $("#username").val();
  var language = $("#select_language").val();

  $.ajax({
    type: "POST",
    url: url,
    data: {
      username: username,
      language: language
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {
        var annotator_workload_table = $("#annotator_workload_table");
        annotator_workload_table.empty();

        for (var i=0; i<js.result.length; i++)
        {
          annotator_workload_table.append(`
            <tr>
            <td>${js.result[i][0]}</td>
            <td>${js.result[i][1]}</td>
            <td>${js.result[i][2]}</td>
            <td>${js.result[i][3]}</td>
            </tr>
          `)
        }
      } else {
        alert(js.message);
      }
    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })

};

var reset_labels_count = function () {
  var url = "voicemail/get_labels_count";

  //var
  var language = $("#select_language").val();

  $.ajax({
    type: "POST",
    url: url,
    data: {
      language: language
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {
        var labels_count_table = $("#labels_count_table");
        labels_count_table.empty();

        for (var i=0; i<js.result.length; i++)
        {
          labels_count_table.append(
            "<tr>" +
            "<td>" + js.result[i][0] + "</td>" +
            "<td>" + js.result[i][1] + "</td>" +
            "</tr>"
          )
        }
      } else {
        alert(js.message);
      }
    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })
}

var reset_model_info = function () {
  var url = "voicemail/get_model_info";

  //var
  var language = $("#select_language").val();

  $.ajax({
    type: "POST",
    url: url,
    data: {
      language: language
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {
        var model_info_table = $("#model_info_table");
        model_info_table.empty();

        for (var i=0; i<js.result.length; i++)
        {
          model_info_table.append(
            "<tr>" +
            "<td>" + js.result[i][0] + "</td>" +
            "<td>" + js.result[i][1] + "</td>" +
            "</tr>"
          )
        }
      } else {
        alert(js.message);
      }
    }
  })
}


//work
var download_one = function (username, language) {
  var url = "voicemail/download_one";

  var element_annotate_mode = $("#annotate_mode")
  var element_recommend_mode = $("#recommend_mode")

  var annotate_mode = element_annotate_mode.val()
  var recommend_mode = element_recommend_mode.val()

  $.ajax({
    type: "POST",
    url: url,
    data: {
      username: username,
      language: language,
      annotate_mode: annotate_mode,
      recommend_mode: recommend_mode
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {
        $("#spectrum_image").attr("src", js.result.image_filename)
        $("#voicemail_audio").attr("src", js.result.audio_filename)
        $("#audio_display_name").text(js.result.audio_display_name)
        $("#voicemail_audio_box").load()

        //prob
        for (var i=0; i<js.result.predict_info.length; i++)
        {
          var label_button_prob = $(`#label_button_prob_${js.result.predict_info[i].label}`);
          label_button_prob.text(js.result.predict_info[i].prob)
        }

      } else {
        alert(js.message);
      }
    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })
}

var annotate_one = function (label, callback) {
  var url = "voicemail/annotate_one";
  var element_voicemail_audio = $("#voicemail_audio")
  var element_username = $("#username")
  var element_select_language = $("#select_language")

  var audio_filename = element_voicemail_audio.attr("src")
  var username = element_username.val()
  var language = element_select_language.val()

  $.ajax({
    type: "POST",
    url: url,
    data: {
      username: username,
      audio_filename: audio_filename,
      label:label,
      language: language
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {
        last_annotation = {
          "audio_filename": js.result,
          "image_filename": $("#spectrum_image").attr("src"),
          "audio_display_name": $("#audio_display_name").text(),
        }
      } else {
        alert(js.message);
      }
      typeof callback == 'function' && callback()

    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })
}


$(document).ready(function(){
  reset_choice_of_language();
  reset_choice_of_recommend_mode();

  $("#play_button").click(function(){
    when_click_play_button();
  });

  $("#last_button").click(function(){
    when_click_last_button();
  });

  $("#search").click(function(){
    when_click_search();
  });

})
