

//func

var run_bark_tts = function (text, speaker, callback) {
  var url = "/test_tts/bark_tts";

  $.ajax({
    type: "POST",
    url: url,
    data: {
      text: text,
      speaker: speaker,
    },
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      typeof callback == 'function' && callback(js)

    },
    error: function (resp, status) {
      var js = JSON.parse(resp.responseText)
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      alert(js.message);
    }
  })
}


//click event
var when_click_bark_predict_button = function () {

  var bark_run_predict_button = $("#bark_run_predict_button");

  if (bark_run_predict_button.attr("value") === "running") {
    alert("please wait this running finish.")
    return null;
  }

  //var
  var text = bark_run_predict_button.parent().siblings().eq(1).find("input:eq(0)").val();
  var speaker = bark_run_predict_button.parent().siblings().eq(2).find("select:eq(0)").val();

  bark_run_predict_button.attr("value", "running")

  run_bark_tts(text, speaker, function (js) {
    //set value
    $("#bark_tts_audio").attr("src", js.result)
    $("#bark_tts_audio_box").load()
    bark_run_predict_button.attr("value", "predict")

  })
}


//reset messages
var reset_bark_speakers = function () {
  var url = "/test_tts/bark_speakers";

  $.ajax({
    type: "GET",
    url: url,
    data: {},
    success: function(js, status){
      console.log("url: " + url + ", status: " + status + ", js: " + JSON.stringify(js));
      if (js.status_code === 60200) {

        var element_bark_speaker_select = $("#bark_speaker_select");
        element_bark_speaker_select.empty();

        for (var i=0; i<js.result.length; i++)
        {
          element_bark_speaker_select.append(`
            <option>${js.result[i]}</option>
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


$(document).ready(function(){
  reset_bark_speakers();

  $("#bark_run_predict_button").click(function () {
    when_click_bark_predict_button();
  });
})

