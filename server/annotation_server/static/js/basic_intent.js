
//global var
var download_number = 20
var last_group = null

//func
var predict = function (language, text, callback) {
  var url = "basic_intent/predict_by_language";

  $.ajax({
    async: true,
    type: "POST",
    url: url,
    data: {
      language: language,
      text: text,
    },
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      typeof callback == 'function' && callback(js)
    }
  });
}

var get_choice_of_label = function (async = true, callback) {
  var url = "basic_intent/get_choice_of_label";

  var language = $("#select_language").val();

  $.ajax({
    async: async,
    type: "POST",
    url: url,
    data: {
      language: language,
    },
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      typeof callback == 'function' && callback(js)
    }
  });
}

var set_text_basic_intent_table_by_js = function (js) {
  if (js.status_code === 60200) {
    var element_text_basic_intent_table = $("#text_basic_intent_table");
    element_text_basic_intent_table.empty();

    // <td><input class="text_input" value="${js.result[i]['text']}"></td>
    // https://www.runoob.com/try/try.php?filename=trycss_table_fancy
    element_text_basic_intent_table.append(`
          <thead>
            <tr>
            <td>text</td>
            <td>label</td>
            <td>predict</td>
            <td>prob</td>
            <td>predict</td>
            </tr>
          </thead>
        `)
    for (var i=0; i<js.result.length; i++)
    {
      if (i % 2 === 0) {
        element_text_basic_intent_table.append(`
              <tr class="alt">
                <td><input class="text_input" value="${js.result[i]['text']}"></td>
                <td><select class="label_input"></select></td>
                <td></td><td></td>
                <td><input class="run_predict_button" type="button" value="predict"></td>
              </tr>
            `)
      } else {
        element_text_basic_intent_table.append(`
              <tr>
                <td><input class="text_input" value="${js.result[i]['text']}"></td>
                <td><select class="label_input"></select></td>
                <td></td><td></td>
                <td><input class="run_predict_button" type="button" value="predict"></td>
              </tr>
            `)
      }
    }

    //label field options
    var label_input_field = $(".label_input");

    get_choice_of_label(false, function (js_l) {
      label_input_field.each(function (idx) {
        for (var j=0; j<js_l.result.length; j++) {
          if (js.result[idx]['label'] === js_l.result[j]) {
            label_input_field.eq(idx).append("<option selected>" + js_l.result[j] + "</option>")
          } else {
            label_input_field.eq(idx).append("<option>" + js_l.result[j] + "</option>")
          }
        }
      })
    });

    // https://github.com/zhaobao1830/jquery-editable-select
    // https://www.cnblogs.com/zhaobao1830/p/6337382.html
    label_input_field.editableSelect({
      filter: true,
      effects: 'fade',
      trigger: 'focus',
    })

    var run_predict_buttons = $(".run_predict_button");

    //click event
    run_predict_buttons.click(function(){
      when_click_run_predict_button($(this));
    });

    //predict
    for (var k=0; k<js.result.length; k++) {
      // console.log(run_predict_buttons.eq(j))
      when_click_run_predict_button(run_predict_buttons.eq(k));
    }

  } else {
    alert(js.message);
  }

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
    reset_annotator_workload();
    reset_labels_count();
    reset_model_info();
    download_n(username, language, download_number);
  }
}

var when_click_submit = function () {
  //
  var submit = $("#submit_button");
  var text_basic_intent_table = $("#text_basic_intent_table");

  //var
  var username = $("#username").val();
  var language = $("#select_language").val();

  if (username === "") {
    alert("请输入用户名!")
    return null;
  } else {
    annotate_n(username, language, function () {
      download_n(username, language, download_number);
    });

  }
}

var when_click_last_submit = function () {
  set_text_basic_intent_table_by_js(last_group);
}

var when_click_predict_button = function (element) {
  //fill 'predict' label to 'label'.
  element.parent().siblings().eq(1).find("input:eq(0)").val(element.val());

}

var when_click_run_predict_button = function (element) {

  //data
  var language = $("#select_language").val();
  var text = element.parent().siblings().eq(0).find("input:eq(0)").val();

  //predict
  predict(language, text, function (js) {

    //set value
    element.parent().siblings().eq(2).html(`<input class="predict_button" type="button" value="${js.result.label}">`);
    element.parent().siblings().eq(3).text(js.result.prob);

    //click event
    $(".predict_button").click(function(){
      when_click_predict_button($(this));
    });
  });

}

var on_change_select_language = function () {
  reset_choice_of_recommend_mode();
}


//reset messages
var reset_choice_of_language = function() {
  var url = "basic_intent/get_choice_of_language";

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
  var url = "basic_intent/get_choice_of_recommend_mode";

  var language = $("#select_language").val();

  $.ajax({
    async: false,
    type: "POST",
    url: url,
    data: {
      language: language,
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

var reset_annotator_workload = function () {
  var url = "basic_intent/get_annotator_workload";

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
  var url = "basic_intent/get_labels_count";

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
          labels_count_table.append(`
            <tr>
            <td>${js.result[i][0]}</td>
            <td>${js.result[i][1]}</td>
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
}

var reset_model_info = function () {
  var url = "basic_intent/get_model_info";

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
          model_info_table.append(`
            <tr>
            <td>${js.result[i][0]}</td>
            <td>${js.result[i][1]}</td>
            <td>${js.result[i][2]}</td>
            </tr>
          `)
        }
      } else {
        alert(js.message);
      }
    }
  })
}


//work
var download_n = function (username, language, n) {
  var url = "basic_intent/download_n";

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
      recommend_mode: recommend_mode,
      n: n
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      set_text_basic_intent_table_by_js(js);
    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })
}


var annotate_n = function (username, language, callback) {
  var url = "basic_intent/annotate_n";

  var element_text_basic_intent_table = $("#text_basic_intent_table");

  var annotates = []

  //annotates
  element_text_basic_intent_table.children("tr").each(function () {
    annotates.push({
      text: $(this).find("td").eq(0).find("input:eq(0)").val(),
      label: $(this).find("td").eq(1).find("input:eq(0)").val(),
    });

  });

  $.ajax({
    type: "POST",
    url: url,
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify({
      username: username,
      language: language,
      annotates: annotates,
    }),
    // traditional: true,
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);
      last_group = js;
      typeof callback == 'function' && callback(js)

    }
  });
}


$(document).ready(function(){
  reset_choice_of_language();
  reset_choice_of_recommend_mode();

  $("#select_language").change(function(){
    on_change_select_language();
  });

  $("#search").click(function(){
    when_click_search();
  });

  $("#submit_button").click(function(){
    when_click_submit();
  });

  $("#last_submit_button").click(function(){
    when_click_last_submit();
  });
})
