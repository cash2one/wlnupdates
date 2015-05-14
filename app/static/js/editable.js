/*!
 * Editable.
 * Part of wlnupdates.com
 */

function singleEditable(spans, contentDiv, containerId)
{
	var content = spans.first().html()
	content = content.replace(/(<br>)/g, "\n");
	content = content.replace(/(<p>)/g, "");
	content = content.replace(/(<\/p>)/g, "\n\n");
	if (content == 'N/A') content = ""
	var contentArr = [
		"<textarea name='input-" + containerId + "' rows='2' id='singleitem'>"+content.trim()+"\n</textarea>",
		"<script>$('textarea').autogrow({onInitialize:true});</script>"
	]
	contentDiv.html(contentArr.join("\n"))
}

function dropboxEditable(spans, contentDiv, containerId)
{
	var text = contentDiv.find('.dropitem-text').first();
	var edit = contentDiv.find('.dropitem-box').first();

	console.log(spans)
	console.log(text)
	console.log(edit)
	text.hide();
	edit.show();
	// contentDiv.html()
}

function multiEditable(spans, contentDiv, containerId)
{
	var content = ""
	spans.each(function(){
		content += $(this).find("a").first().text() + "\n"
	})
	// console.log(content)
	if (content == 'N/A') content = ""
	var contentArr = [
		"<p>One entry per line, please.</p>",
		"<textarea name='input-" + containerId + "' rows='2' id='multiitem'>"+content+"</textarea>",
		"<script>$('textarea').autogrow({onInitialize:true});</script>"
	]
	contentDiv.html(contentArr.join("\n"))
}

function listEditable(spans, contentDiv, containerId)
{
	var content = ""
	spans.each(function(){
		content += $(this).text() + "\n"
	})
	// console.log(content)
	if (content == 'N/A') content = ""
	var contentArr = [
		"<p>One entry per line, please.</p>",
		"<textarea name='input-" + containerId + "' rows='2' id='multiitem'>"+content+"</textarea>",
		"<script>$('textarea').autogrow({onInitialize:true});</script>"
	]
	contentDiv.html(contentArr.join("\n"))
}



function edit(containerId){

	var container = $('#'+containerId).first();
	var contentDiv = container.find(".rowContents");
	var spans = contentDiv.find("span");
	if (spans.length == 0)
	{
		console.log("No items? Wat? Error!");
		return;
	}
	var spantype = container.attr('class')

	if (spantype.indexOf("singleitem") >= 0)
	{
		singleEditable(spans, contentDiv, containerId);
	}
	else if (spantype.indexOf("dropitem") >= 0)
	{
		dropboxEditable(spans, contentDiv, containerId);
	}
	else if (spantype.indexOf("multiitem") >= 0)
	{
		multiEditable(spans, contentDiv, containerId);
	}
	else if (spantype.indexOf("multilist") >= 0)
	{
		listEditable(spans, contentDiv, containerId);
	}
	else
	{
		console.log("Unknown span type: '"+spantype+"'! Wat?")
		return;
	}

	var editLink = container.find("#editlink").first();
	editLink.attr('onclick', "saveEdits('" + containerId + "'); return false;");
	editLink.html('[save]');
	// console.log(editLink);
	// console.log(containerId);

}

function toggle_watch(containerId){

	var container = $('#watch-link').first();
	console.log("Contents: ", container.text())

	var watch = false;
	if (container.text().indexOf('No') > -1)
		watch = true;

	container.html("[Working]")


	var data = [];
	var mangaId = $('meta[name=manga-id]').attr('content')

	var params = {
		"mode"      : "set-watch",
		"mangaId"   : mangaId,
		"watch"     : watch,
		"list"      : "watched"
	}

	$.ajax({
		url : "/api",
		success : watchCalback,
		data: JSON.stringify(params),
		method: "POST",
		dataType: 'json',
		contentType: "application/json;",
	});
}


function watchCalback(result)
{
	console.log(result)
	console.log("Watch callback!")
	if (!result.hasOwnProperty("error"))
	{
		console.log("No error result?")
	}
	if (!result.hasOwnProperty("watch_str"))
	{
		console.log("No watch_str result?")
	}
	if (result['error'])
	{
		alert("Error on update!\n\n"+result["message"])
	}
	else
	{
		console.log("Message:", result['message'])
		console.log("watch_str:", result['watch_str'])
		var container = $('#watch-link').first();
		container.text(result['watch_str'])
	}
}


function saveEdits(containerId)
{
	// var containers = $('.info-item');

	var data = [];
	$('.info-item').each(function()
	{
		// Iterate over the info-item wells, extract the textarea if it's present.
		var member = $(this);
		var textarea = member.find("textarea").first();
		var combobox = member.find("select").first();

		if (textarea.length > 0)
		{
			var entryKey  = member.find(".row").first().attr('id');
			var entryType = member.find("textarea").first().attr('id');
			var entryArea = member.find("textarea").first().val();

			var entry = {};
			entry['key'] = entryKey;
			entry['type'] = entryType;
			entry['value'] = entryArea;

			data.push(entry);

		}
		else if (combobox.length > 0 && combobox.is(":visible"))
		{

			var entryKey  = member.find(".row").first().attr('id');
			var entryType = 'combobox';
			var entryArea = combobox.val();

			var entry = {};
			entry['key'] = entryKey;
			entry['type'] = entryType;
			entry['value'] = entryArea;

			data.push(entry);
		}

	}
	)

	console.log("Data:", data)


	var mangaId = $('meta[name=manga-id]').attr('content')

	var container = $('#'+containerId).first();
	var editLink = container.find("#editlink").first();
	editLink.attr('onclick', "return false;");
	editLink.html('[saving]');


	var entryType = container.find("textarea").attr('id');
	var entryArea = container.find("textarea").first().val();

	var params = {
		"mode"      : "manga-update",
		"mangaId"   : mangaId,
		"entries"   : data,
	}


	$.ajax({
		url : "/api",
		success : saveCallback(containerId),
		data: JSON.stringify(params),
		method: "POST",
		dataType: 'json',
		contentType: "application/json;",
	});

}


function saveCallback(containerId)
{
	return function(result)
	{
		console.log("Save callback!")
		if (!result.hasOwnProperty("error"))
		{
			console.log("No error result?")
		}
		if (result['error'])
		{
			alert("Error on update!\n\n"+result["message"])
		}
		else
		{
			location.reload();
		}
		console.log(result)




	}
}

var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken)
		}
	}
})